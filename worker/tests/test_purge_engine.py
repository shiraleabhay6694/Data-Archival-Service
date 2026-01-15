import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError


@pytest.fixture
def mock_cfg():
    cfg = Mock()
    cfg.table_name = "orders"
    cfg.date_column = "created_at"
    cfg.deletion_days = 730
    cfg.archival_db_name = "archival_data"
    cfg.batch_size = 1000
    cfg.archival_db_url = "mysql+pymysql://u:p@h:3306/archival"
    return cfg


class TestPurgeEngine:
    @patch('worker.service.purge_engine.create_engine')
    def test_connect(self, mock_create, mock_cfg):
        from worker.service.purge_engine import PurgeEngine
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=False)
        mock_create.return_value = mock_engine
        
        eng = PurgeEngine(mock_cfg)
        assert eng.connect() is True
    
    @patch('worker.service.purge_engine.create_engine')
    def test_connect_failure(self, mock_create, mock_cfg):
        from worker.service.purge_engine import PurgeEngine
        mock_create.side_effect = SQLAlchemyError("fail")
        eng = PurgeEngine(mock_cfg)
        assert eng.connect() is False
    
    @patch('worker.service.purge_engine.create_engine')
    def test_execute_returns_stats(self, mock_create, mock_cfg):
        from worker.service.purge_engine import PurgeEngine
        mock_engine = MagicMock()
        mock_create.return_value = mock_engine
        
        eng = PurgeEngine(mock_cfg)
        eng.engine = mock_engine
        
        with patch.object(eng, '_table_exists', return_value=True):
            with patch.object(eng, '_count_records', return_value=150):
                with patch.object(eng, '_purge_batch', side_effect=[100, 50, 0]):
                    result = eng.execute_purge()
                    assert result['records_deleted'] == 150
    
    @patch('worker.service.purge_engine.create_engine')
    def test_skips_if_no_table(self, mock_create, mock_cfg):
        from worker.service.purge_engine import PurgeEngine
        mock_engine = MagicMock()
        mock_create.return_value = mock_engine
        
        eng = PurgeEngine(mock_cfg)
        eng.engine = mock_engine
        
        with patch.object(eng, '_table_exists', return_value=False):
            result = eng.execute_purge()
            assert result['records_deleted'] == 0
