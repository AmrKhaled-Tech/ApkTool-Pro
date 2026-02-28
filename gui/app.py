import os
import sys
import threading
import queue
import time
from pathlib import Path
import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Import DnD
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

# Import Pillow
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Import Core Modules
try:
    from config import AppSettings, SettingsManager, PathManager
    from managers import (
        ApktoolManager, APKEditorManager, SigningManager, ZipalignManager,
        BaksmaliManager, FrameworkManager, AAPTManager, DecompilerDetector
    )
    from dialogs import SmartTaskDialog
except ImportError:
    # Handle running from inside gui package
    sys.path.append(str(Path(__file__).parent.parent))
    from config import AppSettings, SettingsManager, PathManager
    from managers import (
        ApktoolManager, APKEditorManager, SigningManager, ZipalignManager,
        BaksmaliManager, FrameworkManager, AAPTManager, DecompilerDetector
    )
    from dialogs import SmartTaskDialog

# Import Tab Mixins
from gui.tab_decompile import DecompileTabMixin
from gui.tab_compile import CompileTabMixin
from gui.tab_sign import SignTabMixin
from gui.tab_merge import MergeTabMixin
from gui.tab_baksmali import BaksmaliTabMixin
from gui.tab_info import InfoTabMixin
from gui.tab_adb import ADBTabMixin
from gui.tab_settings import SettingsTabMixin

