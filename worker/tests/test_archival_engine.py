import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError


@pytest.fixture
def mock_cfg():
    cfg = Mock()
    cfg.table_name = "orders"
    cfg.date_column = "created_at"
    cfg.archival_days = 180
    cfg.batch_size = 1000
    cfg.primary_db_url = "mysql+pymysql://u:p@h:3306/primary"
    cfg.archival_db_url = "mysql+pymysql://u:p@h:3306/archival"
    return cfg


class TestArchivalEngine:
    @patch('worker.service.archival_engine.create_engine')
    def test_connect(self, mock_create, mock_cfg):
        from worker.service.archival_engine import ArchivalEngine
        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.connect.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_engine.connect.return_value.__exit__ = Mock(return_value=False)
        mock_create.return_value = mock_engine
        
        eng = ArchivalEngine(mock_cfg)
        assert eng.connect() is True
    
    @patch('worker.service.archival_engine.create_engine')
    def test_connect_failure(self, mock_create, mock_cfg):
        from worker.service.archival_engine import ArchivalEngine
        mock_create.side_effect = SQLAlchemyError("fail")
        eng = ArchivalEngine(mock_cfg)
        assert eng.connect() is False
    
    def test_execute_returns_stats(self, mock_cfg):
        from worker.service.archival_engine import ArchivalEngine
        eng = ArchivalEngine(mock_cfg)
        
        with patch.object(eng, '_ensure_archive_table', return_value=True):
            with patch.object(eng, '_archive_batch', side_effect=[100, 50, 0]):
                with patch.object(eng, '_close'):
                    result = eng.execute_archival()
                    assert result['records_archived'] == 150
    
    def test_close_disposes_engines(self, mock_cfg):
        from worker.service.archival_engine import ArchivalEngine
        eng = ArchivalEngine(mock_cfg)
        eng.primary_engine = MagicMock()
        eng.archival_engine = MagicMock()
        eng._close()
        eng.primary_engine.dispose.assert_called_once()
        eng.archival_engine.dispose.assert_called_once()
