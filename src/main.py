import os
import shutil
import tempfile
import threading
from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext

class FolderCleaner:
    def __init__(self, output_text=None):
        self.file_count = 0
        self.dir_count = 0
        self.output_text = output_text

    def log_output(self, message):
        if self.output_text:
            self.output_text.insert(tk.END, message + '\n')
            self.output_text.see(tk.END)
        else:
            print(message)

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
                    self.log_output(f"Deleted file: {file_path}")
                except PermissionError:
                    self.log_output(f"Skipped (in use): {file_path}")
                except Exception as e:
                    self.log_output(f"Error deleting {file_path}: {e}")

        def delete_directories(dirs):
            for dir_path in dirs:
                try:
                    shutil.rmtree(dir_path)
                    self.dir_count += 1
                    self.log_output(f"Deleted directory: {dir_path}")
                except PermissionError:
                    self.log_output(f"Skipped (in use): {dir_path}")
                except Exception as e:
                    self.log_output(f"Error deleting {dir_path}: {e}")

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
            self.log_output("Clearing user's TEMP directory...")
            self.delete_folder_contents(user_temp_dir)

        if system_temp_enabled:
            system_temp_dir = Path("C:/Windows/Temp")
            if system_temp_dir.exists():
                self.log_output("Clearing system's TEMP directory...")
                self.delete_folder_contents(system_temp_dir)
            else:
                self.log_output("System TEMP directory does not exist or is inaccessible.")

        if prefetch_enabled:
            prefetch_dir = Path("C:/Windows/Prefetch")
            if prefetch_dir.exists():
                self.log_output("Clearing PREFETCH directory...")
                self.delete_folder_contents(prefetch_dir)
            else:
                self.log_output("PREFETCH directory does not exist or is inaccessible.")

        return self.file_count, self.dir_count


class CleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IDCATF - The cutest temp file remover")
        self.root.geometry("400x300")
        self.temp_var = tk.BooleanVar(value=True)
        self.system_temp_var = tk.BooleanVar(value=True)
        self.prefetch_var = tk.BooleanVar(value=True)
        self.output_window = None
        self.output_text = None
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="Select folders to clear:").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Checkbutton(self.root, text="User TEMP Folder", variable=self.temp_var).pack(anchor="w", padx=20)
        tk.Checkbutton(self.root, text="System TEMP Folder", variable=self.system_temp_var).pack(anchor="w", padx=20)
        tk.Checkbutton(self.root, text="Prefetch Folder", variable=self.prefetch_var).pack(anchor="w", padx=20)
        tk.Button(self.root, text="Open Output", command=self.open_output_window).pack(anchor="w", padx=20, pady=5)
        purge_button = tk.Button(self.root, text="Purge", command=self.start_purge)
        purge_button.pack(pady=20)

    def start_purge(self):
        cleaner = FolderCleaner(output_text=self.output_text)
        temp_enabled = self.temp_var.get()
        system_temp_enabled = self.system_temp_var.get()
        prefetch_enabled = self.prefetch_var.get()
        self.purge_thread = threading.Thread(
            target=self.perform_purge,
            args=(cleaner, temp_enabled, system_temp_enabled, prefetch_enabled)
        )
        self.purge_thread.start()

    def perform_purge(self, cleaner, temp_enabled, system_temp_enabled, prefetch_enabled):
        file_count, dir_count = cleaner.clear_selected_folders(temp_enabled, system_temp_enabled, prefetch_enabled)
        self.show_complete_window(file_count, dir_count)

    def show_complete_window(self, file_count, dir_count):
        complete_window = tk.Toplevel(self.root)
        complete_window.title("Complete!")
        complete_window.geometry("300x150")
        tk.Label(complete_window, text="Purge Complete!", font=("Arial", 16)).pack(pady=20)
        tk.Label(complete_window, text=f"Deleted {file_count} files and {dir_count} directories.").pack(pady=(0, 20))
        tk.Button(complete_window, text="OK", command=complete_window.destroy).pack()

    def open_output_window(self):
        if self.output_window is None or not tk.Toplevel.winfo_exists(self.output_window):
            self.output_window = tk.Toplevel(self.root)
            self.output_window.title("IDCATF - Output")
            self.output_window.geometry("500x400")
            self.output_text = scrolledtext.ScrolledText(self.output_window, wrap=tk.WORD, state='normal')
            self.output_text.pack(fill=tk.BOTH, expand=True)
        else:
            self.output_window.deiconify()


if __name__ == "__main__":
    root = tk.Tk()
    app = CleanerApp(root)
    root.mainloop()
