import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from config import PathManager

class MergeTabMixin:
    def _build_merge_tab(self):
        """Build XAPK/APKS merge tab"""
        tab = self.tab_merge
        tab.grid_columnconfigure(0, weight=1)
        
        # Info label
        ctk.CTkLabel(
            tab,
            text="Merge Split APK Bundles (XAPK/APKS/APKM/ZIP) into Single APK",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=20)
        
        # Bundle selection
        bundle_frame = ctk.CTkFrame(tab)
        bundle_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        bundle_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(bundle_frame, text="Bundle File:", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, padx=10, pady=10
        )
        
        merge_entry = ctk.CTkEntry(
            bundle_frame,
            textvariable=self.merge_input_var,
            placeholder_text="Select XAPK/APKS/APKM/ZIP file...",
            height=35
        )
        merge_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        browse_bundle_btn = ctk.CTkButton(
            bundle_frame,
            text="🗂️ Browse",
            command=self._browse_bundle,
            width=110
        )
        browse_bundle_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # Options
        merge_opts_frame = ctk.CTkFrame(tab)
        merge_opts_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.auto_decompile_merged_var = ctk.BooleanVar(value=True)
        
        ctk.CTkCheckBox(
            merge_opts_frame,
            text="Auto-decompile after merge",
            variable=self.auto_decompile_merged_var
        ).pack(side="left", padx=10)
        
        # Merge button
        merge_btn = ctk.CTkButton(
            tab,
            text="🔀 MERGE TO SINGLE APK",
            command=self._merge_action,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("purple", "#6a1b9a")
        )
        merge_btn.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

    def _browse_bundle(self):
        """Browse for bundle file"""
        filename = filedialog.askopenfilename(
            title="Select Bundle File",
            filetypes=[
                ("XAPK Files", "*.xapk"),
                ("APKS Files", "*.apks"),
                ("APKM Files", "*.apkm"),
                ("ZIP Files", "*.zip"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.merge_input_var.set(filename)

    def _merge_action(self):
        """Merge bundle to single APK"""
        bundle = self.merge_input_var.get()
        import os
        if not bundle or not os.path.exists(bundle):
            messagebox.showerror("Error", "Please select a valid bundle file")
            return
        
        bundle_name = Path(bundle).stem
        output_apk = str(PathManager.get_base_dir() / "output" / f"{bundle_name}_merged.apk")
        
        self._set_processing(True)
        
        def merge_thread():
            success, merged_apk = self.apkeditor_manager.merge_bundle(bundle, output_apk)
            self.callback_queue.put(lambda: self._on_merge_complete(success, merged_apk))
        
        self._run_in_thread(merge_thread)

    def _on_merge_complete(self, success: bool, merged_apk: str):
        """Handle merge completion"""
        self._set_processing(False)
        
        if success:
            self.status_label.configure(text=f"✓ Merged: {Path(merged_apk).name}")
            
            if self.auto_decompile_merged_var.get():
                # Auto-decompile
                self.apk_path_var.set(merged_apk)
                messagebox.showinfo(
                    "Success",
                    f"Merge complete!\n\n{merged_apk}\n\nAuto-decompiling..."
                )
                self.after(500, self._decompile_action)
            else:
                messagebox.showinfo("Success", f"Merge complete!\n\n{merged_apk}")
        else:
            messagebox.showerror("Error", "Merge failed. Check the log.")
