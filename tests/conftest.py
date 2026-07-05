import pytest
import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def sample_project(temp_dir):
    """Create a sample project directory structure."""
    project_dir = temp_dir / "sample_project"
    project_dir.mkdir()
    (project_dir / "main.py").write_text("print('hello')")
    (project_dir / "utils").mkdir()
    (project_dir / "utils" / "__init__.py").write_text("from .helpers import helper")
    (project_dir / "utils" / "helpers.py").write_text("def helper(): return 'help'")
    return project_dir


@pytest.fixture
def engine_fixture():
    """Provide an initialized engine for tests."""
    from omniforge.config import OmniForgeConfig
    from omniforge.core.engine import OmniForgeEngine
    
    config = OmniForgeConfig()
    engine = OmniForgeEngine(config)
    engine.initialize()
    
    yield engine
    
    engine.shutdown()