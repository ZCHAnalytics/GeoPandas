# tests/test_basic.py

def test_simple():
    """Basic test to verify pytest is working."""
    assert True

def test_import_settings():
    """Test that we can import settings."""
    from app.core.config import settings
    assert settings is not None