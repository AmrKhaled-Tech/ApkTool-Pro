"""
MyApkTool - Dialogs Module
Smart dialogs for background tasks, ADB backup, and network scanning.
"""

import sys
import threading
import queue
import subprocess
from pathlib import Path

import customtkinter as ctk


# ============================================================================
# SMART TASK DIALOG
# ============================================================================

class SmartTaskDialog(ctk.CTkToplevel):
    """
    Universal Smart Dialog for performing background tasks with:
    - Live Progress & Status
    - Cancellation Support
    - Log Integration
    - Interactive Decision Making (Ask User from thread)
    """
    def __init__(self, parent, title, task_func, on_complete=None, logger_callback=None):
        super().__init__(parent)
        self.task_func = task_func
        self.on_complete = on_complete
        self.logger_callback = logger_callback
        self.cancelled = False
        self.queue = queue.Queue()
        self.result_queue = queue.Queue() # For user answers
        
        self.title(title)
        self.geometry("500x200")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center
        self.update_idletasks()
        try:
            x = (self.winfo_screenwidth() // 2) - (500 // 2)
            y = (self.winfo_screenheight() // 2) - (200 // 2)
            self.geometry(f"+{x}+{y}")
        except:
            pass
            
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.cancel_task)
        
        # Start monitoring queue
        self.after(100, self._check_queue)
        
        # Start task
        self.after(500, self.start_task)
        
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Status Icon/Title
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="🚀 Processing...", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(0, 10))
        
        # Detailed Status
        self.status_label = ctk.CTkLabel(
            self.main_frame, 
            text="Initializing...", 
            text_color="gray",
            wraplength=450
        )
        self.status_label.pack(pady=(0, 10))
        
        # Progress Bar
        self.progress = ctk.CTkProgressBar(self.main_frame, mode="indeterminate", width=400)
        self.progress.pack(pady=(0, 20))
        self.progress.start()
        
        # Cancel Button
        self.cancel_btn = ctk.CTkButton(
            self.main_frame, 
            text="Cancel Operation", 
            fg_color="#c62828", 
            hover_color="#b71c1c", 
            command=self.cancel_task
        )
        self.cancel_btn.pack()

    def start_task(self):
        # Pass 'self' as controller to the task
        threading.Thread(target=self._run_wrapper, daemon=True).start()

    def _run_wrapper(self):
        try:
            result = self.task_func(self)
            self.queue.put(("finish", result))
        except Exception as e:
            self.queue.put(("error", str(e)))

    def cancel_task(self):
        self.cancelled = True
        self.status_label.configure(text="🛑 Stopping operation...")
        self.cancel_btn.configure(state="disabled", text="Stopping...")
        
        # Force-close after 3 seconds if thread hasn't finished
        self.after(3000, self._force_close)

    def update_status(self, text):
        self.queue.put(("status", text))

    def update_progress(self, val, mode="determinate"):
        self.queue.put(("progress", (val, mode)))
        
    def log(self, message, level="info"):
        self.queue.put(("log", (message, level)))

    def ask_user(self, title, message, options=("yes", "no")):
        """Block thread and ask user on UI thread"""
        self.queue.put(("ask", (title, message, options)))
        return self.result_queue.get() # Waits here

    def _check_queue(self):
        try:
            while True:
                msg_type, data = self.queue.get_nowait()
                
                if msg_type == "status":
                    self.status_label.configure(text=data)
                
                elif msg_type == "progress":
                    val, mode = data
                    if mode != self.progress._mode:
                        self.progress.configure(mode=mode)
                        if mode == "indeterminate":
                            self.progress.start()
                        else:
                            self.progress.stop()
                    if mode == "determinate":
                        self.progress.set(val)
                
                elif msg_type == "log":
                    msg, level = data
                    if self.logger_callback:
                        self.logger_callback(msg, level) 
                    
                elif msg_type == "ask":
                    title, msg, options = data
                    from tkinter import messagebox
                    # Show dialog
                    if options == ("yes", "no"):
                        res = messagebox.askyesno(title, msg, parent=self)
                    else:
                        res = messagebox.askokcancel(title, msg, parent=self)
                    self.result_queue.put(res)
                    
                elif msg_type == "finish":
                    self._finish(True, data)
                    return
                
                elif msg_type == "error":
                    self._finish(False, data)
                    return
                    
        except queue.Empty:
            pass
        
        if self.winfo_exists():
            self.after(50, self._check_queue)

    def _finish(self, success, result):
        if self.cancelled:
            # If cancelled, just close without calling on_complete
            if self.winfo_exists():
                self.destroy()
            return
        if self.on_complete:
            self.on_complete(success, result)
        if self.winfo_exists():
            self.destroy()

    def _force_close(self):
        """Force close dialog after cancel timeout"""
        if self.winfo_exists():
            self.destroy()


