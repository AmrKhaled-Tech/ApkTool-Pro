import customtkinter as ctk
from tkinter import messagebox
from dialogs import ADBBackupDialog, NetworkScanDialog, SmartTaskDialog
from pathlib import Path
try:
    from adb_manager import ADBManager
    ADB_AVAILABLE = True
except ImportError:
    ADB_AVAILABLE = False

class ADBTabMixin:
    def _build_adb_tab(self):
        """Build ADB Manager tab"""
        tab = self.tab_adb
        tab.grid_columnconfigure(0, weight=1)
        
        # Initialize ADB Manager
        if not ADB_AVAILABLE:
            error_label = ctk.CTkLabel(
                tab,
                text="⚠️ ADB Manager not available\nadb_manager.py not found",
                font=ctk.CTkFont(size=14)
            )
            error_label.pack(pady=50)
            return
        
        self.adb_manager = ADBManager(logger=self.log_message)
        
        # Connection Panel
        conn_frame = ctk.CTkFrame(tab)
        conn_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        conn_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            conn_frame,
            text="📱 Device Connection",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=3, pady=(8, 4), sticky="w", padx=10)
        
        # Status indicator
        self.adb_status_label = ctk.CTkLabel(
            conn_frame,
            text="⚫ Not Connected",
            font=ctk.CTkFont(size=12)
        )
        self.adb_status_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # Connection buttons
        btn_frame = ctk.CTkFrame(conn_frame, fg_color="transparent")
        btn_frame.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="e")
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Refresh",
            command=self._adb_refresh_devices,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="📲 USB",
            command=self._adb_connect_usb,
            width=90
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="📡 WiFi",
            command=self._adb_wifi_setup,
            width=90
        ).pack(side="left", padx=5)
        
        # Device selector
        ctk.CTkLabel(conn_frame, text="Device:", font=ctk.CTkFont(size=12)).grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        
        self.adb_device_var = ctk.StringVar(value="No devices found")
        self.adb_device_menu = ctk.CTkOptionMenu(
            conn_frame,
            variable=self.adb_device_var,
            values=["No devices found"],
            command=self._adb_device_selected
        )
        self.adb_device_menu.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="ew")
        
        # Package Management Panel
        pkg_frame = ctk.CTkFrame(tab)
        pkg_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        pkg_frame.grid_columnconfigure(0, weight=1)
        pkg_frame.grid_rowconfigure(2, weight=1)  # Table container expands
        tab.grid_rowconfigure(1, weight=1)
        
        
        ctk.CTkLabel(
            pkg_frame,
            text="📦 Package Management",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, pady=(8, 4), sticky="w", padx=10)
        
        # Row 1: Filters and Search in SAME ROW
        filter_search_frame = ctk.CTkFrame(pkg_frame, fg_color="transparent")
        filter_search_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        filter_search_frame.grid_columnconfigure(1, weight=1)  # Search expands
        
        # Left side: Filters
        filter_container = ctk.CTkFrame(filter_search_frame, fg_color="transparent")
        filter_container.grid(row=0, column=0, sticky="w")
        
        self.adb_filter_var = ctk.StringVar(value="all")
        
        ctk.CTkLabel(filter_container, text="Filter:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 8))
        
        ctk.CTkRadioButton(
            filter_container,
            text="All",
            variable=self.adb_filter_var,
            value="all",
            command=self._adb_filter_changed
        ).pack(side="left", padx=4)
        
        ctk.CTkRadioButton(
            filter_container,
            text="User",
            variable=self.adb_filter_var,
            value="user",
            command=self._adb_filter_changed
        ).pack(side="left", padx=4)
        
        ctk.CTkRadioButton(
            filter_container,
            text="System",
            variable=self.adb_filter_var,
            value="system",
            command=self._adb_filter_changed
        ).pack(side="left", padx=4)
        
        # Right side: Search
        search_container = ctk.CTkFrame(filter_search_frame, fg_color="transparent")
        search_container.grid(row=0, column=1, sticky="e", padx=(20, 0))
        
        ctk.CTkLabel(search_container, text="Search:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 8))
        
        self.adb_search_var = ctk.StringVar()
        self.adb_search_entry = ctk.CTkEntry(
            search_container,
            textvariable=self.adb_search_var,
            placeholder_text="Type package name...",
            width=320,
            font=ctk.CTkFont(size=11)
        )
        self.adb_search_entry.pack(side="left", padx=4)
        self.adb_search_var.trace_add('write', lambda *args: self._adb_update_package_display())
        
        # Row 2: Professional Package Table
        table_container = ctk.CTkFrame(pkg_frame)
        table_container.grid(row=2, column=0, padx=10, pady=(10, 5), sticky="nsew")
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(1, weight=1)
        
        # Table Header
        header_frame = ctk.CTkFrame(table_container, height=35, fg_color=("#e0e0e0", "#2b2b2b"))
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="TYPE",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=100,
            anchor="w"
        ).grid(row=0, column=0, padx=15, pady=8, sticky="w")
        
        ctk.CTkLabel(
            header_frame,
            text="PACKAGE NAME",
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        ).grid(row=0, column=1, padx=10, pady=8, sticky="w")
        
        # Styled Textbox for high performance (instead of slow ScrollableFrame)
        self.adb_package_list = ctk.CTkTextbox(
            table_container,
            font=ctk.CTkFont(family="Cascadia Code", size=11),
            activate_scrollbars=True,
            wrap="none",
            height=180
        )
        self.adb_package_list.grid(row=1, column=0, sticky="nsew")
        
        # Configure tags for styling
        self.adb_package_list.tag_config("sel_row", background="#1b4d3e", foreground="white")
        self.adb_package_list.tag_config("system_app", foreground="#ff6b6b")
        self.adb_package_list.tag_config("user_app", foreground="#4ecdc4")
        
        # Bind events
        self.adb_package_list.bind("<Button-1>", self._adb_package_clicked)
        self.adb_package_list.bind("<Motion>", self._adb_package_hover)
        
        # Row 3: Selected package info (compact strip)
        self.adb_selected_label = ctk.CTkLabel(
            pkg_frame,
            text="Selected: None",
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
            fg_color=("#e8f4f8", "#1e3a4a"),
            corner_radius=4,
            height=28
        )
        self.adb_selected_label.grid(row=3, column=0, padx=10, pady=(4, 8), sticky="ew")
        
        # Operations Panel
        ops_frame = ctk.CTkFrame(tab)
        ops_frame.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")
        ops_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        
        ctk.CTkLabel(
            ops_frame,
            text="🛠️ Operations",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, columnspan=5, pady=(8, 4), sticky="w", padx=10)
        
        ctk.CTkButton(
            ops_frame,
            text="💾 Backup",
            command=self._adb_backup_apk,
            height=36
        ).grid(row=1, column=0, padx=4, pady=(4, 8), sticky="ew")
        
        ctk.CTkButton(
            ops_frame,
            text="📥 Install",
            command=self._adb_install_apk,
            height=36
        ).grid(row=1, column=1, padx=4, pady=(4, 8), sticky="ew")
        
        ctk.CTkButton(
            ops_frame,
            text="🗑️ Uninstall",
            command=self._adb_uninstall_package,
            height=36,
            fg_color=("red", "#c62828")
        ).grid(row=1, column=2, padx=4, pady=(4, 8), sticky="ew")
        
        ctk.CTkButton(
            ops_frame,
            text="📋 Info",
            command=self._adb_show_package_info,
            height=36
        ).grid(row=1, column=3, padx=4, pady=(4, 8), sticky="ew")
        
        ctk.CTkButton(
            ops_frame,
            text="📂 Backup Folder",
            command=self._adb_open_backup_folder,
            height=36
        ).grid(row=1, column=4, padx=4, pady=(4, 8), sticky="ew")
        
        # Initialize
        self.adb_devices = []
        self.adb_packages = []
        self.adb_selected_package = None
        self._adb_refresh_devices()

    def _adb_refresh_devices(self):
        """Refresh device list"""
        if not ADB_AVAILABLE: return
        self._run_in_thread(self.__adb_refresh_devices_bg)
    
    def __adb_refresh_devices_bg(self):
        """Background refresh"""
        devices = self.adb_manager.check_devices()
        def update_ui():
            self.adb_devices = devices
            if devices:
                device_names = [str(d) for d in devices]
                self.adb_device_menu.configure(values=device_names)
                self.adb_device_var.set(device_names[0])
                self.adb_manager.current_device = devices[0].id
                self.adb_status_label.configure(text=f"🟢 Connected ({len(devices)} device(s))")
                self.log_message(f"Found {len(devices)} device(s)", "success")
                self._adb_load_packages()
            else:
                self.adb_device_menu.configure(values=["No devices found"])
                self.adb_device_var.set("No devices found")
                self.adb_status_label.configure(text="⚫ Not Connected")
                self.log_message("No devices found. Connect a device via USB or WiFi", "info")
        self.callback_queue.put(update_ui)

    def _adb_connect_usb(self):
        self._adb_refresh_devices()

    def _adb_wifi_setup(self):
        """WiFi connection wizard - Smart pairing dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("📡 WiFi Connection Setup")
        dialog.transient(self)
        dialog.grab_set()
        
        dialog.update_idletasks()
        width, height = 550, 490
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        dialog.resizable(False, False)
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="📡 WiFi Debugging Setup", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        instructions = (
            "1. On your Android device:\n"
            "   • Go to Settings → Developer Options\n"
            "   • Enable 'Wireless debugging'\n"
            "   • Tap 'Pair device with pairing code'\n\n"
            "2. Enter the pairing details below:"
        )
        ctk.CTkLabel(main_frame, text=instructions, font=ctk.CTkFont(size=11), justify="left", anchor="w").pack(pady=10, fill="x")
        
        def try_auto_detect():
            def on_scan_complete(found_ips):
                if found_ips:
                    ip_combobox.configure(values=found_ips)
                    ip_combobox.set(found_ips[0])
                    status_label.configure(text=f"✓ Found {len(found_ips)} active devices")
                else:
                    status_label.configure(text="⚠️ No devices found. Check connection.")
            NetworkScanDialog(dialog, on_complete=on_scan_complete)

        ctk.CTkButton(main_frame, text="🔍 Find Device IP (Network Scan)", command=try_auto_detect, height=35, font=ctk.CTkFont(size=12, weight="bold")).pack(pady=10)
        
        input_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        input_frame.pack(pady=10, fill="x")
        
        ip_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        ip_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(ip_frame, text="IP Address:", width=120, anchor="w", font=ctk.CTkFont(size=12)).pack(side="left")
        
        ip_combobox = ctk.CTkComboBox(ip_frame, width=300, font=ctk.CTkFont(size=12), values=[])
        ip_combobox.pack(side="left", padx=5)
        ip_combobox.set("")
        ip_combobox.placeholder_text = "Enter IP Address"

        pair_port_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        pair_port_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(pair_port_frame, text="Pairing Port:", width=120, anchor="w", font=ctk.CTkFont(size=12)).pack(side="left")
        pair_port_entry = ctk.CTkEntry(pair_port_frame, placeholder_text="xxxxx", width=300, font=ctk.CTkFont(size=12))
        pair_port_entry.pack(side="left", padx=5)
        
        code_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        code_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(code_frame, text="Pairing Code:", width=120, anchor="w", font=ctk.CTkFont(size=12)).pack(side="left")
        code_entry = ctk.CTkEntry(code_frame, placeholder_text="123456", width=300, font=ctk.CTkFont(size=12))
        code_entry.pack(side="left", padx=5)
        
        status_label = ctk.CTkLabel(main_frame, text="Ready to pair", font=ctk.CTkFont(size=11))
        status_label.pack(pady=10)
        
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        def do_pair():
            ip = ip_combobox.get().strip()
            pair_port = pair_port_entry.get().strip()
            code = code_entry.get().strip()
            
            if not ip or not pair_port or not code:
                status_label.configure(text="⚠️ Please fill all fields")
                return
            
            status_label.configure(text="🔄 Pairing...")
            dialog.update()
            
            success, output = self.adb_manager._run_adb(["pair", f"{ip}:{pair_port}", code])
            
            if success and "success" in output.lower():
                status_label.configure(text="✓ Paired successfully!")
                dialog.update()
                import time
                time.sleep(0.5)
                
                from tkinter import simpledialog
                conn_port = simpledialog.askstring(
                    "Connection Port",
                    f"Pairing successful!\n\nNow check your device for the CONNECTION port.\n(Usually different from pairing port)\n\nEnter connection port:",
                    initialvalue="5555",
                    parent=dialog
                )
                
                if not conn_port:
                    status_label.configure(text="✓ Paired (connection cancelled)")
                    return
                
                status_label.configure(text=f"🔄 Connecting to {ip}:{conn_port}...")
                dialog.update()
                
                conn_success, msg = self.adb_manager.connect_wifi(ip, int(conn_port))
                
                if conn_success:
                    status_label.configure(text=f"✓ Connected to {ip}:{conn_port}!")
                    self.log_message(f"WiFi connected: {ip}:{conn_port}", "success")
                    self._adb_refresh_devices()
                    dialog.after(1500, dialog.destroy)
                else:
                    status_label.configure(text=f"✗ Connection failed: {msg}")
            else:
                status_label.configure(text=f"✗ Pairing failed: {output}")
        
        ctk.CTkButton(btn_frame, text="🔗 Pair & Connect", command=do_pair, width=150, fg_color=("green", "#2d7d32")).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="✖ Cancel", command=dialog.destroy, width=100, fg_color="transparent", border_width=1).pack(side="left", padx=5)

    def _adb_device_selected(self, choice):
        if choice == "No devices found": return
        for device in self.adb_devices:
            if str(device) == choice:
                self.adb_manager.current_device = device.id
                self.log_message(f"Selected device: {device.id}", "info")
                self._adb_load_packages()
                break

    def _adb_filter_changed(self):
        if not hasattr(self, 'adb_manager') or not self.adb_manager.current_device: return
        self._adb_load_packages()

    def _adb_load_packages(self):
        if not self.adb_manager.current_device: return
        self._run_in_thread(self.__adb_load_packages_bg)

    def __adb_load_packages_bg(self):
        filter_type = self.adb_filter_var.get()
        packages = self.adb_manager.list_packages(filter_type=filter_type)
        def update_ui():
            self.adb_packages = packages
            self._adb_update_package_display()
        self.callback_queue.put(update_ui)

    def _adb_update_package_display(self):
        query = self.adb_search_var.get().lower()
        self.adb_package_list.configure(state="normal", font=ctk.CTkFont(family="Cascadia Code", size=12))
        self.adb_package_list.delete("1.0", "end")
        
        filtered = self.adb_packages if hasattr(self, 'adb_packages') else []
        if query:
            filtered = [p for p in filtered if query in p.name.lower()]
            
        header = f"{'TYPE':<10} {'PACKAGE NAME'}\n"
        self.adb_package_list.insert("end", header, "header")
        try:
            font_header = ctk.CTkFont(family="Cascadia Code", size=12, weight="bold")
            self.adb_package_list._textbox.tag_config("header", font=font_header, foreground="gray")
        except: pass
        self.adb_package_list.insert("end", "-"*80 + "\n", "header")
            
        if not filtered:
            self.adb_package_list.insert("end", "\nNo packages found matching query.", "header")
            self.adb_package_list.configure(state="disabled")
            return
            
        self.current_filtered_packages = filtered
        
        for idx, pkg in enumerate(filtered):
            type_text = "SYSTEM" if pkg.is_system else "USER"
            type_tag = "system_app" if pkg.is_system else "user_app"
            line_prefix = f"{type_text:<10} "
            self.adb_package_list.insert("end", line_prefix, type_tag)
            self.adb_package_list.insert("end", f"{pkg.name}\n")
            
        self.adb_package_list.configure(state="disabled")

    def _adb_package_clicked(self, event):
        try:
            index = self.adb_package_list.index(f"@{event.x},{event.y}")
            line = int(index.split('.')[0])
            pkg_idx = line - 3
            if hasattr(self, 'current_filtered_packages') and 0 <= pkg_idx < len(self.current_filtered_packages):
                pkg = self.current_filtered_packages[pkg_idx]
                self.adb_selected_package = pkg
                self.adb_selected_label.configure(text=f"✓ Selected: {pkg.name}")
                self.adb_package_list.tag_remove("sel_row", "1.0", "end")
                self.adb_package_list.tag_add("sel_row", f"{line}.0", f"{line}.end")
        except: pass

    def _adb_package_hover(self, event): pass

    def _adb_backup_apk(self):
        if not self.adb_selected_package:
            messagebox.showwarning("No Selection", "Please select a package first")
            return
        folder = filedialog.askdirectory(title="Select Backup Folder")
        if not folder: return
        ADBBackupDialog(self, self.adb_selected_package, self.adb_manager, folder, on_complete=self._on_backup_complete)

    def _on_backup_complete(self, success, result):
        if success: self.log_message(f"Backup saved to: {result}", "success")
        else:
             if result != "Cancelled by user": self.log_message(f"Backup failed: {result}", "error")

    def _adb_install_apk(self):
        if not self.adb_manager.current_device:
            messagebox.showwarning("No Device", "No device connected")
            return
        apk_path = filedialog.askopenfilename(title="Select APK to Install", filetypes=[("APK Files", "*.apk"), ("All Files", "*.*")])
        if not apk_path: return
        
        def install_task(controller):
            controller.update_status(f"Installing {Path(apk_path).name}...")
            controller.update_progress(0, "indeterminate")
            def run_install(flags=[]):
                cmd = ["install", "-r"] + flags + [apk_path]
                controller.log(f"Running: adb -s {self.adb_manager.current_device} {' '.join(cmd)}", "info")
                return self.adb_manager._run_adb(cmd, device_id=self.adb_manager.current_device, timeout=300)

            success, output = run_install()
            if success and "Success" in output:
                controller.update_progress(100, "determinate")
                controller.update_status("✓ Install Successful!")
                return "Installed Successfully"
            
            error_msg = output.strip()
            controller.log(f"Install failed: {error_msg}", "error")
            
            if "INSTALL_FAILED_TEST_ONLY" in output:
                if controller.ask_user("Test-Only APK Detected", "Install with '-t' flag?", options=("yes", "no")):
                    controller.update_status("🔄 Retrying with -t flag...")
                    success, output = run_install(["-t"])
                    if success and "Success" in output: return "Installed with -t"
            elif "INSTALL_FAILED_VERSION_DOWNGRADE" in output:
                if controller.ask_user("Version Downgrade", "Force downgrade? (May lose data)", options=("yes", "no")):
                    controller.update_status("🔄 Retrying with -d flag...")
                    success, output = run_install(["-d"])
                    if success and "Success" in output: return "Downgraded successfully"
            elif "INSTALL_FAILED_UPDATE_INCOMPATIBLE" in output:
                raise Exception("Signature mismatch - Uninstall old version first")

            if not success or "Success" not in output: raise Exception(f"Install Failed: {error_msg}")
            return "Installed Successfully"

        def on_complete(success, result):
            if success:
                self.log_message(f"Install Complete: {result}", "success")
                self._adb_refresh_devices()
            else:
                self.log_message(f"Install Error: {result}", "error")

        SmartTaskDialog(self, "Smart APK Installer", install_task, on_complete=on_complete, logger_callback=self.log_message)

    def _adb_uninstall_package(self):
        if not self.adb_selected_package:
            messagebox.showwarning("No Selection", "Please select a package first")
            return
        package = self.adb_selected_package
        if package.is_system:
             if not messagebox.askyesno("Warning", f"⚠️ {package.name} is a SYSTEM app.\n\nUninstalling system apps may cause instability.\nAre you sure?"): return
        else:
            if not messagebox.askyesno("Confirm", f"Uninstall {package.name}?"): return
            
        def uninstall_task(controller):
            controller.update_status(f"Uninstalling {package.name}...")
            controller.update_progress(0, "indeterminate")
            controller.log(f"Uninstalling {package.name}...", "info")
            success, msg = self.adb_manager.uninstall_package(package.name)
            if success:
                controller.update_progress(100, "determinate")
                controller.update_status("✓ Uninstall Successful!")
                controller.log(f"✓ {package.name} removed.", "success")
                return "success"
            else:
                raise Exception(f"Uninstall failed: {msg}")

        def on_complete(success, result):
            if success:
                self.status_label.configure(text=f"✓ Uninstalled: {package.name}")
                self._adb_load_packages()
            else:
                self.status_label.configure(text="Uninstall failed")

        SmartTaskDialog(self, f"Uninstalling {package.name}", uninstall_task, on_complete=on_complete, logger_callback=self.log_message)

    def _adb_show_package_info(self):
        if not self.adb_selected_package:
            messagebox.showwarning("No Selection", "Please select a package first")
            return
        package = self.adb_selected_package
        def info_task(controller):
            controller.update_status(f"Fetching info for {package.name}...")
            controller.update_progress(0, "indeterminate")
            info = self.adb_manager.get_package_info(package.name)
            if not info: raise Exception("Failed to retrieve package info")
            controller.update_progress(100, "determinate")
            try: size_mb = f"{info.size / (1024*1024):.2f} MB" if info.size > 0 else "N/A"
            except: size_mb = "Unknown"
            
            lines = [
                f"📦  PACKAGE: {info.name}",
                f"{'-'*40}",
                f"ℹ️  Version:      {info.version_name} (Code: {info.version_code})",
                f"💾  Size:         {size_mb}",
                f"🛠️  SDK:          Min: {info.min_sdk} | Target: {info.target_sdk}",
                f"👤  Type:         {'System App' if info.is_system else 'User App'}",
                f"🏴  Flags:        {' '.join(info.flags) if hasattr(info, 'flags') and info.flags else 'None'}",
                f"{'-'*40}",
                f"🕒  Installed:    {info.install_time}",
                f"🔄  Updated:      {info.update_time}",
                f"{'-'*40}",
                f"📁  Path:         {info.apk_path}",
                f"📂  Data:         {info.data_dir}",
                f"🆔  UID:          {info.uid}",
                f"💿  Installer:    {info.installer or 'Unknown'}"
            ]
            return "\n".join(lines)

        def on_complete(success, result):
            if success: messagebox.showinfo(f"Package Info: {package.name}", result)
            else: messagebox.showerror("Error", f"Failed to get info: {result}")

        SmartTaskDialog(self, "Package Inspector", info_task, on_complete=on_complete, logger_callback=self.log_message)

    def _adb_open_backup_folder(self):
        backup_dir = Path.home() / "Desktop" / "APK_Backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        try:
            import os, sys
            if sys.platform == 'win32': os.startfile(str(backup_dir))
            else: 
                 import subprocess
                 subprocess.Popen(['xdg-open', str(backup_dir)])
        except: pass
