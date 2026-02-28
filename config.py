"""
MyApkTool - Configuration & Settings Module
Handles application settings, path management, and configuration persistence.
"""

import os
import sys
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict, List


import shutil
import subprocess

# ============================================================================
# JAVA UTILITIES
# ============================================================================

class JavaUtils:
    """Utilities for finding and validating Java"""
    
    @staticmethod
    def get_common_paths() -> list:
        """Get common Java installation paths on Windows"""
        paths = []
        program_files = [os.environ.get("ProgramFiles", "C:\\Program Files"), 
                         os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")]
        
        # Additional Known Roots
        roots = []
        for pf in program_files:
            roots.append((Path(pf) / "Java", ["jdk", "jre"]))
            roots.append((Path(pf) / "Eclipse Adoptium", ["jdk", "jre"]))
            roots.append((Path(pf) / "Microsoft", ["jdk", "jre"]))
            roots.append((Path(pf) / "Azul Systems", ["zulu", "jdk"]))
            roots.append((Path(pf) / "OpenLogic", ["jdk", "jre"]))
            roots.append((Path(pf) / "Amazon Corretto", ["jdk", "jre"]))
            # Android Studio Embedded JDK
            roots.append((Path(pf) / "Android" / "Android Studio" / "jbr" / "bin", []))
            roots.append((Path(pf) / "Android" / "Android Studio" / "jre" / "bin", []))

        for root, prefixes in roots:
            if not root.exists(): continue
            
            # If direct bin path (Android Studio /jbr/bin)
            if root.name == "bin":
                java_bin = root / "java.exe"
                if java_bin.exists():
                    paths.append(str(java_bin))
                continue

            # Scan children
            try:
                for child in root.iterdir():
                    if child.is_dir():
                        # Check prefixes or just check for bin/java
                        if not prefixes or any(child.name.lower().startswith(p) for p in prefixes):
                            bin_path = child / "bin" / "java.exe"
                            if bin_path.exists():
                                paths.append(str(bin_path))
            except Exception:
                pass
                
        return paths

    @staticmethod
    def _resolve_symlink_or_path(path_str: str) -> Optional[Path]:
        """Resolve symlinks or incomplete paths to real file"""
        if not path_str: return None
        p = Path(path_str)
        if not p.exists():
             shutil_path = shutil.which(path_str)
             if shutil_path:
                 p = Path(shutil_path)
             else:
                 return None
        
        # Resolve symlinks (e.g. C:\ProgramData\Oracle\Java\javapath\java.exe)
        try:
            return p.resolve()
        except:
            return p

    @staticmethod
    def find_java_path() -> str:
        """Smart discover Java path"""
        # 1. Check JAVA_HOME
        java_home = os.environ.get("JAVA_HOME")
        if java_home:
            bin_path = Path(java_home) / "bin" / "java.exe"
            if bin_path.exists():
                return str(bin_path)

        # 2. Check PATH (Resolve Real Path!)
        path_java = shutil.which("java")
        if path_java:
            real_path = JavaUtils._resolve_symlink_or_path(path_java)
            if real_path and real_path.exists():
                 # Valid real java
                 return str(real_path)

        # 3. Check Common Paths
        common_paths = JavaUtils.get_common_paths()
        if common_paths:
            # Sort to prefer newer versions (often higher numbers)
            # Rough sort by string length/name
            common_paths.sort(key=lambda x: x.lower(), reverse=True) 
            return common_paths[0]

        return "java" # Fallback

    @staticmethod
    def find_keytool_path(java_path_hint: str = "") -> str:
        """Find keytool based on java path or smart scan"""
        
        # 1. Try Hint (Resolved to Real Path) - PRIORITY
        if java_path_hint:
             real_path = JavaUtils._resolve_symlink_or_path(java_path_hint)
             if real_path:
                 # Check sibling (bin/java -> bin/keytool)
                 keytool = real_path.parent / "keytool.exe"
                 if keytool.exists():
                     return str(keytool)
                 # Check if hint was root (jdk-17/ -> bin/keytool)
                 keytool = real_path / "bin" / "keytool.exe"
                 if keytool.exists():
                     return str(keytool)

        # 2. Check JAVA_HOME
        java_home = os.environ.get("JAVA_HOME")
        if java_home:
            keytool = Path(java_home) / "bin" / "keytool.exe"
            if keytool.exists():
                return str(keytool)
                
        # 3. Check System PATH for keytool
        path_keytool = shutil.which("keytool")
        if path_keytool:
            return path_keytool

        # 4. Scan Common Paths (Deep Search) for best match
        # We look for ANY valid jdk/jre that has keytool
        common_paths = JavaUtils.get_common_paths() # Returns .../bin/java.exe paths
        
        # Sort by version (newer first) if possible?
        # common_paths is already roughly sorted.
        
        for java_exe in common_paths:
            # Check sibling keytool
            p = Path(java_exe)
            keytool = p.parent / "keytool.exe"
            if keytool.exists():
                return str(keytool)
            
        return "" # Not found (Empty string triggers error in UI)

@dataclass
class AppSettings:
    """Application settings"""
    language: str = "en"
    theme: str = "dark"
    default_decompiler: str = "apktool"  # or "apkeditor"
    decode_resources: bool = True
    decode_sources: bool = True
    use_aapt2: bool = False
    auto_sign_after_compile: bool = True
    auto_zipalign: bool = True
    zipalign_before_sign: bool = True
    use_testkey: bool = True
    v1_signing: bool = True
    v2_signing: bool = True
    v3_signing: bool = False
    threads: int = 4
    save_logs: bool = True
    suppress_java_warnings: bool = True  # New setting to hide JVM warnings
    clear_framework_before: bool = False
    fix_apktool_errors: bool = True
    java_path: str = "" # Default empty, will auto-detect in __post_init__ or property
    heap_size: int = 2048
    compression_level: int = 5  # 0-9 (Note: Apktool generally handles this via yml, but we can use it for zipping)
    
    def __post_init__(self):
        # Auto-detect Java if empty
        if not self.java_path:
            self.java_path = JavaUtils.find_java_path()
    # Custom Tools Management
    use_custom_apktool: bool = False
    custom_apktool_path: str = ""  # Path to selected specific jar
    
    use_custom_aapt: bool = False
    custom_aapt_path: str = ""     # Path to custom aapt.exe
    
    use_custom_aapt2: bool = False
    custom_aapt2_path: str = ""    # Path to custom aapt2.exe
    
    apksigner_path: str = ""       # Custom path override for signer
    
    # Keystore Settings
    use_custom_keystore: bool = False
    keystore_path: str = ""
    keystore_pass: str = ""
    key_alias: str = ""
    key_pass: str = ""
    key_alias: str = ""
    key_pass: str = ""
    
    # Keystore Profiles (Path -> {pass, alias, key_pass})
    saved_keystores: Dict[str, Dict[str, str]] = field(default_factory=dict)
    
    # Extended settings
    default_output_dir: str = "output"
    default_decompile_dir: str = "workspace"
    backup_output_dir: str = "output/backups"
    aapt_variant: str = "aapt"
    zipalign_alignment: int = 4
    force_overwrite: bool = False


# ============================================================================
# SETTINGS MANAGER
# ============================================================================

class SettingsManager:
    """Manage application settings"""
    
    def __init__(self, config_file: Path):
        self.config_file = config_file
        self.settings = AppSettings()
        self.load()
    
    def load(self):
        """Load settings from JSON file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if hasattr(self.settings, key):
                            setattr(self.settings, key, value)
            except Exception as e:
                print(f"Error loading settings: {e}")
    
    def save(self):
        """Save settings to JSON file"""
        try:
            data = {k: v for k, v in self.settings.__dict__.items()}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")


# ============================================================================
# PATH MANAGEMENT
# ============================================================================

class PathManager:
    """Handle all file paths and tool locations"""
    
    @staticmethod
    def get_base_dir() -> Path:
        """Get base directory"""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        else:
            return Path(__file__).parent
    
    @staticmethod
    def quote_path(path: str) -> str:
        """Quote path if it contains spaces"""
        path = str(path)
        if ' ' in path and not (path.startswith('"') and path.endswith('"')):
            return f'"{path}"'
        return path
    
    @staticmethod
    def get_tool_path(tool_name: str) -> Optional[Path]:
        """Get path to a tool in the tools folder"""
        base = PathManager.get_base_dir()
        tool_path = base / "tools" / tool_name
        if tool_path.exists():
            return tool_path
        
        # Check platform-tools for ADB
        if tool_name in ["adb.exe", "adb"]:
            platform_tools = base / "tools" / "platform-tools" / tool_name
            if platform_tools.exists():
                return platform_tools
        
        return None
    
    @staticmethod
    def ensure_directories():
        """Create required directories"""
        base = PathManager.get_base_dir()
        for dir_name in ["workspace", "output", "output/backups", "temp", "framework", "logs"]:
            (base / dir_name).mkdir(parents=True, exist_ok=True)