# ============================================================================
# ADB BACKUP DIALOG
# ============================================================================

class ADBBackupDialog(ctk.CTkToplevel):
    """Interactive ADB Backup Dialog"""
    
    def __init__(self, parent, package, adb_manager, output_folder, on_complete=None):
        super().__init__(parent)
        self.package = package
        self.adb_manager = adb_manager
        self.output_folder = output_folder
        self.on_complete = on_complete
        self.process = None
        self.cancelled = False
        self.output_file = Path(output_folder) / f"{package.name}.apk"
        
        # UI Setup
        self.title("Backup in Progress")
        self.geometry("450x290")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center dialog
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (250 // 2)
        self.geometry(f"+{x}+{y}")
        
        self._build_ui()
        self.after(500, self.start_backup)
        
    def _build_ui(self):
        # Progress Area
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_frame, 
            text="💾 Backing up APK...", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 15))
        
        # Info Box
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=10)
        
        info_text = (
            f"📦 Package: {self.package.name}\n"
            # f"🏷️ Version: {self.package.version_name}\n"
            f"📂 Destination: {self.output_folder}"
        )
        
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            justify="left",
            font=ctk.CTkFont(family="Cascadia Code", size=11),
            anchor="w"
        ).pack(fill="x", padx=10, pady=10)
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", pady=(20, 10))
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        # Status Label
        self.status_label = ctk.CTkLabel(main_frame, text="Starting backup...", text_color="gray")
        self.status_label.pack(pady=(0, 15))
        
        # Cancel Button
        self.cancel_btn = ctk.CTkButton(
            main_frame,
            text="Cancel Operation",
            fg_color="#c62828",
            hover_color="#b71c1c",
            command=self.cancel_backup
        )
        self.cancel_btn.pack(side="bottom")
        
    def start_backup(self):
        """Start backup thread"""
        threading.Thread(target=self._run_backup_logic, daemon=True).start()
        
    def _run_backup_logic(self):
        try:
            # 1. Get paths from device
            success, output = self.adb_manager._run_adb(
                ["shell", "pm", "path", self.package.name], 
                device_id=self.adb_manager.current_device
            )
            
            if not success or not output:
                self._finish(False, "Failed to get APK path")
                return
                
            # 2. Parse paths using Regex
            import re
            import posixpath
            paths = re.findall(r'package:(.*?\.apk)', output)
            paths = [p.strip() for p in paths if p.strip()]

            if not paths:
                self._finish(False, "No valid APK paths found")
                return

            # 3. Determine if app is Split or Single
            is_split = len(paths) > 1
            
            # Prepare target folder or file
            if is_split:
                target_dir = Path(self.output_file).parent / self.package.name
                target_dir.mkdir(parents=True, exist_ok=True)
                self.output_file = target_dir 
            
            # 4. Pull each file individually
            total_files = len(paths)
            for i, remote_path in enumerate(paths):
                if self.cancelled: break
                
                filename = posixpath.basename(remote_path)
                
                # Determine local destination
                if is_split:
                    local_dest = str(Path(self.output_file) / filename)
                    status_msg = f"Downloading part {i+1}/{total_files}: {filename}"
                else:
                    local_dest = str(self.output_file)
                    status_msg = "Downloading APK..."

                self.status_label.configure(text=status_msg)

                # Execute independent Pull command for each file
                cmd = [
                    str(self.adb_manager.adb_path), 
                    "-s", self.adb_manager.current_device, 
                    "pull", remote_path, local_dest
                ]
                
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                
                stdout, stderr = self.process.communicate()
                
                if self.process.returncode != 0:
                    self._finish(False, f"Failed at {filename}: {stderr}")
                    return

            # 5. Finish
            if self.cancelled:
                self._finish(False, "Cancelled by user")
            else:
                self._finish(True, str(self.output_file))
                    
        except Exception as e:
            if not self.cancelled:
                self._finish(False, str(e))
                
    def cancel_backup(self):
        """Cancel current backup"""
        self.cancelled = True
        self.status_label.configure(text="Cancelling...")
        self.cancel_btn.configure(state="disabled", text="Stopping...")
        
        if self.process:
            self.process.terminate()
            
    def _finish(self, success, result):
        """Handle completion"""
        self.progress_bar.stop()
        if self.cancelled:
             self.destroy()
             return

        if success:
           self.status_label.configure(text="✓ Backup Complete!", text_color="#4caf50")
           self.progress_bar.configure(mode="determinate", progress_color="#4caf50")
           self.progress_bar.set(1)
           self.cancel_btn.configure(text="Close", fg_color="green", command=self.destroy)
        else:
           self.status_label.configure(text="✗ Failed", text_color="#f44336")
           self.progress_bar.stop()
           self.cancel_btn.configure(text="Close", command=self.destroy)
           
        if self.on_complete:
            self.on_complete(success, result)


