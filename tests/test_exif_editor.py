import os
import shutil
import tempfile
import configparser
from PIL import Image
import piexif
import pytest

# Import the function we want to test (it doesn't exist yet)
from src.exif_editor import process_directory

@pytest.fixture
def temp_image_dir():
    """Create a temporary directory with dummy image files for testing."""
    temp_dir = tempfile.mkdtemp()
    
    # Create dummy image files
    Image.new('RGB', (100, 100), color = 'red').save(os.path.join(temp_dir, 'image1.jpg'))
    Image.new('RGB', (100, 100), color = 'blue').save(os.path.join(temp_dir, 'image2.jpeg'))
    
    # Create a non-image file
    with open(os.path.join(temp_dir, 'notes.txt'), 'w') as f:
        f.write('This is a text file.')
        
    # Create a config file
    config = configparser.ConfigParser()
    config['Settings'] = {
        'create_backup': 'true',
        'target_extensions': '.jpg, .jpeg'
    }
    config['EXIF'] = {
        'Artist': 'Test Artist',
        'Copyright': 'Test Copyright'
    }
    with open(os.path.join(temp_dir, 'config.ini'), 'w') as configfile:
        config.write(configfile)

    yield temp_dir, os.path.join(temp_dir, 'config.ini')
    
    # Teardown: remove the temporary directory
    shutil.rmtree(temp_dir)

def test_process_directory(temp_image_dir):
    """
    Test the main functionality of processing a directory.
    """
    temp_dir, config_path = temp_image_dir

    # Run the function to be tested
    process_directory(temp_dir, config_path)

    # 1. Check if backups were created for image files
    assert os.path.exists(os.path.join(temp_dir, 'image1.jpg.bak'))
    assert os.path.exists(os.path.join(temp_dir, 'image2.jpeg.bak'))
    
    # 2. Check that no backup was created for the non-image file
    assert not os.path.exists(os.path.join(temp_dir, 'notes.txt.bak'))

    # 3. Check if EXIF tags were written to the image files
    exif_dict_1 = piexif.load(os.path.join(temp_dir, 'image1.jpg'))
    exif_dict_2 = piexif.load(os.path.join(temp_dir, 'image2.jpeg'))

    assert exif_dict_1['0th'][piexif.ImageIFD.Artist].decode('utf-8') == 'Test Artist'
    assert exif_dict_1['0th'][piexif.ImageIFD.Copyright].decode('utf-8') == 'Test Copyright'
    assert exif_dict_2['0th'][piexif.ImageIFD.Artist].decode('utf-8') == 'Test Artist'
    assert exif_dict_2['0th'][piexif.ImageIFD.Copyright].decode('utf-8') == 'Test Copyright'

    # 4. Check that the non-image file was not modified
    with open(os.path.join(temp_dir, 'notes.txt'), 'r') as f:
        content = f.read()
    assert content == 'This is a text file.'

def test_process_directory_case_insensitive(temp_image_dir):
    """
    Test that the process_directory function handles case-insensitive extensions.
    """
    temp_dir, config_path = temp_image_dir
    
    # Create an image with an uppercase extension
    Image.new('RGB', (100, 100), color = 'green').save(os.path.join(temp_dir, 'image3.JPG'))

    # Run the function to be tested
    process_directory(temp_dir, config_path)

    # Check if a backup was created for the uppercase extension image
    assert os.path.exists(os.path.join(temp_dir, 'image3.JPG.bak'))

    # Check if EXIF tags were written to the uppercase extension image
    exif_dict_3 = piexif.load(os.path.join(temp_dir, 'image3.JPG'))
    assert exif_dict_3['0th'][piexif.ImageIFD.Artist].decode('utf-8') == 'Test Artist'
    assert exif_dict_3['0th'][piexif.ImageIFD.Copyright].decode('utf-8') == 'Test Copyright'