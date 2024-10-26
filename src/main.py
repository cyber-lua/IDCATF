# By cyber :D

import os
import shutil
import tempfile
import threading
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

class FolderCleaner:
    def __init__(self):
        self.file_count = 0
        self.dir_count = 0

    def delete_folder_contents(self, folder_path):
        files, dirs = [], []
        for root, dirnames, filenames in os.walk(folder_path, topdown=False):
            files.extend([os.path.join(root, name) for name in filenames])
            dirs.extend([os.path.join(root, name) for name in dirnames])

        def delete_files(files):
            for file_path in files:
                try:
                    os.remove(file_path)
                    self.file_count += 1
                except PermissionError:
                    print(f"Skipped (in use): {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

        def delete_directories(dirs):
            for dir_path in dirs:
                try:
                    shutil.rmtree(dir_path)
                    self.dir_count += 1
                except PermissionError:
                    print(f"Skipped (in use): {dir_path}")
                except Exception as e:
                    print(f"Error deleting {dir_path}: {e}")

        file_thread = threading.Thread(target=delete_files, args=(files,))
        dir_thread = threading.Thread(target=delete_directories, args=(dirs,))

        file_thread.start()
        dir_thread.start()
        file_thread.join()
        dir_thread.join()

    def clear_selected_folders(self, temp_enabled, system_temp_enabled, prefetch_enabled):
        self.file_count = 0
        self.dir_count = 0

        if temp_enabled:
            user_temp_dir = tempfile.gettempdir()
            print("Clearing user's TEMP directory...")
            self.delete_folder_contents(user_temp_dir)

        if system_temp_enabled:
            system_temp_dir = Path("C:/Windows/Temp")
            if system_temp_dir.exists():
                print("Clearing system's TEMP directory...")
                self.delete_folder_contents(system_temp_dir)
            else:
                print("System TEMP directory does not exist or is inaccessible.")

        if prefetch_enabled:
            prefetch_dir = Path("C:/Windows/Prefetch")
            if prefetch_dir.exists():
                print("Clearing PREFETCH directory...")
                self.delete_folder_contents(prefetch_dir)
            else:
                print("PREFETCH directory does not exist or is inaccessible.")

        return self.file_count, self.dir_count


class CleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IDCATF")
        
        self.temp_var = tk.BooleanVar(value=True)
        self.system_temp_var = tk.BooleanVar(value=True)
        self.prefetch_var = tk.BooleanVar(value=True)
        
        self.setup_ui()

    def setup_ui(self):
        
        tk.Label(self.root, text="Select folders to clear:").pack(anchor="w")
        tk.Checkbutton(self.root, text="User TEMP Folder", variable=self.temp_var).pack(anchor="w")
        tk.Checkbutton(self.root, text="System TEMP Folder", variable=self.system_temp_var).pack(anchor="w")
        tk.Checkbutton(self.root, text="Prefetch Folder", variable=self.prefetch_var).pack(anchor="w")
        
        purge_button = tk.Button(self.root, text="Purge", command=self.start_purge)
        purge_button.pack(pady=10)

    def start_purge(self):
        cleaner = FolderCleaner()
        temp_enabled = self.temp_var.get()
        system_temp_enabled = self.system_temp_var.get()
        prefetch_enabled = self.prefetch_var.get()

        purge_thread = threading.Thread(target=self.perform_purge, args=(cleaner, temp_enabled, system_temp_enabled, prefetch_enabled))
        purge_thread.start()

    def perform_purge(self, cleaner, temp_enabled, system_temp_enabled, prefetch_enabled):
        file_count, dir_count = cleaner.clear_selected_folders(temp_enabled, system_temp_enabled, prefetch_enabled)
        
        messagebox.showinfo("Purge Complete", f"Purging complete! Deleted {file_count} files and {dir_count} directories.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CleanerApp(root)
    root.mainloop()