# ============================================================================
# NETWORK SCAN DIALOG
# ============================================================================

class NetworkScanDialog(ctk.CTkToplevel):
    """Network Scan Dialog with Progress and Live Stats"""
    def __init__(self, parent, on_complete=None):
        super().__init__(parent)
        self.on_complete = on_complete
        self.cancelled = False
        self.executor = None
        self.scanned_count = 0
        self.found_count = 0
        self.total_targets = 0
        
        self.title("Network Scan")
        self.geometry("450x220")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Center
        self.update_idletasks()
        try:
            x = (self.winfo_screenwidth() // 2) - (450 // 2)
            y = (self.winfo_screenheight() // 2) - (220 // 2)
            self.geometry(f"+{x}+{y}")
        except:
            pass
        
        self._build_ui()
        self.after(500, self.start_scan)
        
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, text="🔍 Scanning Network...", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(main_frame, text="Identifying network interfaces...", text_color="gray")
        self.status_label.pack(pady=(0, 5))
        
        # Counters
        self.stats_label = ctk.CTkLabel(main_frame, text="Found: 0 | Scanned: 0/0", font=ctk.CTkFont(size=11))
        self.stats_label.pack(pady=(0, 10))
        
        self.progress = ctk.CTkProgressBar(main_frame, mode="determinate")
        self.progress.pack(fill="x", pady=(0, 15))
        self.progress.set(0)
        
        ctk.CTkButton(main_frame, text="Cancel", fg_color="#c62828", hover_color="#b71c1c", command=self.cancel_scan).pack()

    def cancel_scan(self):
        self.cancelled = True
        self.status_label.configure(text="Cancelling...")
        if self.executor:
            self.executor.shutdown(wait=False)
        self.destroy()

    def start_scan(self):
        threading.Thread(target=self._scan_logic, daemon=True).start()

    def _update_progress(self, scanned, total, found):
        if self.winfo_exists():
            self.scanned_count = scanned
            self.total_targets = total
            self.found_count = found
            
            # Update labels
            self.stats_label.configure(text=f"Found: {found} | Scanned: {scanned}/{total}")
            
            # Update progress bar
            if total > 0:
                self.progress.set(scanned / total)

    def _scan_logic(self):
        try:
            import socket
            import concurrent.futures
            import subprocess
            import re
            
            found_ips = []
            subnets = set()
            excluded_ips = set()
            
            # 1. Identify valid local subnets via ipconfig
            try:
                result = subprocess.run(["ipconfig"], capture_output=True, text=True)
                
                # Extract IPv4 Addresses
                ips = re.findall(r'IPv4 Address[ .]*: ([\d\.]+)', result.stdout)
                if not ips:
                     ips = re.findall(r'(\d+\.\d+\.\d+\.\d+)', result.stdout)

                for ip in ips:
                    if ip.startswith("127.") or ip.startswith("169.254.") or ip.endswith(".255") or ip == "0.0.0.0":
                        continue
                    
                    excluded_ips.add(ip)
                    subnet = ".".join(ip.split('.')[:-1])
                    subnets.add(subnet)

                # Extract Default Gateways
                gateways = re.findall(r'Default Gateway[ .]*: ([\d\.]+)', result.stdout)
                for gw in gateways:
                    if gw and gw != "0.0.0.0":
                        excluded_ips.add(gw)

            except Exception as e:
                pass
            
            # 2. Add standard fallbacks
            subnets.add("192.168.0")
            subnets.add("192.168.1")
            subnets.add("192.168.8")    # Common Huawei/TP-Link
            subnets.add("192.168.10")
            subnets.add("192.168.31")   # Xiaomi
            subnets.add("192.168.43")   # Android Hotspot
            subnets.add("172.20.10")    # iPhone Hotspot
            subnets.add("10.0.0")       # Common corporate/home
            
            # 3. Generate Targets
            target_ips = []
            for sub in subnets:
                for i in range(2, 255): 
                    ip = f"{sub}.{i}"
                    target_ips.append(ip)
            
            # Dedup
            target_ips = list(set(target_ips))
            
            # Remove excluded IPs
            final_targets = []
            for ip in target_ips:
                if ip not in excluded_ips and not ip.endswith(".1"):
                    final_targets.append(ip)
            
            total_targets = len(final_targets)
            self.after(0, lambda: self.status_label.configure(text=f"Scanning {len(subnets)} subnets ({total_targets} IP)..."))
            
            # 4. Active Wake-Up Ping
            def check_ip(ip):
                if self.cancelled: return None
                try:
                    args = ['ping', '-n', '1', '-w', '300', ip] if sys.platform == 'win32' else ['ping', '-c', '1', '-W', '0.3', ip]
                    
                    startupinfo = None
                    if sys.platform == 'win32':
                        startupinfo = subprocess.STARTUPINFO()
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                        
                    res = subprocess.run(
                        args, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL,
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                    )
                    return ip if res.returncode == 0 else None
                except:
                    return None

            # 5. Execute with Progress Updates
            scanned = 0
            found = 0
            
            self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=300)
            futures = {self.executor.submit(check_ip, ip): ip for ip in final_targets}
            
            for future in concurrent.futures.as_completed(futures):
                if self.cancelled: break
                
                scanned += 1
                result = future.result()
                if result:
                    found += 1
                    found_ips.append(result)
                
                if scanned % 2 == 0 or scanned == total_targets:
                     self.after(0, lambda s=scanned, t=total_targets, f=found: self._update_progress(s, t, f))
            
            if not self.cancelled:
                self.after(0, lambda: self._finish(found_ips))
                
        except Exception as e:
            if not self.cancelled:
                 self.after(0, lambda: self._finish([]))

    def _finish(self, ips):
        if self.on_complete:
            self.on_complete(ips)
        if self.winfo_exists():
            self.destroy()
