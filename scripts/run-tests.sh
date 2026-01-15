set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  Data Archival Service - Test Runner${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

COMMAND=${1:-all}
shift 2>/dev/null || true

run_all_tests() {
    echo -e "${YELLOW}Running all tests...${NC}"
    docker-compose -f docker-compose.test.yml build tests
    docker-compose -f docker-compose.test.yml run --rm tests
}

run_unit_tests() {
    echo -e "${YELLOW}Running unit tests only...${NC}"
    docker-compose -f docker-compose.test.yml build tests
    docker-compose -f docker-compose.test.yml run --rm tests pytest -v -m "not integration" --tb=short
}

run_integration_tests() {
    echo -e "${YELLOW}Running integration tests with database...${NC}"
    docker-compose -f docker-compose.test.yml build tests-with-db
    docker-compose -f docker-compose.test.yml up -d test-db
    echo "Waiting for database to be ready..."
    sleep 10
    docker-compose -f docker-compose.test.yml run --rm tests-with-db
    docker-compose -f docker-compose.test.yml down
}

run_with_coverage() {
    echo -e "${YELLOW}Running tests with coverage report...${NC}"
    docker-compose -f docker-compose.test.yml build tests
    docker-compose -f docker-compose.test.yml run --rm tests pytest -v --cov=orchestrator --cov=worker --cov-report=term-missing --cov-report=html:/app/coverage
    
    echo ""
    echo -e "${GREEN}Coverage report generated at: ./coverage/index.html${NC}"
    
    if command -v open &> /dev/null; then
        echo "Opening coverage report..."
        open ./coverage/index.html 2>/dev/null || true
    fi
}

run_specific_tests() {
    echo -e "${YELLOW}Running specific tests: $@${NC}"
    docker-compose -f docker-compose.test.yml build tests
    docker-compose -f docker-compose.test.yml run --rm tests pytest -v "$@"
}

run_quick_check() {
    echo -e "${YELLOW}Running quick syntax/import check...${NC}"
    docker-compose -f docker-compose.test.yml build tests
    docker-compose -f docker-compose.test.yml run --rm tests python -c "
import orchestrator.security.jwt_service
import orchestrator.security.encryption_service
import orchestrator.security.auth
import orchestrator.model.models
print('✓ All modules import successfully')
"
}

cleanup() {
    echo -e "${YELLOW}Cleaning up test containers...${NC}"
    docker-compose -f docker-compose.test.yml down -v --remove-orphans
    echo -e "${GREEN}Cleanup complete!${NC}"
}

case "$COMMAND" in
    all)
        run_all_tests
        ;;
    unit)
        run_unit_tests
        ;;
    integration)
        run_integration_tests
        ;;
    coverage)
        run_with_coverage
        ;;
    specific)
        run_specific_tests "$@"
        ;;
    quick)
        run_quick_check
        ;;
    clean)
        cleanup
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        echo ""
        echo "Usage: $0 {all|unit|integration|coverage|specific|quick|clean}"
        echo ""
        echo "Commands:"
        echo "  all         - Run all tests (default)"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests with database"
        echo "  coverage    - Run tests with coverage report"
        echo "  specific    - Run specific test file/class/function"
        echo "  quick       - Quick import/syntax check"
        echo "  clean       - Clean up test containers"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Tests completed!${NC}"
echo -e "${GREEN}============================================${NC}"
