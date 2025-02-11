# tests/services/etl/mapping/test_map_config.py

import os
from app.services.etl.mapping.map_config import MapConfig

def test_map_config():
    """Test basic map configuration."""
    config = MapConfig()
    
    # Test Finsbury Park coordinates
    assert isinstance(config.FPK_LATITUDE, float)
    assert isinstance(config.FPK_LONGITUDE, float)
    assert config.FPK_LATITUDE == 51.5643002449157
    assert config.FPK_LONGITUDE == -0.106284978884699
    
    # Test directory creation
    assert os.path.exists(MapConfig.OUTPUT_DIR)
