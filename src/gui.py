import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import configparser
import os
from exif_editor import process_directory
from cleanup_backups import cleanup_backups
import threading
import queue

class ExifEditorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EXIF Editor")
        self.geometry("600x500")

        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.ini')
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        # Ensure History section exists
        if not self.config.has_section('History'):
            self.config.add_section('History')
            self.config.set('History', 'camera_models', '')
            self.config.set('History', 'lens_models', '')

        self.exif_tags = {}
        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        # Frame for EXIF tags
        exif_frame = tk.LabelFrame(self, text="EXIF Tags", padx=10, pady=10)
        exif_frame.pack(padx=10, pady=10, fill="x")

        # Create entry for each EXIF tag
        row = 0
        for section in self.config.sections():
            if section == 'EXIF':
                for key in self.config[section]:
                    label = tk.Label(exif_frame, text=key.replace('_', ' ').title())
                    label.grid(row=row, column=0, sticky="w", padx=5, pady=2)
                    
                    if key == 'model':
                        self.exif_tags[key] = ttk.Combobox(exif_frame, width=57)
                        self.exif_tags[key].grid(row=row, column=1, sticky="ew", padx=5, pady=2)
                        self.exif_tags[key].bind('<<ComboboxSelected>>', self.update_user_comment)
                        self.exif_tags[key].bind('<KeyRelease>', self.update_user_comment)
                    elif key == 'lensmodel':
                        self.exif_tags[key] = ttk.Combobox(exif_frame, width=57)
                        self.exif_tags[key].grid(row=row, column=1, sticky="ew", padx=5, pady=2)
                        self.exif_tags[key].bind('<<ComboboxSelected>>', self.update_user_comment)
                        self.exif_tags[key].bind('<KeyRelease>', self.update_user_comment)
                    else:
                        entry = tk.Entry(exif_frame, width=60)
                        entry.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
                        self.exif_tags[key] = entry
                    row += 1
        
        exif_frame.columnconfigure(1, weight=1)

        # Frame for directory selection
        dir_frame = tk.Frame(self, padx=10, pady=5)
        dir_frame.pack(fill="x")

        self.dir_label = tk.Label(dir_frame, text="No directory selected", bg="white", anchor="w", relief="sunken")
        self.dir_label.pack(side="left", fill="x", expand=True, ipady=2)
        
        dir_button = tk.Button(dir_frame, text="Select Directory", command=self.select_directory)
        dir_button.pack(side="right", padx=5)

        # Frame for actions
        action_frame = tk.Frame(self, padx=10, pady=10)
        action_frame.pack(fill="x")

        start_button = tk.Button(action_frame, text="Save & Start Processing", command=self.start_processing)
        start_button.pack(side="right")

        cleanup_button = tk.Button(action_frame, text="Cleanup Backups", command=self.cleanup_backups_thread)
        cleanup_button.pack(side="left")

        # Frame for output log
        log_frame = tk.LabelFrame(self, text="Log", padx=10, pady=10)
        log_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state='disabled')
        self.log_area.pack(fill="both", expand=True)

    def load_config(self):
        # Load EXIF values
        if 'EXIF' in self.config:
            for key, widget in self.exif_tags.items():
                if isinstance(widget, ttk.Combobox):
                    widget.set(self.config['EXIF'].get(key, ''))
                else:
                    widget.insert(0, self.config['EXIF'].get(key, ''))

        # Load history for comboboxes
        if 'History' in self.config:
            camera_models = self.config['History'].get('camera_models', '').split(',')
            lens_models = self.config['History'].get('lens_models', '').split(',')
            
            self.exif_tags['model']['values'] = [model for model in camera_models if model]
            self.exif_tags['lensmodel']['values'] = [model for model in lens_models if model]
        
        self.update_user_comment()

    def save_config(self):
        if 'EXIF' in self.config:
            for key, widget in self.exif_tags.items():
                self.config['EXIF'][key] = widget.get()

        # Save history for comboboxes
        if 'History' in self.config:
            # Camera model history
            current_camera = self.exif_tags['model'].get()
            camera_history = self.config['History'].get('camera_models', '').split(',')
            camera_history = [model.strip() for model in camera_history if model]
            if current_camera and current_camera not in camera_history:
                camera_history.append(current_camera)
            self.config['History']['camera_models'] = ','.join(camera_history)

            # Lens model history
            current_lens = self.exif_tags['lensmodel'].get()
            lens_history = self.config['History'].get('lens_models', '').split(',')
            lens_history = [model.strip() for model in lens_history if model]
            if current_lens and current_lens not in lens_history:
                lens_history.append(current_lens)
            self.config['History']['lens_models'] = ','.join(lens_history)

        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

    def update_user_comment(self, event=None):
        camera_model = self.exif_tags['model'].get()
        lens_model = self.exif_tags['lensmodel'].get()
        
        if camera_model and lens_model:
            comment = f"{camera_model} Camera,{lens_model} Lens"
            user_comment_widget = self.exif_tags.get('usercomment')
            if user_comment_widget:
                user_comment_widget.delete(0, tk.END)
                user_comment_widget.insert(0, comment)

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_path = directory
            self.dir_label.config(text=directory)

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + '\n')
        self.log_area.config(state='disabled')
        self.log_area.see(tk.END)

    def start_processing(self):
        if not hasattr(self, 'directory_path') or not self.directory_path:
            self.log("Error: Please select a directory first.")
            return

        self.save_config()
        self.log("Configuration saved.")
        self.log(f"Starting to process files in: {self.directory_path}")

        # Run processing in a separate thread to avoid freezing the GUI
        self.processing_thread = threading.Thread(
            target=self.run_processing,
            args=(self.directory_path, self.config_path)
        )
        self.processing_thread.start()

    def run_processing(self, directory_path, config_path):
        # This is a workaround to capture print statements from process_directory
        q = queue.Queue()
        
        def process_wrapper(directory_path, config_path, queue):
            # Redirect stdout
            import sys
            original_stdout = sys.stdout
            sys.stdout = TTY_Proxy(queue)
            
            try:
                process_directory(directory_path, config_path)
            finally:
                # Restore stdout
                sys.stdout = original_stdout

        thread = threading.Thread(target=process_wrapper, args=(directory_path, config_path, q))
        thread.start()

        while thread.is_alive() or not q.empty():
            try:
                line = q.get_nowait()
                self.after(0, self.log, line.strip())
            except queue.Empty:
                pass
        thread.join()

    def cleanup_backups_thread(self):
        if not hasattr(self, 'directory_path') or not self.directory_path:
            self.log("Error: Please select a directory first.")
            return

        self.log(f"Starting to cleanup backup files in: {self.directory_path}")
        # Run cleanup in a separate thread to avoid freezing the GUI
        cleanup_thread = threading.Thread(
            target=self.run_cleanup,
            args=(self.directory_path,)
        )
        cleanup_thread.start()

    def run_cleanup(self, directory_path):
        cleanup_backups(directory_path)
        self.log("Cleanup finished.")

class TTY_Proxy:
    def __init__(self, queue):
        self.queue = queue

    def write(self, text):
        self.queue.put(text)

    def flush(self):
        pass

if __name__ == "__main__":
    app = ExifEditorGUI()
    app.mainloop()
