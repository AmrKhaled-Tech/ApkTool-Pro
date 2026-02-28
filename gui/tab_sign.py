import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
from dialogs import SmartTaskDialog
from config import PathManager

class SignTabMixin:
    def _build_sign_tab(self):
        """Build sign & zipalign tab"""
        tab = self.tab_sign
        tab.grid_columnconfigure(0, weight=1)
        
        # APK selection for signing
        sign_frame = ctk.CTkFrame(tab)
        sign_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        sign_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(sign_frame, text="APK to Sign:", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, padx=10, pady=10
        )
        
        self.sign_apk_var = ctk.StringVar()
        sign_entry = ctk.CTkEntry(
            sign_frame,
            textvariable=self.sign_apk_var,
            placeholder_text="Select APK to sign...",
            height=35
        )
        sign_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        browse_sign_btn = ctk.CTkButton(
            sign_frame,
            text="🗂️ Browse",
            command=self._browse_sign_apk,
            width=110
        )
        browse_sign_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # Zipalign options
        zipalign_frame = ctk.CTkFrame(tab)
        zipalign_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        # Shared vars initialized in main app
        
        ctk.CTkCheckBox(
            zipalign_frame,
            text="Zipalign APK",
            variable=self.var_auto_zipalign
        ).pack(side="left", padx=10)
        
        ctk.CTkCheckBox(
            zipalign_frame,
            text="Zipalign BEFORE Signing (Recommended)",
            variable=self.var_zipalign_before
        ).pack(side="left", padx=10)
        
        # Signing options
        signing_frame = ctk.CTkFrame(tab)
        signing_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(signing_frame, text="Signature Schemes:", font=ctk.CTkFont(size=12)).pack(
            side="left", padx=10
        )
        
        # Shared vars
        
        ctk.CTkCheckBox(signing_frame, text="v1", variable=self.var_v1).pack(side="left", padx=5)
        ctk.CTkCheckBox(signing_frame, text="v2", variable=self.var_v2).pack(side="left", padx=5)
        ctk.CTkCheckBox(signing_frame, text="v3", variable=self.var_v3).pack(side="left", padx=5)
        
        # Action buttons
        action_frame = ctk.CTkFrame(tab)
        action_frame.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        action_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(
            action_frame,
            text="📏 Zipalign",
            command=self._zipalign_only_action,
            height=45,
            font=ctk.CTkFont(size=14)
        ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(
            action_frame,
            text="✓ Sign APK",
            command=self._sign_action,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=("orange", "#d84315")
        ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def _browse_sign_apk(self):
        """Browse for APK to sign"""
        filename = filedialog.askopenfilename(
            title="Select APK to Sign",
            filetypes=[("APK Files", "*.apk")]
        )
        if filename:
            self.sign_apk_var.set(filename)

    def _sign_action(self):
        """Sign APK with Smart Dialog"""
        apk = self.sign_apk_var.get()
        import os
        if not apk or not os.path.exists(apk):
            messagebox.showerror("Error", "Please select a valid APK file")
            return
        
        # Update settings
        self.settings.v1_signing = self.var_v1.get()
        self.settings.v2_signing = self.var_v2.get()
        self.settings.v3_signing = self.var_v3.get()
        
        # Check Zipalign options
        do_zipalign = self.var_auto_zipalign.get()
        zipalign_before = self.var_zipalign_before.get()
        
        def sign_task(controller):
            controller.update_status("Initializing signing process...")
            controller.update_progress(0, "indeterminate")
            
            # Swap Loggers
            original_sign_logger = self.signing_manager.logger
            original_zip_logger = self.zipalign_manager.logger
            
            self.signing_manager.logger = lambda msg, level="info": controller.log(msg, level)
            self.zipalign_manager.logger = lambda msg, level="info": controller.log(msg, level)
            
            final_apk = apk
            
            try:
                # 1. Zipalign BEFORE
                if do_zipalign and zipalign_before:
                    controller.update_status("Zipaligning before sign...")
                    controller.log("Starting Zipalign...", "info")
                    success, aligned_apk = self.zipalign_manager.zipalign(apk)
                    if success:
                        final_apk = aligned_apk
                        controller.log("✓ Zipalign successful", "success")
                    else:
                        controller.log("⚠ Zipalign failed, using original APK", "warning")
                        
                # 2. Sign
                controller.update_status("Signing APK...")
                controller.log(f"Signing {Path(final_apk).name}...", "info")
                success, signed_apk = self.signing_manager.sign(final_apk)
                
                if not success:
                    # s_signed_apk now contains the error log if failed
                    raise Exception(f"Signing failed:\n{signed_apk}")
                    
                controller.log("✓ Signing successful", "success")
                controller.update_progress(80)
                
                # 3. Zipalign AFTER
                if do_zipalign and not zipalign_before:
                    controller.update_status("Zipaligning after sign...")
                    success2, final_signed = self.zipalign_manager.zipalign(signed_apk)
                    if success2:
                        signed_apk = final_signed
                        controller.log("✓ Zipalign after sign successful", "success")
                
                controller.update_progress(100, "determinate")
                
                # Copy to output
                import shutil
                output_dir = PathManager.get_base_dir() / "output"
                output_dir.mkdir(parents=True, exist_ok=True)
                
                dest_path = output_dir / Path(signed_apk).name
                shutil.copy2(signed_apk, dest_path)
                signed_apk = str(dest_path)
                controller.log(f"✓ Saved to output: {dest_path.name}", "success")
                
                controller.update_status("✓ Process Complete!")
                return signed_apk
                
            except Exception as e:
                raise e
            finally:
                # Restore loggers
                self.signing_manager.logger = original_sign_logger
                self.zipalign_manager.logger = original_zip_logger

        def on_complete(success, result):
            if success:
                self.status_label.configure(text=f"✓ Signed: {Path(result).name}")
                messagebox.showinfo("Success", f"Signing complete!\n\nSigned APK: {result}")
            else:
                messagebox.showerror("Error", f"Signing failed:\n{result}")

        SmartTaskDialog(self, "Signing APK", sign_task, on_complete=on_complete, logger_callback=self.log_message)

    def _zipalign_only_action(self):
        """Zipalign only with Smart Dialog"""
        apk = self.sign_apk_var.get()
        import os
        if not apk or not os.path.exists(apk):
            messagebox.showerror("Error", "Please select a valid APK file")
            return
        
        def zipalign_task(controller):
            controller.update_status("Zipaligning APK...")
            controller.update_progress(0, "indeterminate")
            
            # Swap Logger
            original_logger = self.zipalign_manager.logger
            self.zipalign_manager.logger = lambda msg, level="info": controller.log(msg, level)
            
            try:
                controller.log(f"Zipaligning {Path(apk).name}...", "info")
                success, aligned_apk = self.zipalign_manager.zipalign(apk)
                
                if success:
                    # Copy to output
                    import shutil
                    output_dir = PathManager.get_base_dir() / "output"
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    dest_path = output_dir / Path(aligned_apk).name
                    shutil.copy2(aligned_apk, dest_path)
                    aligned_apk = str(dest_path)
                    controller.log(f"✓ Saved to output: {dest_path.name}", "success")

                    controller.update_progress(100, "determinate")
                    controller.update_status("✓ Zipalign Successful!")
                    return aligned_apk
                else:
                    raise Exception("Zipalign failed")
            except Exception as e:
                raise e
            finally:
                self.zipalign_manager.logger = original_logger

        def on_complete(success, result):
            if success:
                self.status_label.configure(text=f"✓ Zipaligned: {Path(result).name}")
                messagebox.showinfo("Success", f"Zipalign complete!\n\n{result}")
            else:
                messagebox.showerror("Error", f"Zipalign failed:\n{result}")

        SmartTaskDialog(self, "Zipaligning APK", zipalign_task, on_complete=on_complete, logger_callback=self.log_message)
