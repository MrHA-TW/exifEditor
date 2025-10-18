import argparse
import configparser
import os
from exif_editor import get_exif_summary_from_directory
import json

def query_directory_exif(directory_path, config_path='config/config.ini'):
    """
    Processes a directory to get EXIF summary and prints it.

    Args:
        directory_path (str): The path to the directory containing images.
        config_path (str): The path to the configuration file.
    """
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        print(f"錯誤：找不到設定檔 {config_path}")
        return

    config.read(config_path)

    if not config.has_option('Settings', 'target_extensions'):
        print("錯誤：設定檔中缺少 'target_extensions'")
        return

    target_extensions = [ext.strip() for ext in config.get('Settings', 'target_extensions').split(',')]
    
    print(f"正在掃描目錄：{directory_path}")
    
    summary_data = get_exif_summary_from_directory(directory_path, target_extensions)
    
    if not summary_data:
        print("在指定目錄中找不到任何符合條件的圖片檔案。")
        return

    # 準備要輸出的格式
    # 首先找到最長的檔案名稱，以便對齊
    max_len = max(len(item['filename']) for item in summary_data)
    header = f"{'檔案名稱':<{max_len}} | {'相機製造商':<15} | {'相機型號':<20} | {'鏡頭型號':<25}"
    print(header)
    print("-" * len(header))

    for item in summary_data:
        filename = item['filename']
        make = item['make']
        model = item['model']
        lens_model = item['lens_model']
        print(f"{filename:<{max_len}} | {make:<15} | {model:<20} | {lens_model:<25}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='查詢目錄中圖片的 EXIF 資訊摘要。')
    parser.add_argument('directory', help='包含圖片的目錄路徑')
    parser.add_argument('--config', default='config/config.ini', help='設定檔的路徑')
    args = parser.parse_args()
    
    query_directory_exif(args.directory, args.config)
