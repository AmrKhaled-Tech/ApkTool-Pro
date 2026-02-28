import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from dialogs import SmartTaskDialog
from dialogs import SmartTaskDialog
from managers import DecompilerDetector
from config import PathManager

class CompileTabMixin:
    def _build_compile_tab(self):
        """Build compile tab"""
        tab = self.tab_compile
        tab.grid_columnconfigure(0, weight=1)
        
        # Project selection
        project_frame = ctk.CTkFrame(tab)
        project_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        project_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(project_frame, text="Project Folder:", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, padx=10, pady=10
        )
        
        project_entry = ctk.CTkEntry(
            project_frame,
            textvariable=self.project_path_var,
            placeholder_text="Select decompiled project folder...",
            height=35
        )
        project_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        browse_project_btn = ctk.CTkButton(
            project_frame,
            text="🗂️ Browse",
            command=self._browse_project,
            width=110
        )
        browse_project_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # Auto-detect decompiler info
        self.decompiler_info_label = ctk.CTkLabel(
            tab,
            text="Decompiler: Not detected",
            font=ctk.CTkFont(size=12)
        )
        self.decompiler_info_label.grid(row=1, column=0, padx=20, pady=5)
        
        # Compile options
        compile_opts_frame = ctk.CTkFrame(tab)
        compile_opts_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        # self.var_use_aapt2 initialized in main app
        
        ctk.CTkCheckBox(
            compile_opts_frame,
            text="Use AAPT2 (Disable for Apktool 2.12+)",
            variable=self.var_use_aapt2
        ).pack(side="left", padx=10)
        
        # Compile button
        self.compile_btn = ctk.CTkButton(
            tab,
            text="🔨 COMPILE APK",
            command=self._compile_action,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("green", "#2d7d32")
        )
        self.compile_btn.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        
        # Quick actions
        quick_frame = ctk.CTkFrame(tab)
        quick_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        quick_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        ctk.CTkButton(
            quick_frame,
            text="📂 Open Project",
            command=self._open_project_folder,
            height=35
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(
            quick_frame,
            text="📜 AndroidManifest.xml",
            command=self._open_manifest,
            height=35
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(
            quick_frame,
            text="📄 apktool.yml",
            command=self._open_apktool_yml,
            height=35
        ).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    def _browse_project(self):
        """Browse for project folder"""
        folder = filedialog.askdirectory(title="Select Decompiled Project Folder")
        if folder:
            self.project_path_var.set(folder)
            # Auto-detect decompiler
            decompiler = DecompilerDetector.detect(Path(folder))
            self.decompiler_info_label.configure(
                text=f"Decompiler: {decompiler.upper()} detected"
            )
            self.current_project = folder

    def _compile_action(self):
        """Compile project with Smart Dialog"""
        project = self.project_path_var.get()
        import os
        if not project or not os.path.exists(project):
            self.log_message("Please select a valid project folder", "error")
            messagebox.showerror("Error", "Please select a valid decompiled project folder")
            return
        
        # Update settings
        self.settings.use_aapt2 = self.var_use_aapt2.get()
        
        # Auto-detect decompiler
        decompiler = DecompilerDetector.detect(Path(project))
        
        def compile_task(controller):
            controller.update_status(f"Compiling with {decompiler}...")
            controller.update_progress(0, "indeterminate")
            
            # Select Manager
            manager = self.apktool_manager if decompiler == "apktool" else self.apkeditor_manager
            
            # Swap Loggers & Inject Cancellation
            original_logger = manager.logger
            manager.logger = lambda msg, level="info": controller.log(msg, level)
            manager.cancellation_check = lambda: controller.cancelled
            
            # For Auto-Sign later
            zip_logger = self.zipalign_manager.logger
            sign_logger = self.signing_manager.logger
            
            self.zipalign_manager.cancellation_check = lambda: controller.cancelled
            self.signing_manager.cancellation_check = lambda: controller.cancelled
            
            try:
                # 1. Compilation
                controller.log(f"Building project: {Path(project).name}", "info")
                success, apk_path = manager.compile(project)
                
                if controller.cancelled: raise Exception("Cancelled")
                
                if not success or not apk_path:
                    raise Exception("Build failed")
                
                controller.log("✓ Build successful!", "success")
                controller.update_progress(50)
                
                final_apk = apk_path
                
                # 2. Auto-Sign Workflow (Integrated)
                if self.settings.auto_sign_after_compile:
                    controller.update_status("Auto-signing built APK...")
                    controller.log("Starting auto-sign process...", "info")
                    
                    # Swap other loggers
                    self.zipalign_manager.logger = lambda msg, level="info": controller.log(msg, level)
                    self.signing_manager.logger = lambda msg, level="info": controller.log(msg, level)
                    
                    # Zipalign
                    if self.settings.auto_zipalign and self.settings.zipalign_before_sign:
                        controller.update_status("Zipaligning...")
                        z_success, z_apk = self.zipalign_manager.zipalign(final_apk)
                        if z_success:
                            final_apk = z_apk
                        else:
                            controller.log("⚠ Zipalign failed, proceeding with original", "warning")
                    
                    if controller.cancelled: raise Exception("Cancelled")

                    # Sign
                    controller.update_status("Signing with testkey...")
                    s_success, s_apk = self.signing_manager.sign(final_apk)
                    
                    if s_success:
                        final_apk = s_apk
                        controller.log("✓ Signing complete", "success")
                    else:
                        controller.log("✗ Signing failed", "error")
                        # Raise exception with the error log (s_apk contains log on failure now)
                        raise Exception(f"Signing Failed:\n{s_apk}")

                # Copy to output folder
                import shutil
                output_dir = PathManager.get_base_dir() / "output"
                output_dir.mkdir(parents=True, exist_ok=True)
                
                dest_path = output_dir / Path(final_apk).name
                shutil.copy2(final_apk, dest_path)
                final_apk = str(dest_path)
                controller.log(f"✓ Saved to output: {dest_path.name}", "success")
                        
                controller.update_progress(100, "determinate")
                controller.update_status("✓ All Operations Complete!")
                return final_apk

            except Exception as e:
                raise e
            finally:
                # Restore All Loggers & Clear Cancellation
                manager.logger = original_logger
                manager.cancellation_check = None
                
                self.zipalign_manager.logger = zip_logger
                self.zipalign_manager.cancellation_check = None
                
                self.signing_manager.logger = sign_logger
                self.signing_manager.cancellation_check = None

        def on_complete(success, result):
            if success:
                self.built_apk = result
                self.status_label.configure(text=f"✓ Built: {Path(result).name}")
                
                if messagebox.askyesno("Success", f"Process Complete!\n\nAPK: {result}\n\nOpen output folder?"):
                    self._open_output_folder()
            else:
                self.status_label.configure(text="Compilation failed")
                if "cancelled" not in str(result).lower():
                    messagebox.showerror("Error", f"Compilation/Signing failed:\n{result}")

        SmartTaskDialog(self, "Compiling APK", compile_task, on_complete=on_complete, logger_callback=self.log_message)
