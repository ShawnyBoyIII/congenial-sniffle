import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys
import os

from imager import create_image
from carver import carve_files
from bootable import create_bootable_usb

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ResQCard - Data Extraction Tool")
        self.root.geometry("600x500")

        self.cancel_event = threading.Event()
        self.worker_thread = None

        self.create_widgets()

    def create_widgets(self):
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tabs
        self.tab_imager = ttk.Frame(self.notebook)
        self.tab_carver = ttk.Frame(self.notebook)
        self.tab_bootable = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_imager, text="1. Create Image")
        self.notebook.add(self.tab_carver, text="2. Extract Files")
        self.notebook.add(self.tab_bootable, text="3. Create Bootable USB")

        self.setup_imager_tab()
        self.setup_carver_tab()
        self.setup_bootable_tab()

        # Shared Progress and Status
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill='x', padx=10, pady=5)

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(status_frame, textvariable=self.status_var).pack(side='left')

        self.progress_var = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progressbar.pack(side='right', fill='x', expand=True, padx=(10, 0))

    # --- Imager Tab ---
    def setup_imager_tab(self):
        frame = self.tab_imager

        ttk.Label(frame, text="Source Device / File (e.g. /dev/sdb):").grid(row=0, column=0, sticky='w', pady=5)
        self.imager_src = tk.StringVar()
        ttk.Entry(frame, textvariable=self.imager_src, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Browse", command=lambda: self.browse_file(self.imager_src)).grid(row=0, column=2)

        ttk.Label(frame, text="Destination Image (.img):").grid(row=1, column=0, sticky='w', pady=5)
        self.imager_dst = tk.StringVar()
        ttk.Entry(frame, textvariable=self.imager_dst, width=40).grid(row=1, column=1, padx=5)
        ttk.Button(frame, text="Browse", command=lambda: self.browse_save_file(self.imager_dst, [("Image Files", "*.img")])).grid(row=1, column=2)

        ttk.Button(frame, text="Start Imaging", command=self.start_imaging).grid(row=2, column=0, columnspan=3, pady=20)
        ttk.Button(frame, text="Cancel", command=self.cancel_task).grid(row=3, column=0, columnspan=3)

    def start_imaging(self):
        src = self.imager_src.get()
        dst = self.imager_dst.get()
        if not src or not dst:
            messagebox.showerror("Error", "Please specify source and destination.")
            return

        self.run_task(self.imager_task, src, dst)

    def imager_task(self, src, dst):
        def progress(read, total, errors):
            pct = (read / total * 100) if total > 0 else 0
            self.update_progress(f"Imaging... Errors: {errors}", pct)

        success, msg = create_image(src, dst, progress_callback=progress, cancel_event=self.cancel_event)
        self.task_finished(success, msg)


    # --- Carver Tab ---
    def setup_carver_tab(self):
        frame = self.tab_carver

        ttk.Label(frame, text="Source Image/Device:").grid(row=0, column=0, sticky='w', pady=5)
        self.carver_src = tk.StringVar()
        ttk.Entry(frame, textvariable=self.carver_src, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Browse", command=lambda: self.browse_file(self.carver_src)).grid(row=0, column=2)

        ttk.Label(frame, text="Output Directory:").grid(row=1, column=0, sticky='w', pady=5)
        self.carver_dst = tk.StringVar()
        ttk.Entry(frame, textvariable=self.carver_dst, width=40).grid(row=1, column=1, padx=5)
        ttk.Button(frame, text="Browse", command=lambda: self.browse_dir(self.carver_dst)).grid(row=1, column=2)

        ttk.Button(frame, text="Start Extracting", command=self.start_carving).grid(row=2, column=0, columnspan=3, pady=20)
        ttk.Button(frame, text="Cancel", command=self.cancel_task).grid(row=3, column=0, columnspan=3)

    def start_carving(self):
        src = self.carver_src.get()
        dst = self.carver_dst.get()
        if not src or not dst:
            messagebox.showerror("Error", "Please specify source and destination.")
            return

        self.run_task(self.carver_task, src, dst)

    def carver_task(self, src, dst):
        def progress(read, total, files):
            pct = (read / total * 100) if total > 0 else 0
            self.update_progress(f"Carving... Found {files} files.", pct)

        success, msg = carve_files(src, dst, progress_callback=progress, cancel_event=self.cancel_event)
        self.task_finished(success, msg)

    # --- Bootable Tab ---
    def setup_bootable_tab(self):
        frame = self.tab_bootable

        ttk.Label(frame, text="Target USB Device (e.g. /dev/sdc):\\nWARNING: THIS WILL WIPE THE DRIVE").grid(row=0, column=0, sticky='w', pady=5)
        self.boot_dst = tk.StringVar()
        ttk.Entry(frame, textvariable=self.boot_dst, width=40).grid(row=0, column=1, padx=5)

        ttk.Button(frame, text="Create Bootable USB", command=self.start_bootable).grid(row=1, column=0, columnspan=2, pady=20)
        ttk.Button(frame, text="Cancel", command=self.cancel_task).grid(row=2, column=0, columnspan=2)

    def start_bootable(self):
        dst = self.boot_dst.get()
        if not dst:
            messagebox.showerror("Error", "Please specify target USB device.")
            return

        if messagebox.askyesno("Confirm", f"Are you sure you want to write to {dst}? All data will be lost."):
            self.run_task(self.bootable_task, dst)

    def bootable_task(self, dst):
        def progress(status, pct):
            self.update_progress(status, pct)

        success, msg = create_bootable_usb(dst, progress_callback=progress, cancel_event=self.cancel_event)
        self.task_finished(success, msg)


    # --- Helpers ---
    def browse_file(self, var):
        path = filedialog.askopenfilename()
        if path:
            var.set(path)

    def browse_save_file(self, var, filetypes):
        path = filedialog.asksaveasfilename(filetypes=filetypes)
        if path:
            var.set(path)

    def browse_dir(self, var):
        path = filedialog.askdirectory()
        if path:
            var.set(path)

    def run_task(self, target, *args):
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showwarning("Warning", "A task is already running.")
            return

        self.cancel_event.clear()
        self.progress_var.set(0)
        self.worker_thread = threading.Thread(target=target, args=args, daemon=True)
        self.worker_thread.start()

    def cancel_task(self):
        self.cancel_event.set()
        self.status_var.set("Canceling...")

    def update_progress(self, status_msg, pct):
        # Update GUI from thread
        self.root.after(0, lambda: self.status_var.set(status_msg))
        self.root.after(0, lambda: self.progress_var.set(pct))

    def task_finished(self, success, msg):
        self.root.after(0, lambda: self.status_var.set("Ready."))
        self.root.after(0, lambda: self.progress_var.set(0))
        if success:
            self.root.after(0, lambda: messagebox.showinfo("Success", msg))
        else:
            self.root.after(0, lambda: messagebox.showerror("Error", msg))

def main():
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
