import os
import sys
import pytest
import tempfile
import shutil

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import app after path is set up
from app import app as flask_app

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    # Create necessary static directories
    static_dir = os.path.join(project_root, 'static')
    previews_dir = os.path.join(static_dir, 'Data_pic', 'previews')
    os.makedirs(previews_dir, exist_ok=True)
    
    # Create a test image file
    test_image_path = os.path.join(previews_dir, 'test.jpg')
    with open(test_image_path, 'wb') as f:
        f.write(b'fake-image-content')
    
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'DATABASE': db_path
    })
    
    # Create the database and load test data
    with flask_app.app_context():
        from app import init_db
        init_db()
    
    yield flask_app
    
    # Clean up
    os.close(db_fd)
    os.unlink(db_path)
    # Don't remove static directories as they might be needed by other tests 