import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_config():
    cfg = Mock()
    cfg.config_id = 1
    cfg.job_type = "archival"
    cfg.table_name = "orders"
    cfg.date_column = "created_at"
    cfg.archival_days = 180
    cfg.deletion_days = 730
    cfg.batch_size = 1000
    cfg.primary_db_url = "mysql+pymysql://u:p@localhost/primary"
    cfg.archival_db_url = "mysql+pymysql://u:p@localhost/archival"
    cfg.archival_db_name = "archival"
    return cfg
