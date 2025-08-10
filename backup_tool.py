import customtkinter as ctk
from tkinter import filedialog, messagebox, PhotoImage
import os
import shutil
from PIL import Image
import threading
import sys
import json
import webbrowser
import platform
import subprocess
import re
import time

def create_gradient_button(master, **kwargs):
    """Create a button with gradient styling"""
    return ctk.CTkButton(
        master,
        fg_color=["white", "white"],
        text_color="#4fd1c5",
        hover_color=["#f0f0f0", "#f0f0f0"],
        border_color=["#4fd1c5", "#4fd1c5"],
        border_width=2,
        **kwargs
    )

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class BackupApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        self.source_path = ctk.StringVar()
        self.dest_path = ctk.StringVar()
        self.custom_name_var = ctk.StringVar()
        self.skipped_files = []
        
        self.default_name_var = ctk.StringVar()
        self.load_config()

        self.title("LocalVC")
        self.geometry("480x480")
        self.minsize(460, 460)
        
        self.stop_thread = False

        try:
            icon_path = resource_path("app_icon.ico")
            self.iconbitmap(icon_path)
            self.wm_iconbitmap(icon_path)
            icon = PhotoImage(file=resource_path("app_icon.png"))
            self.iconphoto(True, icon)
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.configure(fg_color="#181c20")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, corner_radius=18, fg_color="#23272e")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.create_widgets()
        self.toggle_custom_name_entry()

    def create_widgets(self):
        padx_value = 25
        
        ctk.CTkLabel(self.main_frame, text="LocalVC", font=ctk.CTkFont(size=22, weight="bold"), text_color="#4fd1c5").grid(
            row=0, column=0, columnspan=2, pady=(15, 20), padx=padx_value)

        ctk.CTkLabel(self.main_frame, text="Source Folder", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(0, 5), padx=padx_value)
        source_entry = ctk.CTkEntry(self.main_frame, textvariable=self.source_path, height=30, state="disabled", corner_radius=8, fg_color="#2D3748", border_color="#4A5568")
        source_entry.grid(row=2, column=0, sticky="ew", padx=(padx_value, 10))
        create_gradient_button(
            self.main_frame, text="Select", width=80, height=30, command=self.select_source_folder,
            corner_radius=8, font=ctk.CTkFont(weight="bold")
        ).grid(row=2, column=1, sticky="e", padx=(0, padx_value))

        ctk.CTkLabel(self.main_frame, text="Destination Folder", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(15, 5), padx=padx_value)
        dest_entry = ctk.CTkEntry(self.main_frame, textvariable=self.dest_path, height=30, state="disabled", corner_radius=8, fg_color="#2D3748", border_color="#4A5568")
        dest_entry.grid(row=4, column=0, sticky="ew", padx=(padx_value, 10))
        create_gradient_button(
            self.main_frame, text="Select", width=80, height=30, command=self.select_dest_folder,
            corner_radius=8, font=ctk.CTkFont(weight="bold")
        ).grid(row=4, column=1, sticky="e", padx=(0, padx_value))

        naming_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        naming_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(20, 15), padx=padx_value)
        naming_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkSwitch(naming_frame, text="Default Name (v1, v2...)", variable=self.default_name_var, onvalue="on", offvalue="off", command=self.toggle_custom_name_entry, progress_color="#4fd1c5").grid(
            row=0, column=0, sticky="w", pady=(0, 10))
        self.custom_name_entry = ctk.CTkEntry(naming_frame, textvariable=self.custom_name_var, placeholder_text="Enter a custom name...", corner_radius=8, fg_color="#2D3748", border_color="#4A5568", height=30)
        self.custom_name_entry.grid(row=1, column=0, sticky="ew")

        self.backup_button = create_gradient_button(
            self.main_frame, text="Backup Current Version", command=self.perform_backup, height=40,
            corner_radius=10, font=ctk.CTkFont(size=14, weight="bold")
        )
        self.backup_button.grid(row=6, column=0, columnspan=2, pady=(15, 15), sticky="ew", padx=padx_value)

        self.progress_label = ctk.CTkLabel(self.main_frame, text="", font=ctk.CTkFont(size=12))
        self.progress_label.grid(row=7, column=0, columnspan=2, padx=padx_value)
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, height=8, corner_radius=4)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(5, 15), padx=padx_value)
        self.progress_label.grid_remove()
        self.progress_bar.grid_remove()

        self.main_frame.grid_rowconfigure(9, weight=1)

        self.dev_info_button = ctk.CTkButton(
            self.main_frame, text="ⓘ", width=20, height=20, command=self.show_dev_info,
            corner_radius=20, font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#23272e", text_color="#808080", hover_color=["#2a2f36", "#2a2f36"],
            border_color=["#4A5568", "#4A5568"], border_width=2
        )
        self.dev_info_button.grid(row=10, column=1, pady=(0, 15), padx=(0, padx_value), sticky="se")

    def show_dev_info(self):
        """Shows the developer information dialog."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Developer Info")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        
        dialog.transient(self)
        dialog.grab_set()
        
        window_width = 300
        window_height = 200
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        dialog.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        
        dialog.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(dialog, text="Developer Info", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, pady=(15, 20), padx=20)
        
        def create_link(text, url, row):
            link = ctk.CTkButton(
                dialog, text=text, fg_color="transparent", hover_color=["#f0f0f0", "#2d3748"],
                text_color="#4fd1c5", command=lambda: webbrowser.open(url), height=25, cursor="hand2"
            )
            link.grid(row=row, column=0, pady=5, padx=20, sticky="w")
        
        create_link("GitHub: @Chamidu0423", "https://github.com/Chamidu0423", 1)
        create_link("Email: chamidudilshan0423@gmail.com", "mailto:chamidudilshan0423@gmail.com", 2)
        create_link("Website: chamidu-dilshaninfo.web.app", "https://chamidu-dilshaninfo.web.app/", 3)

        def set_dialog_icon():
            try:
                icon_path = resource_path("app_icon.ico")
                dialog.iconbitmap(default=icon_path)
                dialog.wm_iconbitmap(default=icon_path)
            except Exception as e:
                print(f"Warning: Could not load icon for dialog: {e}")
        
        dialog.after(10, set_dialog_icon)

    def load_config(self):
        """Loads the configuration from config.json."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.default_name_var.set(config.get('default_name', 'on'))
            else:
                self.default_name_var.set('on')
        except Exception as e:
            print(f"Error loading config: {e}")
            self.default_name_var.set('on')

    def save_config(self):
        """Saves the configuration to config.json."""
        try:
            config = {'default_name': self.default_name_var.get()}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")

    def perform_backup(self):
        if not self.source_path.get() or not self.dest_path.get():
            messagebox.showerror("Error", "Please select both source and destination folders.")
            return
        self.stop_thread = False
        threading.Thread(target=self._execute_backup_fast, daemon=True).start()

    def _get_dir_size(self, path):
        """Calculates the total size of a directory."""
        total = 0
        try:
            for dirpath, _, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        try:
                            total += os.path.getsize(fp)
                        except OSError:
                            pass
        except FileNotFoundError:
            return 0 
        return total

    def _update_progress_on_windows(self, dest_path, total_size):
        """Monitors destination folder size to update progress on Windows."""
        while not self.stop_thread:
            current_size = self._get_dir_size(dest_path)
            if total_size > 0:
                progress = min(1.0, current_size / total_size)
                self.progress_bar.set(progress)
                self.progress_label.configure(text=f"Copying... {int(progress * 100)}%")
                if progress >= 1.0:
                    break
            time.sleep(0.2)

    def _execute_backup_fast(self):
        """Uses system-native tools for a fast backup process."""
        self.backup_button.configure(state="disabled", text="Backing up...")
        self.progress_label.grid()
        self.progress_bar.grid()
        self.progress_bar.set(0)

        try:
            source = self.source_path.get()
            dest = self.dest_path.get()
            new_backup_folder_name = ""

            if self.default_name_var.get() == "on":
                version = 1
                while True:
                    folder_name = f"v{version}"
                    if not os.path.exists(os.path.join(dest, folder_name)):
                        new_backup_folder_name = folder_name
                        break
                    version += 1
            else:
                custom_name = self.custom_name_var.get().strip()
                if not custom_name:
                    messagebox.showerror("Error", "Please enter a custom name.")
                    return
                new_backup_folder_name = custom_name
                full_backup_path = os.path.join(dest, new_backup_folder_name)
                if os.path.exists(full_backup_path):
                    if messagebox.askyesno("Confirmation", f"'{new_backup_folder_name}' already exists. Replace it?"):
                        try:
                            shutil.rmtree(full_backup_path)
                        except OSError as e:
                            messagebox.showerror("Error", f"Could not remove existing directory: {e}")
                            return
                    else:
                        messagebox.showinfo("Cancelled", "Backup operation cancelled.")
                        return
            
            final_path = os.path.join(dest, new_backup_folder_name)
            os.makedirs(final_path, exist_ok=True)

            system = platform.system()
            command = []
            progress_thread = None

            if system == "Windows":
                self.progress_label.configure(text="Calculating size...")
                total_size = self._get_dir_size(source)
                
                progress_thread = threading.Thread(target=self._update_progress_on_windows, args=(final_path, total_size), daemon=True)
                progress_thread.start()

                command = ['robocopy', source, final_path, '/E', '/MT:8', '/R:2', '/W:5', '/NP', '/NJS', '/NJH']
            elif system in ["Linux", "Darwin"]:
                self.progress_label.configure(text="Copying with Rsync...")
                source_path_for_rsync = source if source.endswith('/') else source + '/'
                command = ['rsync', '-a', '--info=progress2', source_path_for_rsync, final_path]
            
            if not command:
                messagebox.showwarning("Unsupported OS", "This OS is not supported for fast copy.")
                return

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
            
            if system in ["Linux", "Darwin"]:
                rsync_progress_re = re.compile(r'(\d+)%')
                for line in iter(process.stdout.readline, ''):
                    match = rsync_progress_re.search(line)
                    if match:
                        progress = int(match.group(1))
                        self.progress_bar.set(progress / 100)
                        self.progress_label.configure(text=f"Copying... {progress}%")
            
            stdout_output, stderr_output = process.communicate()
            
            if progress_thread:
                self.stop_thread = True
                progress_thread.join()

            is_windows_success = system == "Windows" and process.returncode <= 8
            if process.returncode != 0 and not is_windows_success:
                raise Exception(f"Backup failed with exit code {process.returncode}:\n{stderr_output}")

            self.progress_bar.set(1)
            self.progress_label.configure(text="Copying complete!")
            success_message = f"Backup successful!\nFolder saved as: {new_backup_folder_name}"
            messagebox.showinfo("Success", success_message)

        except Exception as e:
            messagebox.showerror("Backup Failed", f"An error occurred: {e}")
        finally:
            self.stop_thread = True
            self.backup_button.configure(state="normal", text="Backup Current Version")
            self.progress_label.grid_remove()
            self.progress_bar.grid_remove()

    def select_source_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected: self.source_path.set(folder_selected)

    def select_dest_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected: self.dest_path.set(folder_selected)
            
    def toggle_custom_name_entry(self):
        if self.default_name_var.get() == "on":
            self.custom_name_entry.configure(state="disabled")
        else:
            self.custom_name_entry.configure(state="normal")
        self.save_config()

if __name__ == "__main__":
    app = BackupApp()
    app.mainloop()