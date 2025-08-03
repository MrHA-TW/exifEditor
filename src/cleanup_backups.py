import os
import argparse

def cleanup_backups(directory):
    """
    Removes all files with a .bak extension from a directory.

    Args:
        directory (str): The path to the directory to clean up.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.bak'):
                os.remove(os.path.join(root, file))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clean up backup files (.bak) in a directory.')
    parser.add_argument('directory', help='The directory to clean up.')
    args = parser.parse_args()
    cleanup_backups(args.directory)
