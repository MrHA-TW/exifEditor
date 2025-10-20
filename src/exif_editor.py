import os
import shutil
import configparser
import piexif
import piexif.helper
import argparse
import logging


def get_exif_summary_from_directory(directory_path, target_extensions):
    """
    Scans a directory for images and returns a summary of their EXIF data.

    Args:
        directory_path (str): The path to the directory to scan.
        target_extensions (list): A list of file extensions to check.

    Returns:
        list: A list of dictionaries, each containing info for one file.
    """
    summary_data = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if any(file.lower().endswith(ext.lower()) for ext in target_extensions):
                image_path = os.path.join(root, file)
                try:
                    exif_dict = piexif.load(image_path)
                    make = exif_dict.get("0th", {}).get(piexif.ImageIFD.Make, b'').decode('utf-8', 'ignore')
                    model = exif_dict.get("0th", {}).get(piexif.ImageIFD.Model, b'').decode('utf-8', 'ignore')
                    lens_model = exif_dict.get("Exif", {}).get(piexif.ExifIFD.LensModel, b'').decode('utf-8', 'ignore')

                    summary_data.append({
                        'filename': file,
                                    'make': make if make else 'N/A',
                                    'model': model if model else 'N/A',
                                    'lens_model': lens_model if lens_model else 'N/A'                    })
                except Exception as e:
                    logging.warning(f"Could not read EXIF from {image_path}: {e}")
                    summary_data.append({
                        'filename': file,
                        'make': '讀取失敗',
                        'model': '讀取失敗',
                        'lens_model': '讀取失敗'
                    })
    return summary_data


def add_exif_tags_to_file(image_path, config):
    """
    Adds EXIF tags to a single image file based on the provided config.

    Args:
        image_path (str): The path to the image file.
        config (ConfigParser): The configuration object with EXIF tags.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        logging.info(f"Processing: {image_path}")
        try:
            exif_dict = piexif.load(image_path)
        except piexif.InvalidImageDataError:
            # If the image does not contain EXIF data, create a new EXIF dictionary.
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}

        # Ensure the '0th' and 'Exif' IFD dictionaries exist.
        if '0th' not in exif_dict:
            exif_dict['0th'] = {}
        if 'Exif' not in exif_dict:
            exif_dict['Exif'] = {}

        for key, value in config['EXIF'].items():
            if not value:  # Skip if the value is empty
                continue

            if key.lower() == 'artist':
                exif_dict['0th'][piexif.ImageIFD.Artist] = value.encode('utf-8')
            elif key.lower() == 'copyright':
                exif_dict['0th'][piexif.ImageIFD.Copyright] = value.encode('utf-8')
            elif key.lower() == 'make':
                exif_dict['0th'][piexif.ImageIFD.Make] = value.encode('utf-8')
            elif key.lower() == 'model':
                exif_dict['0th'][piexif.ImageIFD.Model] = value.encode('utf-8')
            elif key.lower() == 'software':
                exif_dict['0th'][piexif.ImageIFD.Software] = value.encode('utf-8')
            elif key.lower() == 'datetimeoriginal':
                exif_dict['Exif'][piexif.ExifIFD.DateTimeOriginal] = value.encode('utf-8')
            elif key.lower() == 'usercomment':
                exif_dict['Exif'][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(value, encoding="unicode")
            elif key.lower() == 'lensmake':
                exif_dict['Exif'][piexif.ExifIFD.LensMake] = value.encode('utf-8')
            elif key.lower() == 'lensmodel':
                exif_dict['Exif'][piexif.ExifIFD.LensModel] = value.encode('utf-8')

        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, image_path)
        return True
    except Exception as e:
        logging.error(f"Error processing file {image_path}: {e}")
        return False

def process_directory(directory_path, config_path):
    """
    Processes all images in a directory, adding EXIF tags based on a config file.

    Args:
        directory_path (str): The path to the directory containing images.
        config_path (str): The path to the configuration file.
    """
    logging.basicConfig(filename='exif_editor.log', 
                        level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        logging.error(f"Config file not found at {config_path}")
        print(f"Error: Config file not found at {config_path}")
        return

    config.read(config_path)

    if not config.has_section('Settings') or not config.has_section('EXIF'):
        logging.error("Config file must contain [Settings] and [EXIF] sections.")
        print("Error: Config file must contain [Settings] and [EXIF] sections.")
        return

    if not config.has_option('Settings', 'target_extensions') or not config.get('Settings', 'target_extensions'):
        logging.error("'target_extensions' is not defined or is empty in the [Settings] section.")
        print("Error: 'target_extensions' is not defined or is empty in the [Settings] section.")
        return

    target_extensions = [ext.strip() for ext in config.get('Settings', 'target_extensions').split(',')]
    
    logging.info(f"Starting to process files in: {directory_path}")
    print(f"Starting to process files in: {directory_path}")
    
    total_files = 0
    success_count = 0
    error_count = 0

    for root, _, files in os.walk(directory_path):
        for file in files:
            if any(file.lower().endswith(ext.lower()) for ext in target_extensions):
                total_files += 1
                image_path = os.path.join(root, file)
                
                if config.getboolean('Settings', 'create_backup'):
                    shutil.copy2(image_path, image_path + '.bak')
                
                if add_exif_tags_to_file(image_path, config):
                    success_count += 1
                else:
                    error_count += 1
    
    summary = f"\n--- Processing Summary ---\nTotal files processed: {total_files}\nSuccessful: {success_count}\nErrors: {error_count}\n--------------------------"
    logging.info(summary)
    print(summary)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add EXIF tags to images in a directory.')
    parser.add_argument('directory', help='The directory containing the images to process.')
    parser.add_argument('--config', default='config/config.ini', help='The path to the config file.')
    args = parser.parse_args()
    process_directory(args.directory, args.config)