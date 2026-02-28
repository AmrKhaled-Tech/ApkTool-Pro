import customtkinter as ctk
from tkinter import messagebox
import subprocess
import os
from pathlib import Path
from config import PathManager

class KeystoreCreatorDialog(ctk.CTkToplevel):
    """
    Professional Dialog for creating Android Keystores
    """
    def __init__(self, parent, on_create_callback=None):
        super().__init__(parent)
        self.parent = parent
        self.on_create = on_create_callback
        
        # Window Setup
        self.title("Create New Keystore 🔐")
        self.geometry("500x750")
        self.resizable(False, False)
        
        # Modal
        self.transient(parent)
        self.grab_set()
        
        # Grid Config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # Content expands
        
        # Variables
        self.var_filename = ctk.StringVar(value="my-release-key.jks")
        self.var_alias = ctk.StringVar(value="my_alias")
        self.var_password = ctk.StringVar()
        self.var_confirm = ctk.StringVar()
        self.var_validity = ctk.StringVar(value="25")
        
        # DName Vars
        self.var_cn = ctk.StringVar() # First/Last Name
        self.var_ou = ctk.StringVar() # Org Unit
        self.var_o = ctk.StringVar()  # Org Name
        self.var_l = ctk.StringVar()  # City
        self.var_st = ctk.StringVar() # State
        self.var_c = ctk.StringVar()  # Country Code
        
        self._build_ui()
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        ctk.CTkLabel(
            header, 
            text="Create Keystore 🔑", 
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack()
        
        ctk.CTkLabel(
            header,
            text="Generate a professional signing certificate for your Android app.",
            text_color="gray"
        ).pack()

        # Content Scrollable
        content = ctk.CTkScrollableFrame(self)
        content.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        
        # SECTION 1: KEYSTORE DETAILS
        # ---------------------------
        self._create_section_header(content, "1. Keystore Details")
        
        # Filename
        ctk.CTkLabel(content, text="Filename (.jks):").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(content, textvariable=self.var_filename).pack(fill="x", pady=(0,10))
        
        # Alias
        ctk.CTkLabel(content, text="Key Alias:").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(content, textvariable=self.var_alias).pack(fill="x", pady=(0,10))
        
        # Password
        pass_frame = ctk.CTkFrame(content, fg_color="transparent")
        pass_frame.pack(fill="x", pady=(0,10))
        pass_frame.grid_columnconfigure((0,1), weight=1)
        
        ctk.CTkLabel(pass_frame, text="Password:").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(pass_frame, text="Confirm:").grid(row=0, column=1, sticky="w")
        
        ctk.CTkEntry(pass_frame, textvariable=self.var_password, show="*").grid(row=1, column=0, sticky="ew", padx=(0,5))
        ctk.CTkEntry(pass_frame, textvariable=self.var_confirm, show="*").grid(row=1, column=1, sticky="ew", padx=(5,0))
        
        # Validity
        ctk.CTkLabel(content, text="Validity (Years):").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(content, textvariable=self.var_validity).pack(fill="x", pady=(0,10))

        # SECTION 2: CERTIFICATE INFO
        # ---------------------------
        self._create_section_header(content, "2. Certificate Information")
        
        # Common Name
        ctk.CTkLabel(content, text="First and Last Name (CN):").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(content, textvariable=self.var_cn, placeholder_text="e.g. John Doe").pack(fill="x", pady=(0,10))
        
        # Org Unit
        ctk.CTkLabel(content, text="Organizational Unit (OU):").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(content, textvariable=self.var_ou, placeholder_text="e.g. Mobile Development").pack(fill="x", pady=(0,10))
        
        # Org Name
        ctk.CTkLabel(content, text="Organization (O):").pack(anchor="w", pady=(5,0))
        ctk.CTkEntry(content, textvariable=self.var_o, placeholder_text="e.g. My Company Inc.").pack(fill="x", pady=(0,10))
        
        # City / State
        loc_frame = ctk.CTkFrame(content, fg_color="transparent")
        loc_frame.pack(fill="x", pady=(0,10))
        loc_frame.grid_columnconfigure((0,1), weight=1)
        
        ctk.CTkLabel(loc_frame, text="City (L):").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(loc_frame, text="State/Province (ST):").grid(row=0, column=1, sticky="w")
        
        ctk.CTkEntry(loc_frame, textvariable=self.var_l).grid(row=1, column=0, sticky="ew", padx=(0,5))
        ctk.CTkEntry(loc_frame, textvariable=self.var_st).grid(row=1, column=1, sticky="ew", padx=(5,0))

        # Country Code
        ctk.CTkLabel(content, text="Country Code (C): (2 letters)").pack(anchor="w", pady=(5,0))
        
        country_frame = ctk.CTkFrame(content, fg_color="transparent")
        country_frame.pack(fill="x", pady=(0,10))
        country_frame.grid_columnconfigure(0, weight=1)
        
        self.combo_country = ctk.CTkComboBox(
            country_frame,
            variable=self.var_c,
            values=[
                 "US", "GB", "CA", "AU", "DE", "FR", "JP", "CN", "IN", "BR", "RU", "SA", "AE", "EG", "TR", "ID"
            ],
            width=80
        )
        self.combo_country.grid(row=0, column=0, sticky="ew")
        self.combo_country.set("US")
        
        ctk.CTkButton(country_frame, text="❓ Codes", width=60, command=self._show_country_codes).grid(row=0, column=1, padx=(5,0))

        # Actions
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        
        ctk.CTkButton(
            action_frame, 
            text="Cancel", 
            fg_color="gray", 
            command=self.destroy
        ).pack(side="left", fill="x", expand=True, padx=(0,10))
        
        ctk.CTkButton(
            action_frame,
            text="✨ Generate Keystore",
            fg_color="green",
            font=ctk.CTkFont(weight="bold"),
            command=self._generate_keystore
        ).pack(side="left", fill="x", expand=True, padx=(10,0))
        
    def _create_section_header(self, parent, text):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(15, 5))
        ctk.CTkLabel(frame, text=text, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
        ctk.CTkFrame(frame, height=2, fg_color="gray50").pack(fill="x")

    def _show_country_codes(self):
        msg = "Common Country Codes:\n\n" \
              "US - United States\n" \
              "GB - United Kingdom\n" \
              "CA - Canada\n" \
              "DE - Germany\n" \
              "FR - France\n" \
              "SA - Saudi Arabia\n" \
              "AE - UAE\n" \
              "EG - Egypt\n" \
              "IN - India\n" \
              "CN - China\n\n" \
              "Use 2-letter ISO code."
        messagebox.showinfo("Country Codes", msg)

    def _generate_keystore(self):
        # Validation
        if not self.var_filename.get() or not self.var_alias.get():
            messagebox.showerror("Error", "Filename and Alias are required!")
            return
            
        if not self.var_password.get() or len(self.var_password.get()) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters!")
            return
            
        if self.var_password.get() != self.var_confirm.get():
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        # Prepare Path
        keys_dir = PathManager.get_base_dir() / "keys"
        keys_dir.mkdir(parents=True, exist_ok=True)
        
        filename = self.var_filename.get()
        if not filename.endswith(".jks"):
            filename += ".jks"
            
        keystore_path = keys_dir / filename
        
        if keystore_path.exists():
            if not messagebox.askyesno("Warning", f"File '{filename}' already exists. Overwrite?"):
                return
                
        # Prepare DName
        dname_parts = []
        if self.var_cn.get(): dname_parts.append(f"CN={self.var_cn.get()}")
        if self.var_ou.get(): dname_parts.append(f"OU={self.var_ou.get()}")
        if self.var_o.get(): dname_parts.append(f"O={self.var_o.get()}")
        if self.var_l.get(): dname_parts.append(f"L={self.var_l.get()}")
        if self.var_st.get(): dname_parts.append(f"ST={self.var_st.get()}")
        if self.var_c.get(): dname_parts.append(f"C={self.var_c.get()}")
        
        dname = ", ".join(dname_parts)
        if not dname:
            dname = "CN=Unknown" # Fallback
            
        # Command
        # keytool -genkeypair -v -keystore <path> -alias <alias> -keyalg RSA -keysize 2048 -validity <days> -storepass <pass> -keypass <pass> -dname <dname>
        
        # Check settings for Java path? Or just assume system 'keytool' / java_path/keytool?
        from config import JavaUtils
        # Use parent settings if available, else auto-detect
        current_java = self.parent.settings.java_path if hasattr(self.parent, 'settings') else ""
        keytool_cmd = JavaUtils.find_keytool_path(current_java)
        
        if not keytool_cmd:
             messagebox.showerror("Error", "Keytool not found! Please check Java installation.")
             return

        year_days = int(self.var_validity.get()) * 365
        
        cmd = [
            keytool_cmd, "-genkeypair", "-v",
            "-keystore", str(keystore_path),
            "-alias", self.var_alias.get(),
            "-keyalg", "RSA",
            "-keysize", "2048",
            "-validity", str(year_days),
            "-storepass", self.var_password.get(),
            "-keypass", self.var_password.get(),
            "-dname", dname
        ]
        
        try:
            # Run
            # We use subprocess directly here for simplicity, or we could use Manager
            process = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
            )
            
            if process.returncode == 0:
                messagebox.showinfo("Success", f"Keystore created successfully!\n\nSaved to: keys/{filename}")
                if self.on_create:
                    self.on_create(str(keystore_path), self.var_password.get(), self.var_alias.get())
                self.destroy()
            else:
                messagebox.showerror("Error", f"Keytool failed:\n{process.stdout}\n{process.stderr}")
                
        except FileNotFoundError:
             messagebox.showerror("Error", "Keytool not found! Install Java or set Java Path in settings.")
        except Exception as e:
             messagebox.showerror("Error", f"An error occurred: {str(e)}")
