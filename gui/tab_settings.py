import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path
from config import PathManager
from gui.dialog_keystore import KeystoreCreatorDialog

class SettingsTabMixin:
    def _build_settings_tab(self):
        """Build professional settings tab"""
        tab = self.tab_settings
        
        # Main Scrollable Container
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Helper to create section frames
        def create_section(title, icon="⚙️"):
            frame = ctk.CTkFrame(scroll)
            frame.pack(fill="x", padx=10, pady=10)
            
            header = ctk.CTkFrame(frame, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(
                header, 
                text=f"{icon}  {title}", 
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(side="left")
            
            content = ctk.CTkFrame(frame, fg_color="transparent")
            content.pack(fill="x", padx=10, pady=10)
            return content

        # ====================================================================
        # 1. JAVA ENVIRONMENT
        # ====================================================================
        java_frame = create_section("Java Environment", "☕")
        java_frame.grid_columnconfigure(1, weight=1)
        
        # Java Path
        ctk.CTkLabel(java_frame, text="Java Path (bin/java):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkEntry(java_frame, textvariable=self.var_java_path).grid(row=0, column=1, sticky="ew", padx=5)
        ctk.CTkButton(java_frame, text="📂", width=40, command=self._browse_java).grid(row=0, column=2, padx=5)
        
        # Heap Size
        ctk.CTkLabel(java_frame, text="Heap Size (MB):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        heap_slider_frame = ctk.CTkFrame(java_frame, fg_color="transparent")
        heap_slider_frame.grid(row=1, column=1, columnspan=2, sticky="ew")
        
        self.heap_label = ctk.CTkLabel(heap_slider_frame, text=f"{self.var_heap_size.get()} MB", width=60)
        self.heap_label.pack(side="right")
        
        slider = ctk.CTkSlider(
            heap_slider_frame, 
            from_=512, to=8192, 
            number_of_steps=15,
            variable=self.var_heap_size,
            command=lambda v: self.heap_label.configure(text=f"{int(v)} MB")
        )
        slider.pack(side="left", fill="x", expand=True, padx=5)

        # Suppress Warnings
        ctk.CTkCheckBox(
            java_frame,
            text="Suppress Java/JVM Warnings",
            variable=self.var_suppress_java_warnings
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # ====================================================================
        # 2. TOOLS & PATHS
        # ====================================================================
        tools_frame = create_section("External Tools Paths", "🛠️")
        tools_frame.grid_columnconfigure(1, weight=1)
        
        # Custom Apktool Version Selection
        ctk.CTkLabel(tools_frame, text="Apktool Version:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        # Container for Switch + Combo
        apk_sel_frame = ctk.CTkFrame(tools_frame, fg_color="transparent")
        apk_sel_frame.grid(row=0, column=1, columnspan=2, sticky="ew")
        
        self.switch_custom_apktool = ctk.CTkSwitch(
            apk_sel_frame, 
            text="Use Custom Version", 
            variable=self.var_use_custom_apktool,
            command=self._toggle_apktool_mode
        )
        self.switch_custom_apktool.pack(side="left", padx=5)
        
        self.combo_apktool = ctk.CTkComboBox(
            apk_sel_frame,
            values=["Default"],
            variable=self.var_custom_apktool_path,
            width=250
        )
        self.combo_apktool.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(apk_sel_frame, text="📂 Add Jar", width=80, command=self._add_custom_apktool).pack(side="left", padx=5)
        
        # Custom AAPT Version Selection
        ctk.CTkLabel(tools_frame, text="AAPT Version:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        aapt_sel_frame = ctk.CTkFrame(tools_frame, fg_color="transparent")
        aapt_sel_frame.grid(row=1, column=1, columnspan=2, sticky="ew")
        
        self.switch_custom_aapt = ctk.CTkSwitch(
            aapt_sel_frame, 
            text="Use Custom Version", 
            variable=self.var_use_custom_aapt,
            command=self._toggle_aapt_mode
        )
        self.switch_custom_aapt.pack(side="left", padx=5)
        
        self.combo_aapt = ctk.CTkComboBox(
            aapt_sel_frame,
            values=["Default"],
            variable=self.var_custom_aapt_path,
            width=250
        )
        self.combo_aapt.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(aapt_sel_frame, text="📂 Add Exe", width=80, command=self._add_custom_aapt).pack(side="left", padx=5)
        
        # Custom AAPT2 Version Selection
        ctk.CTkLabel(tools_frame, text="AAPT2 Version:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        aapt2_sel_frame = ctk.CTkFrame(tools_frame, fg_color="transparent")
        aapt2_sel_frame.grid(row=2, column=1, columnspan=2, sticky="ew")
        
        self.switch_custom_aapt2 = ctk.CTkSwitch(
            aapt2_sel_frame, 
            text="Use Custom Version", 
            variable=self.var_use_custom_aapt2,
            command=self._toggle_aapt2_mode
        )
        self.switch_custom_aapt2.pack(side="left", padx=5)
        
        self.combo_aapt2 = ctk.CTkComboBox(
            aapt2_sel_frame,
            values=["Default"],
            variable=self.var_custom_aapt2_path,
            width=250
        )
        self.combo_aapt2.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(aapt2_sel_frame, text="📂 Add Exe", width=80, command=self._add_custom_aapt2).pack(side="left", padx=5)
        
        # Apksigner Path
        ctk.CTkLabel(tools_frame, text="Custom Apksigner (.jar):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkEntry(tools_frame, textvariable=self.var_apksigner_path, placeholder_text="Default (Internal)").grid(row=3, column=1, sticky="ew", padx=5)
        ctk.CTkButton(tools_frame, text="📂", width=40, command=lambda: self._browse_file(self.var_apksigner_path)).grid(row=3, column=2, padx=5)

        # Refresh combo values
        self._refresh_apktool_list()
        self._toggle_apktool_mode()
        self._refresh_aapt_list()
        self._toggle_aapt_mode()
        self._refresh_aapt2_list()
        self._toggle_aapt2_mode()

        # ====================================================================
        # 3. COMPILATION & FRAMEWORK
        # ====================================================================
        comp_frame = create_section("Detailed Configuration", "⚙️")
        
        # Framework Actions
        f_actions = ctk.CTkFrame(comp_frame, fg_color="transparent")
        f_actions.pack(fill="x", pady=5)
        
        ctk.CTkButton(f_actions, text="📥 Install Framework", command=self._install_framework).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(f_actions, text="🗑️ Clear Framework", command=self._clear_framework, fg_color="red").pack(side="left", padx=5, expand=True, fill="x")
        
        # General Checkboxes
        checks_frame = ctk.CTkFrame(comp_frame, fg_color="transparent")
        checks_frame.pack(fill="x", pady=10)
        
        ctk.CTkCheckBox(checks_frame, text="Use AAPT2", variable=self.var_use_aapt2).pack(side="left", padx=10)
        ctk.CTkCheckBox(checks_frame, text="Decode Resources", variable=self.var_decode_resources).pack(side="left", padx=10)
        ctk.CTkCheckBox(checks_frame, text="Decode Sources", variable=self.var_decode_sources).pack(side="left", padx=10)

        # Compression Level
        comp_lvl_frame = ctk.CTkFrame(comp_frame, fg_color="transparent")
        comp_lvl_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(comp_lvl_frame, text="Compression Level:").pack(side="left", padx=5)
        self.comp_label = ctk.CTkLabel(comp_lvl_frame, text=str(self.var_compression.get()))
        self.comp_label.pack(side="right", padx=5)
        
        ctk.CTkSlider(
            comp_lvl_frame, 
            from_=0, to=9, 
            number_of_steps=9,
            variable=self.var_compression,
            command=lambda v: self.comp_label.configure(text=str(int(v)))
        ).pack(side="left", fill="x", expand=True, padx=10)

        # ====================================================================
        # 4. SIGNING CONFIGURATION
        # ====================================================================
        sign_frame = create_section("Signing Configuration", "🔐")
        sign_frame.grid_columnconfigure(1, weight=1)
        
        # Automation switches
        auto_frame = ctk.CTkFrame(sign_frame, fg_color="transparent")
        auto_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=5)
        
        ctk.CTkCheckBox(auto_frame, text="Auto-Sign after Compile", variable=self.var_auto_sign).pack(side="left", padx=10)
        ctk.CTkCheckBox(auto_frame, text="Auto-Zipalign", variable=self.var_auto_zipalign).pack(side="left", padx=10)
        
        # Keystore Mode
        ctk.CTkSwitch(
            sign_frame, 
            text="Use Custom Keystore", 
            variable=self.var_use_custom_keystore,
            command=self._toggle_keystore_fields
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=10)
        
        # Keystore Fields (Hidden/Disabled logic handled by command)
        self.ks_fields_frame = ctk.CTkFrame(sign_frame)
        self.ks_fields_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        self.ks_fields_frame.grid_columnconfigure(1, weight=1)
        
        # Keystore Fields (Hidden/Disabled logic handled by command)
        self.ks_fields_frame = ctk.CTkFrame(sign_frame)
        self.ks_fields_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        self.ks_fields_frame.grid_columnconfigure(1, weight=1)
        
        # Keystore Selection (Combo + Create)
        keystore_sel_frame = ctk.CTkFrame(self.ks_fields_frame, fg_color="transparent")
        keystore_sel_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=5)
        
        ctk.CTkLabel(keystore_sel_frame, text="Keystore File:").pack(side="left", padx=5)
        
        self.combo_keystore = ctk.CTkComboBox(
            keystore_sel_frame,
            values=["Select or Create..."],
            variable=self.var_keystore_path,
            width=250
        )
        self.combo_keystore.pack(side="left", padx=5, fill="x", expand=True)
        
        ctk.CTkButton(
            keystore_sel_frame, 
            text="✨ Create New", 
            width=100,
            fg_color="green",
            command=self._open_keystore_creator
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            keystore_sel_frame, 
            text="📂 Browse", 
            width=80,
            command=lambda: self._browse_file(self.var_keystore_path)
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(self.ks_fields_frame, text="Keystore Pass:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.entry_ks_pass = ctk.CTkEntry(self.ks_fields_frame, textvariable=self.var_keystore_pass, show="*")
        self.entry_ks_pass.grid(row=1, column=1, sticky="ew", padx=5)
        
        ctk.CTkLabel(self.ks_fields_frame, text="Key Alias:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.entry_alias = ctk.CTkEntry(self.ks_fields_frame, textvariable=self.var_key_alias)
        self.entry_alias.grid(row=2, column=1, sticky="ew", padx=5)
        
        ctk.CTkLabel(self.ks_fields_frame, text="Key Password:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.entry_key_pass = ctk.CTkEntry(self.ks_fields_frame, textvariable=self.var_key_pass, show="*")
        self.entry_key_pass.grid(row=3, column=1, sticky="ew", padx=5)
        
        # Signature Schemes
        schemes_frame = ctk.CTkFrame(sign_frame, fg_color="transparent")
        schemes_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)
        ctk.CTkLabel(schemes_frame, text="Schemes:").pack(side="left", padx=5)
        ctk.CTkCheckBox(schemes_frame, text="v1", variable=self.var_v1).pack(side="left", padx=5)
        ctk.CTkCheckBox(schemes_frame, text="v2", variable=self.var_v2).pack(side="left", padx=5)
        ctk.CTkCheckBox(schemes_frame, text="v3", variable=self.var_v3).pack(side="left", padx=5)
        
        # Initialize UI state
        self._refresh_keystore_list()
        self._toggle_keystore_fields()

        # ====================================================================
        # 5. BOTTOM ACTIONS
        # ====================================================================
        action_frame = ctk.CTkFrame(tab, fg_color="transparent")
        action_frame.pack(fill="x", side="bottom", padx=20, pady=10)
        
        ctk.CTkButton(
            action_frame,
            text="💾 Save All Settings",
            command=self._save_settings,
            height=40,
            fg_color=("green", "#2d7d32"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x")

    def _browse_java(self):
        filename = filedialog.askopenfilename(title="Select Java Executable", filetypes=[("Executables", "*.exe"), ("All Files", "*.*")])
        if filename: self.var_java_path.set(filename)

    def _browse_file(self, var):
        filename = filedialog.askopenfilename(title="Select File", filetypes=[("All Files", "*.*")])
        if filename: var.set(filename)

    def _toggle_keystore_fields(self):
        state = "normal" if self.var_use_custom_keystore.get() else "disabled"
        self.combo_keystore.configure(state=state)
        self.entry_ks_pass.configure(state=state)
        self.entry_alias.configure(state=state)
        self.entry_key_pass.configure(state=state)
        
    def _open_keystore_creator(self):
        """Open the Keystore Creator Dialog"""
        def on_created(path, password, alias):
            # Refresh list
            self._refresh_keystore_list()
            # Select new key
            self.var_keystore_path.set(str(path))
            # Smart Profile: Load credentials when path changes
            self.var_keystore_path.trace_add('write', self._on_keystore_path_change)

            self.var_keystore_pass.set(password) # Use same pass by default
            self.var_key_alias.set(alias)
            self.var_key_pass.set(password) # Use same pass by default
            
            # Save Profile immediately
            self._save_keystore_profile(str(path), password, alias, password)
            self._save_settings() # Persist to disk
            
            messagebox.showinfo("Keystore Created", 
                "Keystore created and selected!\n\nCredentials saved to profile.")

        KeystoreCreatorDialog(self.tab_settings, on_create_callback=on_created)

    def _refresh_keystore_list(self):
        """Refresh list of keystores in keys/ directory"""
        keys_dir = PathManager.get_base_dir() / "keys"
        keys_dir.mkdir(parents=True, exist_ok=True)
        
        # Find .jks and .keystore files
        keys = [f.name for f in keys_dir.glob("*.jks")] + [f.name for f in keys_dir.glob("*.keystore")]
        
        if not keys:
            values = ["No keys found (Create New)"]
        else:
            values = keys
            
        self.combo_keystore.configure(values=values)
        
        # Smart selection logic:
        # If current path is in keys/ dir, just show filename in combo
        # If current path is absolute elsewhere, show full path? Combo might not like mixed.
        # Actually, let's just properly resolve.
        
        current = self.var_keystore_path.get()
        if current:
            p = Path(current)
            if p.parent == keys_dir and p.name in keys:
                 self.combo_keystore.set(p.name) # Show readable name
            # Else keep full path (user browsed elsewhere)

    def _install_framework(self):
        filename = filedialog.askopenfilename(title="Select Framework APK", filetypes=[("APK Files", "*.apk")])
        if filename:
            success, _ = self.framework_manager.install_framework(filename)
            if success: messagebox.showinfo("Success", "Framework installed successfully!")
            else: messagebox.showerror("Error", "Framework installation failed.")

    def _clear_framework(self):
        if messagebox.askyesno("Confirm", "Clear all installed frameworks?"):
            if self.framework_manager.clear_framework():
                messagebox.showinfo("Success", "Framework cache cleared!")

    def _refresh_apktool_list(self):
        """Refresh list of custom apktools"""
        custom_dir = PathManager.get_base_dir() / "tools" / "custom"
        custom_dir.mkdir(parents=True, exist_ok=True)
        
        jars = [f.name for f in custom_dir.glob("*.jar")]
        # Values for combo
        values = ["Default"] + jars
        self.combo_apktool.configure(values=values)
        
        # Ensure current value is valid
        current = self.var_custom_apktool_path.get()
        if current and current not in values and current != "Default":
             # If it's a full path, check if it's in custom dir
             p = Path(current)
             if p.parent == custom_dir and p.name in jars:
                 self.var_custom_apktool_path.set(p.name)
             else:
                 # It might be a custom path outside? For now tailored to custom dir
                 self.var_custom_apktool_path.set("Default")

    def _toggle_apktool_mode(self):
        """Enable/Disable custom apktool selection"""
        if self.var_use_custom_apktool.get():
            self.combo_apktool.configure(state="normal")
            # Create tools/custom if not exists
            (PathManager.get_base_dir() / "tools" / "custom").mkdir(parents=True, exist_ok=True)
        else:
            self.combo_apktool.configure(state="disabled")

    def _add_custom_apktool(self):
        """Import a custom apktool jar"""
        filename = filedialog.askopenfilename(
            title="Select Apktool Jar",
            filetypes=[("Jar Files", "*.jar")]
        )
        if filename:
            try:
                import shutil
                custom_dir = PathManager.get_base_dir() / "tools" / "custom"
                custom_dir.mkdir(parents=True, exist_ok=True)
                
                dest = custom_dir / Path(filename).name
                shutil.copy2(filename, dest)
                
                self._refresh_apktool_list()
                self.var_custom_apktool_path.set(dest.name)
                
                messagebox.showinfo("Success", f"Added {dest.name} to custom tools!")
                self.log_message(f"Imported custom tool: {dest.name}", "success")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import jar: {e}")

    def _refresh_aapt_list(self):
        """Refresh list of custom aapt"""
        custom_dir = PathManager.get_base_dir() / "tools" / "custom"
        custom_dir.mkdir(parents=True, exist_ok=True)
        
        exes = [f.name for f in custom_dir.glob("*.exe")]
        # Values for combo
        values = ["Default"] + exes
        self.combo_aapt.configure(values=values)
        
        # Ensure current value is valid
        current = self.var_custom_aapt_path.get()
        if current and current not in values and current != "Default":
             # If it's a full path, check if it's in custom dir
             p = Path(current)
             if p.parent == custom_dir and p.name in exes:
                 self.var_custom_aapt_path.set(p.name)
             else:
                 self.var_custom_aapt_path.set("Default")

    def _toggle_aapt_mode(self):
        """Enable/Disable custom aapt selection"""
        if self.var_use_custom_aapt.get():
            self.combo_aapt.configure(state="normal")
            (PathManager.get_base_dir() / "tools" / "custom").mkdir(parents=True, exist_ok=True)
        else:
            self.combo_aapt.configure(state="disabled")

    def _add_custom_aapt(self):
        """Import a custom aapt exe"""
        filename = filedialog.askopenfilename(
            title="Select AAPT Executable",
            filetypes=[("Executables", "*.exe")]
        )
        if filename:
            try:
                import shutil
                custom_dir = PathManager.get_base_dir() / "tools" / "custom"
                custom_dir.mkdir(parents=True, exist_ok=True)
                
                dest = custom_dir / Path(filename).name
                shutil.copy2(filename, dest)
                
                self._refresh_aapt_list()
                self.var_custom_aapt_path.set(dest.name)
                
                messagebox.showinfo("Success", f"Added {dest.name} to custom tools!")
                self.log_message(f"Imported custom tool: {dest.name}", "success")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import exe: {e}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to import exe: {e}")

    def _refresh_aapt2_list(self):
        """Refresh list of custom aapt2"""
        custom_dir = PathManager.get_base_dir() / "tools" / "custom"
        custom_dir.mkdir(parents=True, exist_ok=True)
        
        exes = [f.name for f in custom_dir.glob("*.exe")]
        # Values for combo
        values = ["Default"] + exes
        self.combo_aapt2.configure(values=values)
        
        # Ensure current value is valid
        current = self.var_custom_aapt2_path.get()
        if current and current not in values and current != "Default":
             p = Path(current)
             if p.parent == custom_dir and p.name in exes:
                 self.var_custom_aapt2_path.set(p.name)
             else:
                 self.var_custom_aapt2_path.set("Default")

    def _toggle_aapt2_mode(self):
        """Enable/Disable custom aapt2 selection"""
        if self.var_use_custom_aapt2.get():
            self.combo_aapt2.configure(state="normal")
            (PathManager.get_base_dir() / "tools" / "custom").mkdir(parents=True, exist_ok=True)
        else:
            self.combo_aapt2.configure(state="disabled")

    def _add_custom_aapt2(self):
        """Import a custom aapt2 exe"""
        filename = filedialog.askopenfilename(
            title="Select AAPT2 Executable",
            filetypes=[("Executables", "*.exe")]
        )
        if filename:
            try:
                import shutil
                custom_dir = PathManager.get_base_dir() / "tools" / "custom"
                custom_dir.mkdir(parents=True, exist_ok=True)
                
                dest = custom_dir / Path(filename).name
                shutil.copy2(filename, dest)
                
                self._refresh_aapt2_list()
                self.var_custom_aapt2_path.set(dest.name)
                
                messagebox.showinfo("Success", f"Added {dest.name} to custom tools!")
                self.log_message(f"Imported custom tool: {dest.name}", "success")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import exe: {e}")

    def _save_settings(self):
        self.settings_manager.save()
        
        # Update Manager with new path if custom selected
        base_dir = PathManager.get_base_dir() / "tools" / "custom"
        
        # Apktool Update
        if self.var_use_custom_apktool.get():
            val = self.var_custom_apktool_path.get()
            if val and val != "Default":
                 custom_path = base_dir / val
                 self.settings.custom_apktool_path = str(custom_path)
            else:
                 self.settings.custom_apktool_path = ""
        
        # AAPT Update
        if self.var_use_custom_aapt.get():
            val = self.var_custom_aapt_path.get()
            if val and val != "Default":
                 custom_path = base_dir / val
                 self.settings.custom_aapt_path = str(custom_path)
                 self.log_message(f"Set active AAPT: {val}", "info")
            else:
                 self.settings.custom_aapt_path = ""

        # AAPT2 Update
        if self.var_use_custom_aapt2.get():
            val = self.var_custom_aapt2_path.get()
            if val and val != "Default":
                 custom_path = base_dir / val
                 self.settings.custom_aapt2_path = str(custom_path)
                 self.log_message(f"Set active AAPT2: {val}", "info")
            else:
                 self.settings.custom_aapt2_path = ""

        # Final Sync to Ensure Config Object Matching
        if self.var_use_custom_apktool.get() and self.var_custom_apktool_path.get() != "Default":
            self.settings.custom_apktool_path = self.var_custom_apktool_path.get()
        else:
            self.settings.custom_apktool_path = ""
            
        if self.var_use_custom_aapt.get() and self.var_custom_aapt_path.get() != "Default":
            self.settings.custom_aapt_path = self.var_custom_aapt_path.get()
        else:
            self.settings.custom_aapt_path = ""

        if self.var_use_custom_aapt2.get() and self.var_custom_aapt2_path.get() != "Default":
            self.settings.custom_aapt2_path = self.var_custom_aapt2_path.get()
        else:
            self.settings.custom_aapt2_path = ""
            
        # Save Keystore Profile
        current_ks = self.var_keystore_path.get()
        if current_ks and self.var_use_custom_keystore.get():
             self._save_keystore_profile(
                 current_ks,
                 self.var_keystore_pass.get(),
                 self.var_key_alias.get(),
                 self.var_key_pass.get()
             )

        self.settings_manager.save()
        self.log_message("✓ Settings & Profiles saved successfully", "success")

    def _on_keystore_path_change(self, *args):
        """Auto-fill credentials from saved profile"""
        path = self.var_keystore_path.get()
        if not path or not self.settings.saved_keystores: return
        
        # Check by full path
        profile = self.settings.saved_keystores.get(path)
        
        # Check by filename (if relative in keys/)
        if not profile:
             profile = self.settings.saved_keystores.get(Path(path).name)
             
        if profile:
            self.var_keystore_pass.set(profile.get("pass", ""))
            self.var_key_alias.set(profile.get("alias", ""))
            self.var_key_pass.set(profile.get("key_pass", ""))
            self.log_message(f"Loaded credentials for: {Path(path).name}", "info")

    def _save_keystore_profile(self, path, password, alias, key_pass):
        """Update profile in settings"""
        if not path: return
        
        # Save by full path AND filename for robustness? 
        # Prefer full path if absolute, filename if in keys dir.
        # Let's save both lookup keys to be safe or just normalized?
        # Saving by exact value in var is safest for retrieval.
        
        profile = {
            "pass": password,
            "alias": alias,
            "key_pass": key_pass
        }
        
        # Update Dictionary
        if not self.settings.saved_keystores: self.settings.saved_keystores = {}
        self.settings.saved_keystores[path] = profile
        
        # Also map filename if it's in keys dir
        p = Path(path)
        self.settings.saved_keystores[p.name] = profile
