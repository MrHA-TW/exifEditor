import unittest
import tkinter as tk
from tkinter import ttk
import configparser
import os
import sys

# Add src directory to path to import gui
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from gui import ExifEditorGUI

class TestGUI(unittest.TestCase):

    def setUp(self):
        # Create a dummy config file for testing
        self.test_config_path = os.path.join(os.path.dirname(__file__), 'test_config.ini')
        config = configparser.ConfigParser()
        config['Settings'] = {
            'create_backup': 'true',
            'target_extensions': '.jpg, .jpeg'
        }
        config['EXIF'] = {
            'artist': 'Test Artist',
            'copyright': 'Test Copyright',
            'usercomment': '',
            'make': 'Test Make',
            'model': 'Test Model',
            'lensmodel': 'Test Lens'
        }
        config['History'] = {
            'camera_models': 'Test Model,Another Model',
            'lens_models': 'Test Lens,Another Lens'
        }
        with open(self.test_config_path, 'w') as configfile:
            config.write(configfile)

        # Create an instance of the GUI app
        self.app = ExifEditorGUI()
        # Override the config path to use the test config
        self.app.config_path = self.test_config_path
        self.app.config.read(self.test_config_path)
        # We need to call create_widgets again to use the new config
        for widget in self.app.winfo_children():
            widget.destroy()
        self.app.create_widgets()
        self.app.load_config()

    def tearDown(self):
        # Clean up the dummy config file
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
        self.app.destroy()

    def test_comboboxes_created(self):
        """Test if model and lensmodel widgets are Comboboxes."""
        self.assertIsInstance(self.app.exif_tags['model'], ttk.Combobox)
        self.assertIsInstance(self.app.exif_tags['lensmodel'], ttk.Combobox)

    def test_load_history(self):
        """Test if the history is loaded into comboboxes correctly."""
        self.assertEqual(list(self.app.exif_tags['model']['values']), ['Test Model', 'Another Model'])
        self.assertEqual(list(self.app.exif_tags['lensmodel']['values']), ['Test Lens', 'Another Lens'])

    def test_save_history(self):
        """Test if new entries are saved to the history."""
        new_camera = "New Camera"
        new_lens = "New Lens"
        self.app.exif_tags['model'].set(new_camera)
        self.app.exif_tags['lensmodel'].set(new_lens)

        self.app.save_config()

        config = configparser.ConfigParser()
        config.read(self.test_config_path)
        camera_history = config['History']['camera_models'].split(',')
        lens_history = config['History']['lens_models'].split(',')

        self.assertIn(new_camera, camera_history)
        self.assertIn(new_lens, lens_history)

    def test_update_user_comment(self):
        """Test if usercomment is updated automatically."""
        camera_model = "Super Camera"
        lens_model = "Super Lens"
        self.app.exif_tags['model'].set(camera_model)
        self.app.exif_tags['lensmodel'].set(lens_model)
        
        self.app.update_user_comment()

        expected_comment = f"{camera_model} Camera,{lens_model} Lens"
        self.assertEqual(self.app.exif_tags['usercomment'].get(), expected_comment)

if __name__ == '__main__':
    unittest.main()
