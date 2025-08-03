
import os
import shutil
import tempfile
import pytest

# Import the function we want to test (it doesn't exist yet)
from src.cleanup_backups import cleanup_backups

@pytest.fixture
def temp_dir_with_backups():
    """Create a temporary directory with dummy files and backups for testing."""
    temp_dir = tempfile.mkdtemp()
    
    # Create dummy files
    with open(os.path.join(temp_dir, 'image1.jpg'), 'w') as f:
        f.write('dummy image data')
    with open(os.path.join(temp_dir, 'image1.jpg.bak'), 'w') as f:
        f.write('dummy backup data')
    with open(os.path.join(temp_dir, 'notes.txt'), 'w') as f:
        f.write('This is a text file.')
    with open(os.path.join(temp_dir, 'image2.jpeg.bak'), 'w') as f:
        f.write('dummy backup data 2')

    yield temp_dir
    
    # Teardown: remove the temporary directory
    shutil.rmtree(temp_dir)

def test_cleanup_backups(temp_dir_with_backups):
    """
    Test the backup cleanup functionality.
    """
    # Run the function to be tested
    cleanup_backups(temp_dir_with_backups)

    # 1. Check that backup files have been deleted
    assert not os.path.exists(os.path.join(temp_dir_with_backups, 'image1.jpg.bak'))
    assert not os.path.exists(os.path.join(temp_dir_with_backups, 'image2.jpeg.bak'))

    # 2. Check that other files still exist
    assert os.path.exists(os.path.join(temp_dir_with_backups, 'image1.jpg'))
    assert os.path.exists(os.path.join(temp_dir_with_backups, 'notes.txt'))
