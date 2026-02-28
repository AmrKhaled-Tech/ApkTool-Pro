# -*- coding: utf-8 -*-
"""
ADB Manager for MyApkTool
Handles Android Debug Bridge operations for device management
"""

import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class Device:
    """Represents an Android device"""
    id: str
    status: str
    model: str = ""
    product: str = ""
    transport: str = ""  # usb or wifi
    
    def __str__(self):
        return f"{self.id} - {self.model or self.product or 'Unknown'} ({self.status})"


@dataclass
class Package:
    """Represents an installed package"""
    name: str
    version_name: str = ""
    version_code: str = ""
    apk_path: str = ""
    size: int = 0
    is_system: bool = False
    
    # Advanced Dumpsys Info
    min_sdk: str = ""
    target_sdk: str = ""
    install_time: str = ""
    update_time: str = ""
    uid: str = ""
    data_dir: str = ""
    installer: str = ""
    permissions: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    is_test_only: bool = False
    is_debuggable: bool = False
    
    def __str__(self):
        size_mb = f"{self.size / (1024*1024):.1f} MB" if self.size > 0 else "N/A"
        return f"{self.name} v{self.version_name} ({size_mb})"


class ADBManager:
    """Manages ADB operations for Android devices"""
    
    def __init__(self, adb_path: Optional[Path] = None, logger: Optional[Callable] = None):
        """
        Initialize ADB Manager
        
        Args:
            adb_path: Path to adb executable (auto-detect if None)
            logger: Callback function for logging (signature: logger(message, level))
        """
        self.adb_path = adb_path or self.detect_adb_path()
        self.logger = logger or self._default_logger
        self.current_device = None
        
        if not self.adb_path:
            self.logger("⚠️ ADB not found. Please install Android SDK Platform Tools.", "warning")
    
    def _default_logger(self, message: str, level: str = "info"):
        """Default logger if none provided"""
        print(f"[{level.upper()}] {message}")
    
    @staticmethod
    def detect_adb_path() -> Optional[Path]:
        """Auto-detect ADB executable path"""
        # Common ADB locations
        possible_paths = [
            Path("tools/adb.exe"),  # Local tools folder
            Path("Resources/adb.exe"),  # Local tools folder
            Path("tools/platform-tools/adb.exe"),
            Path(r"C:\Android\platform-tools\adb.exe"),
            Path(r"C:\Users") / Path.home().name / "AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe",
        ]
        
        # Check each path
        for path in possible_paths:
            if path.exists():
                return path
        
        # Try system PATH
        try:
            result = subprocess.run(["adb", "version"], capture_output=True, timeout=2)
            if result.returncode == 0:
                return Path("adb")  # In PATH
        except:
            pass
        
        return None
    
    def _run_adb(self, args: List[str], device_id: Optional[str] = None, timeout: int = 30) -> Tuple[bool, str]:
        """
        Run ADB command
        
        Args:
            args: ADB command arguments
            device_id: Specific device ID (None for default)
            timeout: Command timeout in seconds
            
        Returns:
            (success, output)
        """
        if not self.adb_path:
            return False, "ADB not found"
        
        # Build command
        cmd = [str(self.adb_path)]
        
        # Add device selector if specified
        if device_id:
            cmd.extend(["-s", device_id])
        
        cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            output = result.stdout + result.stderr
            success = result.returncode == 0
            
            return success, output.strip()
            
        except subprocess.TimeoutExpired:
            return False, f"Command timed out after {timeout}s"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_devices(self) -> List[Device]:
        """
        Get list of connected devices
        
        Returns:
            List of Device objects
        """
        success, output = self._run_adb(["devices", "-l"])
        
        if not success:
            self.logger(f"Failed to check devices: {output}", "error")
            return []
        
        devices = []
        lines = output.split('\n')[1:]  # Skip header
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse device line: ID STATUS product:X model:Y device:Z transport_id:N
            parts = line.split()
            if len(parts) < 2:
                continue
            
            device_id = parts[0]
            status = parts[1]
            
            # Parse properties
            properties = {}
            for part in parts[2:]:
                if ':' in part:
                    key, value = part.split(':', 1)
                    properties[key] = value
            
            device = Device(
                id=device_id,
                status=status,
                model=properties.get('model', ''),
                product=properties.get('product', ''),
                transport=self._detect_transport(device_id)
            )
            
            devices.append(device)
        
        return devices
    
    def _detect_transport(self, device_id: str) -> str:
        """Detect if device is connected via USB or WiFi"""
        if ':' in device_id:  # WiFi devices have IP:PORT format
            return "wifi"
        return "usb"
    
    def connect_wifi(self, ip: str, port: int = 5555) -> Tuple[bool, str]:
        """
        Connect to device over WiFi
        
        Args:
            ip: Device IP address
            port: ADB port (default: 5555)
            
        Returns:
            (success, message)
        """
        self.logger(f"Connecting to {ip}:{port}...", "info")
        
        success, output = self._run_adb(["connect", f"{ip}:{port}"])
        
        if success and ("connected" in output.lower() or "already connected" in output.lower()):
            self.current_device = f"{ip}:{port}"
            self.logger(f"✓ Connected to {ip}:{port}", "success")
            return True, output
        else:
            self.logger(f"✗ Failed to connect: {output}", "error")
            return False, output
    
    def disconnect(self, device_id: Optional[str] = None) -> bool:
        """Disconnect from device (WiFi connections)"""
        target = device_id or self.current_device or "all"
        
        if target == "all":
            success, output = self._run_adb(["disconnect"])
        else:
            success, output = self._run_adb(["disconnect", target])
        
        if success:
            self.logger(f"✓ Disconnected from {target}", "success")
            if target == self.current_device:
                self.current_device = None
        
        return success
    
    def enable_wifi_debugging(self, device_id: Optional[str] = None) -> Tuple[bool, str, int]:
        """
        Enable WiFi debugging on USB-connected device
        
        Returns:
            (success, ip_address, port)
        """
        target = device_id or self.current_device
        
        # Enable tcpip mode on port 5555
        success, output = self._run_adb(["tcpip", "5555"], device_id=target)
        
        if not success:
            return False, "", 0
        
        # Get device IP
        ip = self.get_device_ip(target)
        
        if ip:
            self.logger(f"✓ WiFi debugging enabled: {ip}:5555", "success")
            return True, ip, 5555
        else:
            return False, "", 0
    
    def get_device_ip(self, device_id: Optional[str] = None) -> str:
        """Get device IP address"""
        target = device_id or self.current_device
        
        # Try to get IP from wlan0
        success, output = self._run_adb(["shell", "ip", "addr", "show", "wlan0"], device_id=target)
        
        if success:
            # Parse IP address from output
            match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', output)
            if match:
                return match.group(1)
        
        return ""
    
    def list_packages(self, device_id: Optional[str] = None, filter_type: str = "all") -> List[Package]:
        """
        List installed packages (Comprehensive)
        
        Args:
            device_id: Device ID (None for current)
            filter_type: "all", "user", or "system"
        """
        target = device_id or self.current_device
        
        # Get package list (-u for uninstalled/data-only inclusion)
        args = ["shell", "pm", "list", "packages", "-f", "-u"]
        
        if filter_type == "user":
            args.append("-3")  # Third-party apps only
        elif filter_type == "system":
            args.append("-s")  # System apps only
        
        success, output = self._run_adb(args, device_id=target, timeout=60)
        
        if not success:
            self.logger(f"Failed to list packages: {output}", "error")
            return []
        
        packages = []
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or not line.startswith('package:'):
                continue
            
            try:
                # Parse: package:/path/to/base.apk=com.example.app
                # Or: package:com.example.app (if path hidden/missing)
                # Regex is safer for varying outputs
                # Match "package:" + (optional path) + "=" + (package_name)
                # OR match "package:" + (package_name)
                
                # 1. Try path=name format
                if '=' in line:
                    parts = line.split('=')
                    apk_path = parts[0].replace('package:', '').strip()
                    package_name = parts[-1].strip() # Take last part in case of weird paths
                else:
                    # 2. Try name only format
                    package_name = line.replace('package:', '').strip()
                    apk_path = ""
                
                if not package_name: continue

                # Get package details
                pkg = Package(
                    name=package_name,
                    apk_path=apk_path,
                    is_system=apk_path.startswith('/system') or apk_path.startswith('/product') or apk_path.startswith('/apex') or apk_path.startswith('/vendor')
                )
                
                packages.append(pkg)
                
            except Exception:
                continue
        
        self.logger(f"Found {len(packages)} packages", "info")
        return packages
    
    def get_package_info(self, package_name: str, device_id: Optional[str] = None) -> Optional[Package]:
        """Get detailed package information"""
        target = device_id or self.current_device
        
        # 1. Get Path (Fast check)
        success, path_out = self._run_adb(["shell", "pm", "path", package_name], device_id=target)
        if not success or not path_out:
            return None
        
        # Handle multiple paths (split APKs), take base
        apk_path = ""
        for line in path_out.split('\n'):
            if 'base.apk' in line or (line.strip().startswith('package:') and not apk_path):
                apk_path = line.replace('package:', '').strip()
                
        if not apk_path:
             apk_path = path_out.split('\n')[0].replace('package:', '').strip()

        # Initialize Package
        pkg = Package(name=package_name, apk_path=apk_path)
        pkg.is_system = apk_path.startswith('/system') or apk_path.startswith('/product') or apk_path.startswith('/vendor') or apk_path.startswith('/apex')

        # 2. Get Detailed Dump
        success, dump = self._run_adb(["shell", "dumpsys", "package", package_name], device_id=target)
        if success:
            for line in dump.split('\n'):
                line = line.strip()
                
                # Independent checks for properties that may share a line
                if 'versionName=' in line:
                    try: pkg.version_name = line.split('versionName=')[1].split()[0]
                    except: pass
                
                if 'versionCode=' in line:
                    match = re.search(r'versionCode=(\d+)', line)
                    if match: pkg.version_code = match.group(1)
                
                if 'minSdk=' in line:
                    match = re.search(r'minSdk=(\d+)', line)
                    if match: pkg.min_sdk = match.group(1)
                    
                if 'targetSdk=' in line:
                    match = re.search(r'targetSdk=(\d+)', line)
                    if match: pkg.target_sdk = match.group(1)
                    
                # Time Info
                elif 'firstInstallTime=' in line:
                    pkg.install_time = line.split('=', 1)[1].strip()
                elif 'lastUpdateTime=' in line:
                    pkg.update_time = line.split('=', 1)[1].strip()
                    
                # Meta
                elif 'installerPackageName=' in line:
                    pkg.installer = line.split('=', 1)[1]
                elif 'dataDir=' in line:
                    pkg.data_dir = line.split('=', 1)[1]
                elif 'appId=' in line:
                    pkg.uid = line.split('=', 1)[1]
                    
                # Flags
                elif 'flags=[' in line:
                    try:
                        # Extract content between [ and ]
                        content = line.split('flags=[')[1].split(']')[0]
                        pkg.flags = [f.strip() for f in content.split() if f.strip()]
                        
                        # Update helpers
                        if 'DEBUGGABLE' in pkg.flags: pkg.is_debuggable = True
                        if 'TEST_ONLY' in pkg.flags: pkg.is_test_only = True
                        if 'SYSTEM' in pkg.flags: pkg.is_system = True
                    except:
                        pass

        # 3. Get Size
        success, size_output = self._run_adb(["shell", "du", "-b", apk_path], device_id=target)
        if success:
            try:
                pkg.size = int(size_output.split()[0])
            except:
                pass
        
        return pkg
    
    def backup_apk(self, package_name: str, output_dir: str, device_id: Optional[str] = None) -> Tuple[bool, str]:
        import posixpath
        target = device_id or self.current_device
        self.logger(f"🔍 Deep scanning: {package_name}", "info")
        
        # 1. جلب المخرجات الخام
        success, output = self._run_adb(["shell", "pm", "path", package_name], device_id=target)
        
        if not success or not output:
            self.logger(f"✗ Package {package_name} not found.", "error")
            return False, ""

        # 2. الحل الجذري: تقسيم النص بناءً على كلمة "package:" وليس بناءً على السطور
        paths = []
        found_paths = re.findall(r'package:(.*?\.apk)', output)
        
        for p in found_paths:
            clean_p = p.strip()
            if clean_p:
                paths.append(clean_p)

        # إزالة التكرار
        paths = list(dict.fromkeys(paths))

        if not paths:
            self.logger("✗ No valid APK paths could be parsed.", "error")
            return False, ""

        # 3. تحديد نوع التطبيق (Single أو Split)
        is_split = len(paths) > 1
        
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        # ==========================================
        # الحالة الأولى: ملف واحد فقط
        # ==========================================
        if not is_split:
            remote_file = paths[0]
            local_file = out_path / f"{package_name}.apk"
            
            self.logger(f"ℹ Single APK detected.", "info")
            ok, err = self._run_adb(["pull", remote_file, str(local_file)], device_id=target, timeout=300)
            
            if ok and local_file.exists():
                self.logger(f"✓ Backup saved: {local_file.name}", "success")
                return True, str(local_file)
            else:
                self.logger(f"✗ Backup failed: {err}", "error")
                return False, ""

        # ==========================================
        # الحالة الثانية: Split APKs (مثل فيسبوك)
        # ==========================================
        else:
            self.logger(f"🚀 Split APKs detected! Found {len(paths)} parts.", "info")
            
            # إنشاء المجلد المحلي
            package_folder = out_path / package_name
            package_folder.mkdir(parents=True, exist_ok=True)
            
            success_count = 0
            for i, remote_p in enumerate(paths):
                filename = posixpath.basename(remote_p)
                local_dest = package_folder / filename
                
                self.logger(f"  ⬇ [{i+1}/{len(paths)}] Pulling: {filename}", "info")
                
                ok, err = self._run_adb(["pull", remote_p, str(local_dest)], device_id=target, timeout=60)
                
                if ok and local_dest.exists():
                    success_count += 1
                else:
                    self.logger(f"  ⚠ Failed to pull {filename}: {err}", "warning")

            if success_count > 0:
                self.logger(f"✓ Backup complete: {success_count} parts saved in /{package_name}", "success")
                return True, str(package_folder)
            else:
                self.logger("✗ Critical failure: No parts were downloaded.", "error")
                return False, ""

    def uninstall_package(self, package_name: str, device_id: Optional[str] = None, keep_data: bool = False) -> Tuple[bool, str]:
        """
        Uninstall package from device
        
        Args:
            package_name: Package name
            device_id: Device ID
            keep_data: Keep app data
            
        Returns:
            (success, message)
        """
        target = device_id or self.current_device
        self.logger(f"Uninstalling {package_name}...", "info")
        
        args = ["uninstall"]
        if keep_data:
            args.append("-k")
        args.append(package_name)
        
        success, output = self._run_adb(args, device_id=target)
        
        if success and "Success" in output:
            self.logger(f"✓ Uninstall complete", "success")
            return True, output
        else:
            self.logger(f"✗ Uninstall failed: {output}", "error")
            return False, output

