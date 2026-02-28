import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from dialogs import SmartTaskDialog

class DecompileTabMixin:
    def _build_decompile_tab(self):
        """Build decompile tab"""
        tab = self.tab_decompile
        tab.grid_columnconfigure(0, weight=1)
        
        # APK selection frame
        apk_frame = ctk.CTkFrame(tab)
        apk_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        apk_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(apk_frame, text="APK File:", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, padx=10, pady=10
        )
        
        self.apk_entry = ctk.CTkEntry(
            apk_frame,
            textvariable=self.apk_path_var,
            placeholder_text="Select APK file...",
            height=35
        )
        self.apk_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # DND Support is handled in main app logic or can be re-bound here if needed, 
        # but self.apk_entry is now available.
        try:
            from tkinterdnd2 import DND_FILES
            self.apk_entry.drop_target_register(DND_FILES)
            self.apk_entry.dnd_bind('<<Drop>>', lambda e: self._on_drop(e, 'apk'))
        except:
            pass
        
        browse_btn = ctk.CTkButton(
            apk_frame,
            text="🗂️ Browse",
            command=self._browse_apk,
            width=110
        )
        browse_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # Decompiler selection
        decompiler_frame = ctk.CTkFrame(tab)
        decompiler_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(decompiler_frame, text="Decompiler:", font=ctk.CTkFont(size=13)).pack(
            side="left", padx=10
        )
        
        # self.var_decompiler is initialized in main app
        
        ctk.CTkRadioButton(
            decompiler_frame,
            text="Apktool (Recommended)",
            variable=self.var_decompiler,
            value="apktool"
        ).pack(side="left", padx=20)
        
        ctk.CTkRadioButton(
            decompiler_frame,
            text="APKEditor (for bundles)",
            variable=self.var_decompiler,
            value="apkeditor"
        ).pack(side="left", padx=20)
        
        # Options
        options_frame = ctk.CTkFrame(tab)
        options_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        # Shared vars initialized in main app        
        ctk.CTkCheckBox(
            options_frame,
            text="Decode Resources",
            variable=self.var_decode_resources
        ).pack(side="left", padx=10)
        
        ctk.CTkCheckBox(
            options_frame,
            text="Decode Sources (Smali)",
            variable=self.var_decode_sources
        ).pack(side="left", padx=10)
        
        ctk.CTkCheckBox(
            options_frame,
            text="Clear Framework Before",
            variable=self.var_clear_framework
        ).pack(side="left", padx=10)
        
        # Decompile button
        self.decompile_btn = ctk.CTkButton(
            tab,
            text="📦 DECOMPILE APK",
            command=self._decompile_action,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("blue", "#1758a7")
        )
        self.decompile_btn.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

    def _browse_apk(self):
        """Browse for APK file"""
        filename = filedialog.askopenfilename(
            title="Select APK File",
            filetypes=[
                ("APK Files", "*.apk"),
                ("All Files", "*.*")
            ]
        )
        if filename:
            self.apk_path_var.set(filename)

    def _decompile_action(self):
        """Decompile APK with Smart Dialog"""
        apk = self.apk_path_var.get()
        import os
        if not apk or not os.path.exists(apk):
            self.log_message("Please select a valid APK file", "error")
            messagebox.showerror("Error", "Please select a valid APK file")
            return
        
        # Update settings from UI
        self.settings.decode_resources = self.var_decode_resources.get()
        self.settings.decode_sources = self.var_decode_sources.get()
        
        # Clear framework if requested
        if self.var_clear_framework.get():
            self.framework_manager.clear_framework()
        
        decompiler = self.var_decompiler.get()
        
        def decompile_task(controller):
            controller.update_status(f"Initializing {decompiler}...")
            controller.update_progress(0, "indeterminate")
            
            # Select Manager
            manager = self.apktool_manager if decompiler == "apktool" else self.apkeditor_manager
            
            # Swap Logger & Inject Cancellation
            original_logger = manager.logger
            manager.logger = lambda msg, level="info": controller.log(msg, level)
            manager.cancellation_check = lambda: controller.cancelled
            
            try:
                controller.log(f"Starting decompilation of {Path(apk).name}...", "info")
                success, workspace = manager.decompile(apk)
                
                if success:
                    controller.update_progress(100, "determinate")
                    controller.update_status("✓ Decompilation Successful!")
                    return workspace
                else:
                    if controller.cancelled:
                         raise Exception("Operation cancelled")
                    raise Exception("Decompilation process returned failure")
                    
            except Exception as e:
                raise e
            finally:
                # Restore Logger & Clear Cancellation
                manager.logger = original_logger
                manager.cancellation_check = None

        def on_complete(success, result):
            if success:
                self.current_project = result
                self.project_path_var.set(result)
                self.status_label.configure(text=f"✓ Decompiled: {Path(result).name}")
                
                # Ask to open
                if messagebox.askyesno("Success", f"Decompilation Complete!\n\nWorkspace: {result}\n\nOpen project folder now?"):
                    self._open_project_folder()
            else:
                self.status_label.configure(text="Decompilation failed")
                if "cancelled" not in str(result).lower():
                     messagebox.showerror("Error", f"Decompilation failed:\n{result}")

        SmartTaskDialog(self, "Decompiling APK", decompile_task, on_complete=on_complete, logger_callback=self.log_message)
