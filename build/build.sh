set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root (one level up from build directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Image names and versions
ORCHESTRATOR_IMAGE="das-orchestrator"
WORKER_IMAGE="das-worker"
VERSION="${VERSION:-latest}"

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Data Archival Service - Build Script${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Project Root: $PROJECT_ROOT"
echo "Version: $VERSION"
echo ""

# Function to build an image
build_image() {
    local name=$1
    local dockerfile=$2
    local tag="${name}:${VERSION}"
    
    echo -e "${YELLOW}Building ${name}...${NC}"
    
    docker build \
        -t "$tag" \
        -f "$PROJECT_ROOT/$dockerfile" \
        "$PROJECT_ROOT"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Successfully built ${tag}${NC}"
    else
        echo -e "${RED}✗ Failed to build ${tag}${NC}"
        exit 1
    fi
    echo ""
}

# Parse command line arguments
BUILD_ORCHESTRATOR=false
BUILD_WORKER=false
BUILD_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        orchestrator)
            BUILD_ORCHESTRATOR=true
            shift
            ;;
        worker)
            BUILD_WORKER=true
            shift
            ;;
        all|--all|-a)
            BUILD_ALL=true
            shift
            ;;
        --version|-v)
            VERSION="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [orchestrator|worker|all] [--version VERSION]"
            echo ""
            echo "Arguments:"
            echo "  orchestrator  Build only the orchestrator image"
            echo "  worker        Build only the worker image"
            echo "  all           Build all images (default)"
            echo ""
            echo "Options:"
            echo "  --version, -v VERSION  Set image version tag (default: latest)"
            echo "  --help, -h             Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown argument: $1${NC}"
            exit 1
            ;;
    esac
done

# Default to build all if no specific service specified
if ! $BUILD_ORCHESTRATOR && ! $BUILD_WORKER && ! $BUILD_ALL; then
    BUILD_ALL=true
fi

# Build images
if $BUILD_ALL || $BUILD_ORCHESTRATOR; then
    build_image "$ORCHESTRATOR_IMAGE" "orchestrator/Dockerfile"
fi

if $BUILD_ALL || $BUILD_WORKER; then
    build_image "$WORKER_IMAGE" "worker/Dockerfile"
fi

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}Build Complete!${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo "Available images:"
docker images | grep -E "(das-orchestrator|das-worker)" | head -10

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Start the services: docker-compose up -d"
echo "2. Access the API at: http://localhost:8000"
echo "3. View API docs at: http://localhost:8000/docs"
