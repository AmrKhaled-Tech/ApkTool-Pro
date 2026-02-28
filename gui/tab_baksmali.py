import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from config import PathManager

class BaksmaliTabMixin:
    def _build_baksmali_tab(self):
        """Build Baksmali/Smali tab"""
        tab = self.tab_baksmali
        tab.grid_columnconfigure(0, weight=1)
        
        # Info
        ctk.CTkLabel(
            tab,
            text="DEX Disassembly & Assembly (Advanced)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=20)
        
        # DEX to Smali section
        dex_frame = ctk.CTkFrame(tab)
        dex_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        dex_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(dex_frame, text="DEX File:", font=ctk.CTkFont(size=12)).grid(
            row=0, column=0, padx=10, pady=10
        )
        
        self.dex_file_var = ctk.StringVar()
        dex_entry = ctk.CTkEntry(
            dex_frame,
            textvariable=self.dex_file_var,
            placeholder_text="Select classes.dex...",
            height=35
        )
        dex_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        browse_dex_btn = ctk.CTkButton(
            dex_frame,
            text="🗂️ Browse",
            command=self._browse_dex,
            width=110
        )
        browse_dex_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # Action buttons for Baksmali
        baksmali_actions = ctk.CTkFrame(tab)
        baksmali_actions.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        baksmali_actions.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(
            baksmali_actions,
            text="⚙️ Baksmali (DEX → Smali)",
            command=self._baksmali_action,
            height=40
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(
            baksmali_actions,
            text="🔧 Smali (Smali → DEX)",
            command=self._smali_action,
            height=40
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def _browse_dex(self):
        """Browse for DEX file"""
        filename = filedialog.askopenfilename(
            title="Select DEX File",
            filetypes=[("DEX Files", "*.dex"), ("All Files", "*.*")]
        )
        if filename:
            self.dex_file_var.set(filename)

    def _baksmali_action(self):
        """Baksmali DEX to Smali"""
        dex_file = self.dex_file_var.get()
        import os
        if not dex_file or not os.path.exists(dex_file):
            messagebox.showerror("Error", "Please select a valid DEX file")
            return
        
        output_dir = str(PathManager.get_base_dir() / "temp" / "smali_output")
        
        self._set_processing(True)
        
        def baksmali_thread():
            success, smali_dir = self.baksmali_manager.baksmali(dex_file, output_dir)
            self.callback_queue.put(lambda: self._on_baksmali_complete(success, smali_dir))
        
        self._run_in_thread(baksmali_thread)

    def _on_baksmali_complete(self, success: bool, smali_dir: str):
        """Handle baksmali completion"""
        self._set_processing(False)
        import os
        if success:
            messagebox.showinfo("Success", f"Baksmali complete!\n\nOutput: {smali_dir}")
            # Open folder
            os.startfile(smali_dir)
        else:
            messagebox.showerror("Error", "Baksmali failed.")

    def _smali_action(self):
        """Smali to DEX"""
        # Ask for smali folder
        smali_dir = filedialog.askdirectory(title="Select Smali Folder")
        if not smali_dir:
            return
        
        output_dex = str(PathManager.get_base_dir() / "output" / "classes.dex")
        
        self._set_processing(True)
        
        def smali_thread():
            success, dex_file = self.baksmali_manager.smali(smali_dir, output_dex)
            self.callback_queue.put(lambda: self._on_smali_complete(success, dex_file))
        
        self._run_in_thread(smali_thread)

    def _on_smali_complete(self, success: bool, dex_file: str):
        """Handle smali completion"""
        self._set_processing(False)
        
        if success:
            messagebox.showinfo("Success", f"Smali complete!\n\nDEX: {dex_file}")
        else:
            messagebox.showerror("Error", "Smali failed.")