class MyApkToolPro(ctk.CTk, 
                   DecompileTabMixin, 
                   CompileTabMixin, 
                   SignTabMixin, 
                   MergeTabMixin, 
                   BaksmaliTabMixin, 
                   InfoTabMixin, 
                   ADBTabMixin, 
                   SettingsTabMixin):
    
    def __init__(self):
        # Initialize CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Init window
        if DND_AVAILABLE:
            super().__init__()
            pass
        else:
            super().__init__()

        self.withdraw() # Hide initially
        
        # Title and geometry
        self.title("MyApkTool - Professional Edition v3.0")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Set Icon
        self._set_app_icon()

        # Show Splash Screen
        self._show_splash()
        
        # Ensure directories
        PathManager.ensure_directories()
        
        # Settings
        base_dir = PathManager.get_base_dir()
        self.settings_manager = SettingsManager(base_dir / "config.json")
        self.settings = self.settings_manager.settings
        
        # Initialize Shared Variables (Sync Logic)
        self._init_shared_vars()

        # State variables
        self.current_project = None
        self.current_apk = None
        self.is_processing = False
        
        # String variables for paths
        self.apk_path_var = ctk.StringVar()
        self.project_path_var = ctk.StringVar()
        self.merge_input_var = ctk.StringVar()
        self.apk_path_var.trace_add('write', self._on_apk_path_change)
        
        # Initialize managers
        self.apktool_manager = ApktoolManager(self.log_message, self.settings)
        self.apkeditor_manager = APKEditorManager(self.log_message, self.settings)
        self.signing_manager = SigningManager(self.log_message, self.settings)
        self.zipalign_manager = ZipalignManager(self.log_message, self.settings)
        self.baksmali_manager = BaksmaliManager(self.log_message, self.settings)
        self.framework_manager = FrameworkManager(self.log_message, self.settings)
        self.aapt_manager = AAPTManager(self.log_message, self.settings)
        
        # Thread queue
        self.callback_queue = queue.Queue()
        
        # Build GUI
        self._build_gui()
        
        # Start callback processor
        self._process_callbacks()
        
        # Show Main Window
        self.after(2000, self.deiconify)
        
        # Bind shortcuts
        self._bind_shortcuts()
        
        # Initial log colors
        self._update_log_colors()

        # Bind Tab switch event
        self._on_tab_change_callback = None
        self.tab_view.configure(command=self._on_tab_change)

    def _on_tab_change(self):
        """Handle dynamic UI changes on tab switch"""
        current_tab = self.tab_view.get()
        
        # Hide Log in Settings Tab
        if current_tab == "Settings":
            if self.log_visible:
                # Save state that it was visible
                self.was_log_visible = True
                self._toggle_log()
        else:
            # Show log if it was visible before entering Settings
            if hasattr(self, 'was_log_visible') and self.was_log_visible and not self.log_visible:
                self._toggle_log()
                self.was_log_visible = False
            elif not hasattr(self, 'was_log_visible') and not self.log_visible:
                # Optional: Force show log in other tabs? User requested: "returns the Activity Log"
                self._toggle_log()

    def _init_shared_vars(self):
        """Initialize Tkinter variables bound to settings for global sync"""
        def bind(var, name):
            var.trace_add('write', lambda *a: setattr(self.settings, name, var.get()))

        # Decompile Config
        self.var_decode_resources = ctk.BooleanVar(value=self.settings.decode_resources)
        bind(self.var_decode_resources, 'decode_resources')
        
        self.var_decode_sources = ctk.BooleanVar(value=self.settings.decode_sources)
        bind(self.var_decode_sources, 'decode_sources')
        
        self.var_clear_framework = ctk.BooleanVar(value=self.settings.clear_framework_before)
        bind(self.var_clear_framework, 'clear_framework_before')
        
        self.var_decompiler = ctk.StringVar(value=self.settings.default_decompiler)
        bind(self.var_decompiler, 'default_decompiler')
        
        # Compile Config
        self.var_use_aapt2 = ctk.BooleanVar(value=self.settings.use_aapt2)
        bind(self.var_use_aapt2, 'use_aapt2')
        
        # Sign/Align Config
        self.var_auto_sign = ctk.BooleanVar(value=self.settings.auto_sign_after_compile)
        bind(self.var_auto_sign, 'auto_sign_after_compile')
        
        self.var_auto_zipalign = ctk.BooleanVar(value=self.settings.auto_zipalign)
        bind(self.var_auto_zipalign, 'auto_zipalign')
        
        self.var_zipalign_before = ctk.BooleanVar(value=self.settings.zipalign_before_sign)
        bind(self.var_zipalign_before, 'zipalign_before_sign')
        
        self.var_v1 = ctk.BooleanVar(value=self.settings.v1_signing)
        bind(self.var_v1, 'v1_signing')
        
        self.var_v2 = ctk.BooleanVar(value=self.settings.v2_signing)
        bind(self.var_v2, 'v2_signing')
        
        self.var_v3 = ctk.BooleanVar(value=self.settings.v3_signing)
        bind(self.var_v3, 'v3_signing')

        self.var_zipalign_alignment = ctk.IntVar(value=self.settings.zipalign_alignment)
        bind(self.var_zipalign_alignment, 'zipalign_alignment')

        # Advanced / Java
        self.var_java_path = ctk.StringVar(value=self.settings.java_path)
        bind(self.var_java_path, 'java_path')

        self.var_heap_size = ctk.IntVar(value=self.settings.heap_size)
        bind(self.var_heap_size, 'heap_size')

        self.var_compression = ctk.IntVar(value=self.settings.compression_level)
        bind(self.var_compression, 'compression_level')

        self.var_suppress_java_warnings = ctk.BooleanVar(value=self.settings.suppress_java_warnings)
        bind(self.var_suppress_java_warnings, 'suppress_java_warnings')

        # Custom Tool Paths
        self.var_use_custom_apktool = ctk.BooleanVar(value=self.settings.use_custom_apktool)
        bind(self.var_use_custom_apktool, 'use_custom_apktool')

        self.var_custom_apktool_path = ctk.StringVar(value=self.settings.custom_apktool_path)
        bind(self.var_custom_apktool_path, 'custom_apktool_path')

        self.var_use_custom_aapt = ctk.BooleanVar(value=self.settings.use_custom_aapt)
        bind(self.var_use_custom_aapt, 'use_custom_aapt')

        self.var_custom_aapt_path = ctk.StringVar(value=self.settings.custom_aapt_path)
        bind(self.var_custom_aapt_path, 'custom_aapt_path')

        self.var_use_custom_aapt2 = ctk.BooleanVar(value=self.settings.use_custom_aapt2)
        bind(self.var_use_custom_aapt2, 'use_custom_aapt2')

        self.var_custom_aapt2_path = ctk.StringVar(value=self.settings.custom_aapt2_path)
        bind(self.var_custom_aapt2_path, 'custom_aapt2_path')

        self.var_apksigner_path = ctk.StringVar(value=self.settings.apksigner_path)
        bind(self.var_apksigner_path, 'apksigner_path')

        # Keystore
        self.var_use_custom_keystore = ctk.BooleanVar(value=self.settings.use_custom_keystore)
        bind(self.var_use_custom_keystore, 'use_custom_keystore')

        self.var_keystore_path = ctk.StringVar(value=self.settings.keystore_path)
        bind(self.var_keystore_path, 'keystore_path')

        self.var_keystore_pass = ctk.StringVar(value=self.settings.keystore_pass)
        bind(self.var_keystore_pass, 'keystore_pass')

        self.var_key_alias = ctk.StringVar(value=self.settings.key_alias)
        bind(self.var_key_alias, 'key_alias')

        self.var_key_pass = ctk.StringVar(value=self.settings.key_pass)
        bind(self.var_key_pass, 'key_pass')

    def _set_app_icon(self):
        """Set app icon from Resources"""
        try:
            icon_path = PathManager.get_base_dir() / "Resources" / "icon.ico"
            png_path = PathManager.get_base_dir() / "Resources" / "icon.png"
            if icon_path.exists(): self.iconbitmap(str(icon_path))
            if png_path.exists() and PIL_AVAILABLE:
                icon_img = ImageTk.PhotoImage(file=str(png_path))
                self.iconphoto(True, icon_img)
        except Exception: pass

    def _show_splash(self):
        """Show splash screen"""
        splash_path = PathManager.get_base_dir() / "Resources" / "splash.png"
        if not splash_path.exists() or not PIL_AVAILABLE: return
        splash = ctk.CTkToplevel(self)
        splash.overrideredirect(True)
        w, h = 600, 350
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        splash.geometry('%dx%d+%d+%d' % (w, h, x, y))
        try:
            img = Image.open(splash_path)
            img = ctk.CTkImage(light_image=img, dark_image=img, size=(w, h))
            ctk.CTkLabel(splash, text="", image=img).pack(fill="both", expand=True)
            splash.after(5000, splash.destroy)
        except: splash.destroy()

    def _build_gui(self):
        """Build main GUI layout"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Tabs expand
        self.grid_rowconfigure(1, weight=0) # Log container (variable)
        self.grid_rowconfigure(2, weight=0) # Status bar
        
        # Tab View
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        # Create tabs
        self.tab_decompile = self.tab_view.add("Decompile")
        self.tab_compile = self.tab_view.add("Compile")
        self.tab_sign = self.tab_view.add("Sign/Zipalign")
        self.tab_merge = self.tab_view.add("Merge Bundles")
        self.tab_baksmali = self.tab_view.add("Baksmali")
        self.tab_info = self.tab_view.add("APK Info")
        self.tab_adb = self.tab_view.add("ADB Manager")
        self.tab_settings = self.tab_view.add("Settings")
        
        # Build individual tabs
        self._build_decompile_tab()
        self._build_compile_tab()
        self._build_sign_tab()
        self._build_merge_tab()
        self._build_baksmali_tab()
        self._build_info_tab()
        self._build_adb_tab()
        self._build_settings_tab()
        
        # Log Area
        self._build_log_area()
        
        # Status Bar
        self._build_status_bar()

    def _build_log_area(self):
        """Build enhanced log output area with hide capability"""
        # Main Container
        self.log_container = ctk.CTkFrame(self)
        self.log_container.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.log_container.grid_columnconfigure(0, weight=1)
        
        # Control Bar (Always visible in container)
        self.log_control_bar = ctk.CTkFrame(self.log_container, fg_color="transparent", height=28)
        self.log_control_bar.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(
            self.log_control_bar, text="📋 Activity Log", font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=5)
        
        # Control Buttons
        ctk.CTkButton(
            self.log_control_bar, text="🗑️ Clear", command=self._clear_log, width=60, 
            fg_color=("red", "#c62828"), height=22, font=ctk.CTkFont(size=11)
        ).pack(side="right", padx=2)

        self.log_toggle_btn = ctk.CTkButton(
            self.log_control_bar, text="⬇ Hide", command=self._toggle_log, width=60, height=22, font=ctk.CTkFont(size=11)
        )
        self.log_toggle_btn.pack(side="right", padx=2)
        
        ctk.CTkButton(
            self.log_control_bar, text="Copy", command=self._copy_log, width=50, height=22, font=ctk.CTkFont(size=11)
        ).pack(side="right", padx=2)
        
        # Log Content Frame (Toggled)
        self.log_content_frame = ctk.CTkFrame(self.log_container, fg_color="transparent")
        self.log_content_frame.pack(fill="both", expand=True, padx=2)
        
        self.log_text = ctk.CTkTextbox(
            self.log_content_frame,
            wrap="word",
            font=ctk.CTkFont(family="Cascadia Code", size=10),
            height=150
        )
        self.log_text.pack(fill="both", expand=True)
        
        self.log_visible = True
        self.expanded_height = 800

    def _build_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, fg_color="transparent", height=28)
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 5))
        self.status_bar.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            self.status_bar, text="Ready", font=ctk.CTkFont(size=11), anchor="w"
        )
        self.status_label.grid(row=0, column=0, sticky="ew")

        self.theme_btn = ctk.CTkButton(
            self.status_bar, text="🌗 Theme", command=self._toggle_theme, width=70, height=22, font=ctk.CTkFont(size=11)
        )
        self.theme_btn.grid(row=0, column=1, sticky="e")

    def _toggle_log(self):
        """Toggle log visibility and adjust window size"""
        current_w = self.winfo_width()
        current_h = self.winfo_height()
        
        if self.log_visible:
            # Hide
            self.log_content_frame.pack_forget()
            self.log_toggle_btn.configure(text="⬆ Show")
            self.log_visible = False
            
            # Reduce height
            new_h = max(600, current_h - 150)
            self.expanded_height = current_h # Remember original
            self.geometry(f"{current_w}x{new_h}")
        else:
            # Show
            self.log_content_frame.pack(fill="both", expand=True, padx=2)
            self.log_toggle_btn.configure(text="⬇ Hide")
            self.log_visible = True
            
            # Restore height
            self.geometry(f"{current_w}x{self.expanded_height}")

    def log_message(self, message: str, level: str = "info"):
        if not hasattr(self, 'log_text'): return
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}\n"
        tag = level.upper() if level.upper() in ["INFO", "SUCCESS", "WARNING", "ERROR", "CMD"] else "INFO"
        
        self.log_text.configure(state="normal")
        self.log_text.insert("end", formatted, tag)
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def _toggle_theme(self):
        new_mode = "Light" if ctk.get_appearance_mode() == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        self.after(200, self._update_log_colors) # Delay to allow theme apply

    def _update_log_colors(self):
        """Update log text colors based on current theme"""
        mode = ctk.get_appearance_mode().lower()
        is_dark = "dark" in mode
        
        # Define colors (Light, Dark)
        colors = {
            "INFO":    ("#333333", "#b0bec5"),  # Dark Grey / Light Grey
            "SUCCESS": ("#007E33", "#69f0ae"),  # Strong Green / Pastel Green
            "WARNING": ("#FF8800", "#ffca28"),  # Orange / Amber
            "ERROR":   ("#CC0000", "#ff5252"),  # Dark Red / Red
            "CMD":     ("#0099CC", "#80d8ff"),  # Blue / Light Blue
        }
        
        for tag, (light, dark) in colors.items():
            color = dark if is_dark else light
            self.log_text.tag_config(tag, foreground=color)

    def _clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def _copy_log(self):
        self.clipboard_clear()
        self.clipboard_append(self.log_text.get("1.0", "end"))

    # Helpers
    def _on_apk_path_change(self, *args):
        path = self.apk_path_var.get()
        self.title(f"MyApkTool - {Path(path).name}" if path else "MyApkTool - Professional Edition v3.0")

    def _process_callbacks(self):
        try:
            while True: self.callback_queue.get_nowait()()
        except queue.Empty: pass
        self.after(100, self._process_callbacks)

    def _run_in_thread(self, target):
        threading.Thread(target=target, daemon=True).start()

    def _bind_shortcuts(self):
        self.bind("<Control-o>", lambda e: self.tab_decompile.focus_set() or self._browse_apk()) # Assuming mixin method availability logic via Tabs? 
        # Actually mixin methods are on SELF. So self._browse_apk() is from DecompileTabMixin.
        # But _browse_apk interacts with specific vars.
    
    # ... (Keep existing helpers: _open_project_folder, _open_output_folder, _open_folder, _on_drop, _open_manifest, _open_apktool_yml) ...
    # Re-implementing compact versions for replacement completeness:
    
    def _open_project_folder(self):
        if self.current_project: self._open_folder(self.current_project)
    def _open_output_folder(self): self._open_folder(PathManager.get_base_dir() / "output")
    def _open_folder(self, path):
        import subprocess, platform
        path = str(path)
        if platform.system() == "Windows": os.startfile(path)
        elif platform.system() == "Darwin": subprocess.Popen(["open", path])
        else: subprocess.Popen(["xdg-open", path])
    def _on_drop(self, event, type):
        data = event.data
        if data.startswith('{') and data.endswith('}'): data = data[1:-1]
        if type == 'apk' and data.lower().endswith('.apk'): self.apk_path_var.set(data)
    def _open_manifest(self):
        if self.current_project and (Path(self.current_project)/"AndroidManifest.xml").exists():
            self._open_folder(Path(self.current_project)/"AndroidManifest.xml")
    def _open_apktool_yml(self):
        if self.current_project and (Path(self.current_project)/"apktool.yml").exists():
            self._open_folder(Path(self.current_project)/"apktool.yml")

# Standalone run
def main():
    app = MyApkToolPro()
    app.mainloop()

if __name__ == "__main__":
    main()
