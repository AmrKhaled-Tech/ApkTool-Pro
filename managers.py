"""
MyApkTool - Tool Managers Module
All tool managers for APK operations: decompile, compile, sign, zipalign, etc.
"""

import os
import subprocess
import shutil
import re
from pathlib import Path
from typing import Optional, Callable, Dict, List, Tuple

from config import AppSettings, PathManager, JavaUtils


# ============================================================================
# BASE TOOL MANAGER
# ============================================================================

class BaseToolManager:
    """Base class for tool managers"""
    
    def __init__(self, logger_callback: Callable[[str, str], None], settings: Optional[AppSettings] = None):
        self.logger = logger_callback
        self.settings = settings
        self.base_dir = PathManager.get_base_dir()
        self.cancellation_check = None  # Function that returns True if cancelled
    
    def _run_command(self, command: List[str], cwd: Optional[Path] = None, env: Optional[Dict] = None) -> Tuple[bool, str]:
        """Run a command and capture output"""
        try:
            # Add Java flags if this is a Java command
            if command and command[0].lower() == "java":
                # Insert Java flags after 'java' but before '-jar'
                java_flags = [
                    "--add-opens", "java.base/sun.security.rsa=ALL-UNNAMED",
                    "--add-opens", "java.base/java.util=ALL-UNNAMED",
                    "--add-opens", "java.base/java.lang.invoke=ALL-UNNAMED"
                ]
                # Custom Java Path & Heap
                java_cmd = "java"
                heap_flags = []
                
                if self.settings:
                    if self.settings.java_path and self.settings.java_path.strip():
                        java_cmd = self.settings.java_path
                    if self.settings.heap_size > 0:
                        heap_flags = [f"-Xmx{self.settings.heap_size}m"]

                # Insert flags
                # command[0] is 'java' (or similar), we replace it with configured java_cmd
                # Then add heap flags
                # Then add java module flags
                command = [java_cmd] + heap_flags + java_flags + command[1:]
            
            cmd = []
            for part in command:
                if os.path.exists(str(part)) or '\\' in str(part) or '/' in str(part):
                    cmd.append(PathManager.quote_path(str(part)))
                else:
                    cmd.append(str(part))
            
            self.logger(f"Running: {' '.join(cmd)}", "info")
            
            process = subprocess.Popen(
                ' '.join(cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(cwd) if cwd else None,
                env=env, # Pass custom environment
                shell=True
            )
            
            output = []
            for line in iter(process.stdout.readline, ''):
                # Check for cancellation
                if self.cancellation_check and self.cancellation_check():
                    self.logger("🛑 Operation cancelled by user.", "warning")
                    process.terminate()  # Try graceful termination
                    return False, "Cancelled by user"

                if line:
                    line = line.rstrip()
                    output.append(line)
                    
                    # Skip Java warning lines
                    if 'WARNING' in line and 'illegal reflective access' in line.lower():
                        continue
                    if 'Use --add-opens' in line:
                        continue
                    
                    # Check for Java 9+ Modularization Warnings (if suppressed)
                    if self.settings and getattr(self.settings, 'suppress_java_warnings', True):
                        if "WARNING: A restricted method in java.lang.System has been called" in line: continue
                        if "WARNING: java.lang.System::loadLibrary has been called" in line: continue
                        if "WARNING: Use --enable-native-access" in line: continue
                        if "WARNING: Restricted methods will be blocked" in line: continue
                    
                    line_lower = line.lower()
                    if any(word in line_lower for word in ['error', 'fail', 'exception']):
                        self.logger(line, "error")
                    elif any(word in line_lower for word in ['warning', 'skip']):
                        self.logger(line, "warning")
                    elif any(word in line_lower for word in ['success', 'done', 'complete']):
                        self.logger(line, "success")
                    else:
                        self.logger(line, "info")
            
            process.wait()
            full_output = '\n'.join(output)
            return process.returncode == 0, full_output
            
        except Exception as e:
            error_msg = f"Command failed: {str(e)}"
            self.logger(error_msg, "error")
            return False, error_msg


# ============================================================================
# APKTOOL MANAGER
# ============================================================================

class ApktoolManager(BaseToolManager):
    """Manage Apktool operations"""
    
    
    def __init__(self, logger_callback: Callable, settings: AppSettings):
        super().__init__(logger_callback, settings)  # Pass settings to base
        self.workspace_dir = self.base_dir / "workspace"
        self.framework_dir = self.base_dir / "framework"
        
    def _get_apktool_path(self) -> Optional[Path]:
        """Resolve Apktool path dynamically"""
        # Default internal path
        path = PathManager.get_tool_path("apktool.jar")
        
        # Check for Custom Version
        if self.settings and self.settings.use_custom_apktool and self.settings.custom_apktool_path:
            # If path is just filename (from combo), look in tools/custom
            if "\\" not in self.settings.custom_apktool_path and "/" not in self.settings.custom_apktool_path:
                 custom_path = self.base_dir / "tools" / "custom" / self.settings.custom_apktool_path
            else:
                 custom_path = Path(self.settings.custom_apktool_path)

            if custom_path.exists():
                return custom_path
            else:
                self.logger(f"Custom Apktool not found at {custom_path}, using default.", "warning")
        
        return path

    def _get_aapt_path(self) -> Optional[Path]:
        """Resolve Custom AAPT path dynamically"""
        if self.settings and self.settings.use_custom_aapt and self.settings.custom_aapt_path:
            # If path is just filename, look in tools/custom
            if "\\" not in self.settings.custom_aapt_path and "/" not in self.settings.custom_aapt_path:
                 custom_path = self.base_dir / "tools" / "custom" / self.settings.custom_aapt_path
            else:
                 custom_path = Path(self.settings.custom_aapt_path)

            if custom_path.exists():
                return custom_path
        return None

    def _get_aapt2_path(self) -> Optional[Path]:
        """Resolve Custom AAPT2 path dynamically"""
        if self.settings and self.settings.use_custom_aapt2 and self.settings.custom_aapt2_path:
            # If path is just filename, look in tools/custom
            if "\\" not in self.settings.custom_aapt2_path and "/" not in self.settings.custom_aapt2_path:
                 custom_path = self.base_dir / "tools" / "custom" / self.settings.custom_aapt2_path
            else:
                 custom_path = Path(self.settings.custom_aapt2_path)

            if custom_path.exists():
                return custom_path
        return None

    def decompile(self, apk_path: str, output_folder: Optional[str] = None) -> Tuple[bool, str]:
        """Decompile APK using Apktool"""
        self.apktool_path = self._get_apktool_path()
        if not self.apktool_path:
            return False, "apktool.jar not found"
        
        apk_name = Path(apk_path).stem
        output = Path(output_folder) if output_folder else (self.workspace_dir / apk_name)
        
        if output.exists():
            self.logger(f"Removing existing folder: {output}", "warning")
            shutil.rmtree(output)
        
        command = ["java", "-jar", str(self.apktool_path), "d", apk_path, "-o", str(output), "-f"]
        
        # Add options
        if not self.settings.decode_resources:
            command.append("-r")
        if not self.settings.decode_sources:
            command.append("-s")
        # Prepare Environment
        env = os.environ.copy()
        
        # Add Custom AAPT2 to PATH if selected
        if self.settings.use_aapt2:
            command.extend(["--use-aapt2"])
            aapt2_path = self._get_aapt2_path()
            if aapt2_path:
                self.logger(f"Custom AAPT2 selected: {aapt2_path.name}", "info")
                # Prepend to PATH so Apktool finds this aapt2 first
                env["PATH"] = str(aapt2_path.parent) + os.pathsep + env["PATH"]
                self.logger(f"Injecting into PATH: {aapt2_path.parent}", "info")

        # Custom AAPT (1) Logic
        aapt_path = self._get_aapt_path()
        if aapt_path:
             self.logger(f"Custom AAPT selected: {aapt_path.name}", "info")
             command.extend(["--aapt", str(aapt_path)])
        
        # Framework path
        command.extend(["-p", str(self.framework_dir)])
        
        self.logger(f"Starting Apktool ({self.apktool_path.name})...", "info")
        success, _ = self._run_command(command, env=env)
        
        if success:
            self.logger(f"✓ Decompilation complete: {output}", "success")
            # Mark as Apktool project
            marker_file = output / ".apktool_project"
            marker_file.touch()
        
        return success, str(output)
    
    def compile(self, folder_path: str) -> Tuple[bool, str]:
        """Compile APK using Apktool"""
        self.apktool_path = self._get_apktool_path()
        if not self.apktool_path:
            return False, "apktool.jar not found"
        
        folder = Path(folder_path)
        output_apk = folder / "dist" / f"{folder.name}.apk"
        
        command = ["java", "-jar", str(self.apktool_path), "b", str(folder), "-f"]
        
        # Prepare Environment
        env = os.environ.copy()

        # Add options
        if self.settings.use_aapt2:
            command.append("--use-aapt2")
            
            # Custom AAPT2
            aapt2_path = self._get_aapt2_path()
            if aapt2_path:
                # Prepend to PATH
                env["PATH"] = str(aapt2_path.parent) + os.pathsep + env["PATH"]

            aapt_path = self._get_aapt_path()
            if aapt_path:
                 command.extend(["--aapt", str(aapt_path)])
        
        # Framework path
        command.extend(["-p", str(self.framework_dir)])
        
        self.logger(f"Starting Apktool ({self.apktool_path.name})...", "info")
        success, _ = self._run_command(command, env=env)
        
        if success and output_apk.exists():
            self.logger(f"✓ Build complete: {output_apk}", "success")
            return True, str(output_apk)
        
        return False, ""


# ============================================================================
# APKEDITOR MANAGER
# ============================================================================

class APKEditorManager(BaseToolManager):
    """Manage APKEditor operations"""
    
    def __init__(self, logger_callback: Callable, settings: Optional[AppSettings] = None):
        super().__init__(logger_callback, settings)
        self.apkeditor_path = PathManager.get_tool_path("APKEditor.jar")
        self.workspace_dir = self.base_dir / "workspace"
    
    def decompile(self, apk_path: str, output_folder: Optional[str] = None) -> Tuple[bool, str]:
        """Decompile APK using APKEditor"""
        if not self.apkeditor_path:
            return False, "APKEditor.jar not found"
        
        apk_name = Path(apk_path).stem
        output = Path(output_folder) if output_folder else (self.workspace_dir / apk_name)
        
        if output.exists():
            shutil.rmtree(output)
        
        command = ["java", "-jar", str(self.apkeditor_path), "d", "-i", apk_path, "-o", str(output)]
        
        self.logger("Starting APKEditor decompilation...", "info")
        success, _ = self._run_command(command)
        
        if success:
            self.logger(f"✓ Decompilation complete: {output}", "success")
            # Mark as APKEditor project
            marker_file = output / ".apkeditor_project"
            marker_file.touch()
        
        return success, str(output)
    
    def compile(self, folder_path: str) -> Tuple[bool, str]:
        """Compile APK using APKEditor"""
        if not self.apkeditor_path:
            return False, "APKEditor.jar not found"
        
        folder = Path(folder_path)
        output_apk = self.base_dir / "output" / f"{folder.name}_compiled.apk"
        
        command = ["java", "-jar", str(self.apkeditor_path), "b", "-i", str(folder), "-o", str(output_apk)]
        
        self.logger("Starting APKEditor compilation...", "info")
        success, _ = self._run_command(command)
        
        if success and output_apk.exists():
            self.logger(f"✓ Build complete: {output_apk}", "success")
            return True, str(output_apk)
        
        return False, ""
    
    def merge_bundle(self, bundle_path: str, output_apk: str) -> Tuple[bool, str]:
        """Merge XAPK/APKS/APKM to single APK using APKEditor"""
        if not self.apkeditor_path:
            return False, "APKEditor.jar not found"
        
        command = ["java", "-jar", str(self.apkeditor_path), "m", "-i", bundle_path, "-o", output_apk]
        
        self.logger(f"Merging bundle: {Path(bundle_path).name}", "info")
        success, _ = self._run_command(command)
        
        if success:
            self.logger(f"✓ Merge complete: {output_apk}", "success")
            return True, output_apk
        
        return False, ""


# ============================================================================
# ZIPALIGN MANAGER
# ============================================================================

class ZipalignManager(BaseToolManager):
    """Manage Zipalign operations"""
    
    def __init__(self, logger_callback: Callable, settings: Optional[AppSettings] = None):
        super().__init__(logger_callback, settings)
        self.zipalign_path = PathManager.get_tool_path("zipalign.exe")
    
    def zipalign(self, input_apk: str, output_apk: Optional[str] = None, alignment: int = 4) -> Tuple[bool, str]:
        """Zipalign an APK"""
        if not self.zipalign_path:
            return False, "zipalign.exe not found"
        
        # Check alignment setting if available
        if self.settings and self.settings.zipalign_alignment:
            alignment = self.settings.zipalign_alignment
        
        if not output_apk:
            input_path = Path(input_apk)
            output_apk = str(input_path.parent / f"{input_path.stem}_aligned.apk")
        
        command = [str(self.zipalign_path), "-f", str(alignment), input_apk, output_apk]
        
        self.logger(f"Zipaligning APK (alignment: {alignment})...", "info")
        success, _ = self._run_command(command)
        
        if success:
            self.logger(f"✓ Zipalign complete: {output_apk}", "success")
            return True, output_apk
        
        return False, ""


# ============================================================================
# SIGNING MANAGER
# ============================================================================

class SigningManager(BaseToolManager):
    """Manage APK signing operations"""
    
    def __init__(self, logger_callback: Callable, settings: AppSettings):
        super().__init__(logger_callback, settings)
        self.testkey_pk8 = PathManager.get_tool_path("testkey.pk8")
        self.testkey_pem = PathManager.get_tool_path("testkey.x509.pem")

    def _get_signer_path(self) -> Optional[Path]:
        """Resolve apksigner path dynamically"""
        if self.settings and self.settings.apksigner_path and os.path.exists(self.settings.apksigner_path):
            return Path(self.settings.apksigner_path)
        return PathManager.get_tool_path("apksigner.jar")
    
    def _generate_debug_keystore(self, target_path: Path):
        """Generate a fallback debug keystore"""
        try:
            self.logger("⚠ Generating temp debug keystore...", "warning")
            # Find keytool using JavaUtils/Settings
            java_path = self.settings.java_path if self.settings else ""
            keytool = JavaUtils.find_keytool_path(java_path)
            if not keytool:
                keytool = "keytool"

            cmd = [
                keytool, "-genkey", "-v", 
                "-keystore", str(target_path),
                "-storepass", "android",
                "-alias", "androiddebugkey",
                "-keypass", "android", 
                "-keyalg", "RSA", 
                "-keysize", "2048", 
                "-validity", "10000",
                "-dname", "CN=Android Debug,O=Android,C=US"
            ]
            
            # Run without shell window
            subprocess.run(
                cmd, 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
            )
            self.logger(f"✓ Created debug.keystore", "success")
        except Exception as e:
            self.logger(f"Failed to generate debug keystore: {e}", "error")

    def sign(self, input_apk: str, output_apk: Optional[str] = None) -> Tuple[bool, str]:
        """Sign APK using apksigner"""
        self.apksigner_path = self._get_signer_path()
        if not self.apksigner_path:
            return False, "apksigner.jar not found"
        
        if not output_apk:
            input_path = Path(input_apk)
            output_apk = str(input_path.parent / f"{input_path.stem}_signed.apk")
        
        # Prepare Signing Credentials
        keystore_args = []
        
        if self.settings.use_custom_keystore and self.settings.keystore_path:
            # Custom Keystore Logic
            keystore_path = Path(self.settings.keystore_path)
            if not keystore_path.exists():
                # Try keys/ directory
                possible_path = self.base_dir / "keys" / self.settings.keystore_path
                if possible_path.exists():
                    keystore_path = possible_path
                else:
                     return False, f"Custom keystore not found: {self.settings.keystore_path}"
            
            keystore_args = [
                "--ks", str(keystore_path),
            ]
            if self.settings.keystore_pass:
                keystore_args.extend(["--ks-pass", f"pass:{self.settings.keystore_pass}"])
            if self.settings.key_alias:
                keystore_args.extend(["--ks-key-alias", self.settings.key_alias])
            if self.settings.key_pass:
                 keystore_args.extend(["--key-pass", f"pass:{self.settings.key_pass}"])
        else:
             # Default / Test Key Logic
             pk8 = PathManager.get_tool_path("testkey.pk8")
             pem = PathManager.get_tool_path("testkey.x509.pem")
             
             if pk8 and pem and pk8.exists() and pem.exists():
                 # Use standard test keys
                 keystore_args = [
                    "--key", str(pk8),
                    "--cert", str(pem)
                ]
             else:
                 # Fallback to debug.keystore
                 debug_ks = self.base_dir / "tools" / "debug.keystore"
                 if not debug_ks.exists():
                      self._generate_debug_keystore(debug_ks)
                 
                 if debug_ks.exists():
                     keystore_args = [
                         "--ks", str(debug_ks),
                         "--ks-pass", "pass:android",
                         "--ks-key-alias", "androiddebugkey",
                         "--key-pass", "pass:android"
                     ]
                     self.logger("Using fallback debug.keystore", "info")
                 else:
                     return False, "No test keys found and failed to generate debug keystore."

        # Build command with signature schemes BEFORE --out parameter
        command = [
            "java", "-jar", str(self.apksigner_path), "sign"
        ] + keystore_args
        
        # Add signature schemes (must come before --out)
        if self.settings.v1_signing:
            command.extend(["--v1-signing-enabled", "true"])
        if self.settings.v2_signing:
            command.extend(["--v2-signing-enabled", "true"])
        if self.settings.v3_signing:
            command.extend(["--v3-signing-enabled", "true"])
        
        # Now add output and input files
        command.extend(["--out", output_apk, input_apk])
        
        self.logger("Signing APK with testkey...", "info")
        success, _ = self._run_command(command)
        
        if success:
            self.logger(f"✓ Signing complete: {output_apk}", "success")
            return True, output_apk
        
        # Log failure details if not already logged
        self.logger(f"❌ Signing failed. Output:\n{output}", "error")
        return False, output


# ============================================================================
# BAKSMALI MANAGER
# ============================================================================

class BaksmaliManager(BaseToolManager):
    """Manage Baksmali/Smali operations"""
    
    def __init__(self, logger_callback: Callable, settings: Optional[AppSettings] = None):
        super().__init__(logger_callback, settings)
        self.baksmali_path = PathManager.get_tool_path("baksmali.jar")
        self.smali_path = PathManager.get_tool_path("smali.jar")
    
    def baksmali(self, dex_file: str, output_dir: str) -> Tuple[bool, str]:
        """Disassemble DEX to Smali"""
        if not self.baksmali_path:
            return False, "baksmali.jar not found"
        
        command = ["java", "-jar", str(self.baksmali_path), "d", dex_file, "-o", output_dir]
        
        self.logger("Disassembling DEX file...", "info")
        success, _ = self._run_command(command)
        
        if success:
            self.logger(f"✓ Baksmali complete: {output_dir}", "success")
            return True, output_dir
        
        return False, ""
    
    def smali(self, smali_dir: str, output_dex: str) -> Tuple[bool, str]:
        """Assemble Smali to DEX"""
        if not self.smali_path:
            return False, "smali.jar not found"
        
        command = ["java", "-jar", str(self.smali_path), "a", smali_dir, "-o", output_dex]
        
        self.logger("Assembling Smali files...", "info")
        success, _ = self._run_command(command)
        
        if success:
            self.logger(f"✓ Smali complete: {output_dex}", "success")
            return True, output_dex
        
        return False, ""


# ============================================================================
# FRAMEWORK MANAGER
# ============================================================================

class FrameworkManager(BaseToolManager):
    """Manage Apktool framework operations"""
    
    def __init__(self, logger_callback: Callable, settings: Optional[AppSettings] = None):
        super().__init__(logger_callback, settings)
        self.apktool_path = PathManager.get_tool_path("apktool.jar")
        self.framework_dir = self.base_dir / "framework"
    
    def install_framework(self, framework_apk: str) -> Tuple[bool, str]:
        """Install framework APK"""
        if not self.apktool_path:
            return False, "apktool.jar not found"
        
        command = ["java", "-jar", str(self.apktool_path), "if", framework_apk, "-p", str(self.framework_dir)]
        
        self.logger(f"Installing framework: {Path(framework_apk).name}", "info")
        success, output = self._run_command(command)
        
        if success:
            self.logger("✓ Framework installed", "success")
        
        return success, output
    
    def clear_framework(self) -> bool:
        """Clear all installed frameworks"""
        try:
            if self.framework_dir.exists():
                for item in self.framework_dir.glob("*"):
                    if item.is_file():
                        item.unlink()
                self.logger("✓ Framework cache cleared", "success")
                return True
        except Exception as e:
            self.logger(f"Error clearing framework: {e}", "error")
        return False


# ============================================================================
# AAPT MANAGER
# ============================================================================

class AAPTManager(BaseToolManager):
    """Manage AAPT operations for APK info"""
    
    def __init__(self, logger_callback: Callable, settings: Optional[AppSettings] = None):
        super().__init__(logger_callback, settings)
        self.aapt_path = PathManager.get_tool_path("aapt.exe")

    def _get_aapt_path(self) -> Optional[Path]:
        """Resolve AAPT path dynamically"""
        if self.settings and self.settings.use_custom_aapt and self.settings.custom_aapt_path:
             # If path is just filename (from combo), look in tools/custom
            if "\\" not in self.settings.custom_aapt_path and "/" not in self.settings.custom_aapt_path:
                 custom_path = self.base_dir / "tools" / "custom" / self.settings.custom_aapt_path
            else:
                 custom_path = Path(self.settings.custom_aapt_path)

            if custom_path.exists():
                return custom_path
                
        return PathManager.get_tool_path("aapt.exe")
    
    def get_apk_info(self, apk_path: str) -> Dict:
        """Extract APK information using aapt dump badging"""
        self.aapt_path = self._get_aapt_path()
        if not self.aapt_path:
            return {}
        
        try:
            result = subprocess.run(
                [str(self.aapt_path), "dump", "badging", apk_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {}
            
            info = {}
            output = result.stdout
            
            # Parse package name and version
            pkg_match = re.search(r"package: name='([^']+)' versionCode='([^']+)' versionName='([^']+)'", output)
            if pkg_match:
                info['package_name'] = pkg_match.group(1)
                info['version_code'] = pkg_match.group(2)
                info['version_name'] = pkg_match.group(3)
            
            # Parse SDK versions
            sdk_match = re.search(r"sdkVersion:'(\d+)'", output)
            if sdk_match:
                info['min_sdk'] = sdk_match.group(1)
            
            target_sdk_match = re.search(r"targetSdkVersion:'(\d+)'", output)
            if target_sdk_match:
                info['target_sdk'] = target_sdk_match.group(1)
            
            # Parse permissions
            permissions = re.findall(r"uses-permission: name='([^']+)'", output)
            info['permissions'] = permissions
            
            # Parse native code
            native_match = re.search(r"native-code: '([^']+)'", output)
            if native_match:
                info['native_code'] = native_match.group(1).split("' '")
            
            return info
            
        except Exception as e:
            self.logger(f"Error reading APK info: {e}", "error")
            return {}


# ============================================================================
# DECOMPILER DETECTOR
# ============================================================================

class DecompilerDetector:
    """Detect which tool was used to decompile a project"""
    
    @staticmethod
    def detect(project_path: Path) -> str:
        """Detect decompiler type"""
        if (project_path / ".apktool_project").exists() or (project_path / "apktool.yml").exists():
            return "apktool"
        elif (project_path / ".apkeditor_project").exists():
            return "apkeditor"
        else:
            # Default to apktool
            return "apktool"
