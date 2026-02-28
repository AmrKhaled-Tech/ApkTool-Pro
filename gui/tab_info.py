import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import os

class InfoTabMixin:
    def _build_info_tab(self):
        """Build APK info tab"""
        tab = self.tab_info
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)
        
        # APK selection for info
        info_frame = ctk.CTkFrame(tab)
        info_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        info_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(info_frame, text="APK File:", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, padx=10, pady=10
        )
        
        self.info_apk_var = ctk.StringVar()
        info_entry = ctk.CTkEntry(
            info_frame,
            textvariable=self.info_apk_var,
            placeholder_text="Select APK to analyze...",
            height=35
        )
        info_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        browse_info_btn = ctk.CTkButton(
            info_frame,
            text="🗂️ Browse",
            command=self._browse_info_apk,
            width=110
        )
        browse_info_btn.grid(row=0, column=2, padx=10, pady=10)
        
        analyze_btn = ctk.CTkButton(
            info_frame,
            text="ℹ️ Analyze",
            command=self._analyze_apk,
            width=110
        )
        analyze_btn.grid(row=0, column=3, padx=10, pady=10)
        
        # Info display (scrollable)
        self.info_display = ctk.CTkTextbox(
            tab,
            wrap="word",
            font=ctk.CTkFont(family="Cascadia Code", size=11)
        )
        self.info_display.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

    def _browse_info_apk(self):
        """Browse for APK to analyze"""
        filename = filedialog.askopenfilename(
            title="Select APK to Analyze",
            filetypes=[("APK Files", "*.apk")]
        )
        if filename:
            self.info_apk_var.set(filename)

    def _analyze_apk(self):
        """Analyze APK and display info"""
        apk = self.info_apk_var.get()
        import os
        if not apk or not os.path.exists(apk):
            messagebox.showerror("Error", "Please select a valid APK file")
            return
        
        self.info_display.delete("1.0", "end")
        self.info_display.insert("1.0", "Analyzing APK & Verifying Signature...\n")
        
        def analyze_thread():
            # 1. AAPT Info
            info = self.aapt_manager.get_apk_info(apk)
            
            # 2. Signature Verification
            cert_info = self._verify_signature(apk)
            
            self.callback_queue.put(lambda: self._display_apk_info(info, cert_info))
        
        self._run_in_thread(analyze_thread)

    def _verify_signature(self, apk_path: str) -> str:
        """Run apksigner verify --print-certs -v"""
        try:
            # We need to get apksigner path from manager (or config)
            # Accessing via self.signing_manager
            signer_path = self.signing_manager._get_signer_path()
            if not signer_path:
                return "apksigner not found."

            import subprocess
            cmd = ["java", "-jar", str(signer_path), "verify", "--print-certs", "-v", apk_path]
            
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            return result.stdout + "\n" + result.stderr
        except Exception as e:
            return f"Error verifying signature: {e}"

    def _display_apk_info(self, info: dict, cert_info: str):
        """Display APK information"""
        self.info_display.delete("1.0", "end")
        
        output = []
        output.append("=" * 60)
        output.append("📦 APK MANIFEST INFO")
        output.append("=" * 60)
        
        if not info:
             output.append("Failed to read manifest info (AAPT error).")
        else:
            output.append(f"Package : {info.get('package_name', 'N/A')}")
            output.append(f"Ver Code : {info.get('version_code', 'N/A')}")
            output.append(f"Ver Name : {info.get('version_name', 'N/A')}")
            output.append(f"Min SDK :  {info.get('min_sdk', 'N/A')}")
            output.append(f"Tgt SDK :  {info.get('target_sdk', 'N/A')}")
            
            if 'native_code' in info:
                output.append(f"ABI : {', '.join(info['native_code'])}")
            
            if 'permissions' in info:
                output.append("")
                output.append(f"Permissions ({len(info['permissions'])}):")
                for perm in info['permissions'][:10]:
                    output.append(f"  - {perm}")
                if len(info['permissions']) > 10:
                    output.append(f"  ... {len(info['permissions']) - 10} more")

        output.append("")
        output.append("=" * 60)
        output.append("🔐 SIGNATURE VERIFICATION")
        output.append("=" * 60)
        output.append(cert_info)
        
        self.info_display.insert("1.0", "\n".join(output))
