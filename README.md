
<div align="center">

# 🐍 MyApkTool - Super Edition (Python)

**أداة احترافية للهندسة العكسية لتطبيقات الأندرويد مع واجهة رسومية عصرية**
*A professional Android APK reverse engineering desktop tool with a modern GUI and advanced automation features.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-2E3440?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D7?style=for-the-badge&logo=windows)](https://www.microsoft.com/windows)
[![Architecture](https://img.shields.io/badge/Architecture-Multi--Threaded-FF6F00?style=for-the-badge&logo=opslevel)](https://docs.python.org/3/library/threading.html)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---
*A Masterpiece Developed by **Amr Khaled** in Collaboration with **Ali Sakkaf***
</div>

<br>

> ### 🔥 Looking for the Standalone C++ (Qt) Version?
> هل تبحث عن نسخة تعمل كبرنامج تنفيذي مباشر (.exe) بدون الحاجة لتثبيت بايثون؟
> تم تطوير نسخة شقيقة لهذا المشروع مبنية بالكامل بلغة **C++** وإطار عمل **Qt Framework** لتقدم أداءً خارقاً وسرعة قصوى من تطوير **Ali Sakkaf**.
> 👉 **[Click Here to get MyApkTool-Pro (C++ Edition) by Ali Sakkaf](https://github.com/alisakkaf/MyApkTool-Pro)**

---

## 📖 Table of Contents (الفهرس)
1. [Introduction (مقدمة)](#introduction)
2. [Features & Modern GUI (المميزات)](#features)
3. [Technical Details (التفاصيل التقنية)](#technical-details)
4. [Project Structure (البنية والشجرة)](#structure)
5. [Requirements (المتطلبات)](#requirements)
6. [Installation & Setup (التثبيت)](#installation)
7. [Usage & Workflow (الاستخدام)](#usage)
8. [Converting to EXE (تحويل لملف تنفيذي)](#build)
9. [Important Notes (ملاحظات)](#notes)
10. [Troubleshooting (حل المشاكل)](#troubleshooting)
11. [The Masterminds & Collaboration (فريق التطوير)](#collaboration)

---

<a id="introduction"></a>
## 🚀 1. Introduction (مقدمة)

Welcome to **MyApkTool - Super Edition**, a Python desktop application designed for professional Android developers, malware analysts, and reverse engineers. It eliminates the friction of Command Line Interface (CLI) operations by wrapping the world's most powerful tools (`apktool`, `APKEditor`, `zipalign`, `apksigner`, `baksmali`, `adb`) into a stunning, responsive, and multi-threaded Graphical User Interface.

**The best part? It's 100% Out-of-the-Box Ready.** This repository comes fully bundled with all necessary `.jar` binaries and `.exe` tools inside the `Resources/` and `tools/` directories. No manual downloading of background tools is required!

---

<a id="features"></a>
## ✨ 2. Features & Modern GUI (المميزات)

### 🎯 Super Features
* **Java Detector:** Automatic Java runtime detection with precise version display.
* **Threading Engine:** Background processing ensures a smooth GUI without any freezing, even during heavy operations.
* **Real-time Logger:** Color-coded terminal output embedded in the UI (🔴 Red: errors, 🟢 Green: success, 🟡 Yellow: warnings, ⚪ White: info).
* **Auto-Signer:** Automatic APK signing using `apksigner` or `uber-apk-signer` immediately after a successful build.
* **Smart Paths:** The tool is designed to handle Windows paths with spaces and special characters flawlessly.
* **Drag & Drop:** Drop APK files directly into the application window to begin.
* **Dual-Decompilation:** Switch intelligently between **Apktool** (for deep resource decoding) and **APKEditor** (for rapid bypass of obfuscation).
* **Direct Baksmali/Smali & Split-APK Merger:** Modify `.dex` files directly or merge App Bundles into a single universal APK.

### 🎨 Modern GUI
* Dark theme with modern aesthetics powered by `CustomTkinter`.
* Responsive design with a resizable, frameless-styled window.
* Progress bar with real-time dynamic updates.
* Activity log with accurate timestamps.

---

<a id="technical-details"></a>
## 📝 3. Technical Details (التفاصيل التقنية)

The architecture of this tool is strictly modular, verifying environments before executing commands.

### Internal Architecture Models
* **LibraryChecker:** Validates all Python dependencies upon startup.
* **JavaDetector:** Checks the system's `JAVA_HOME` and tests the installation.
* **PathManager:** Smart path handling for Windows directories.
* **APKOperations:** Core underlying logic for decompiling, building, and signing.
* **MyApkToolGUI:** The frontend CustomTkinter-based interface.

### Threading Model
All long operations run in background threads to preserve user experience:
* **Main thread:** Handles GUI updates and user interactions exclusively.
* **Worker threads:** Executes Java subprocesses (`apktool`, `zipalign`, etc.).
* **Queue-based callbacks:** Ensures thread-safe communication between background tasks and the UI.

---

<a id="structure"></a>
## 📁 4. Project Structure (البنية والشجرة)

Here is the exact layout of the repository, highlighting the rich GUI modularity and the pre-bundled tools:

```text
MyApkTool/
├── main.py                     # Main application entry point
├── main.spec                   # PyInstaller configuration file
├── requirements.txt            # Python dependencies
├── README.md                   # This documentation
├── config.py                   # Global configuration and path handlers
├── managers.py                 # Advanced threading and queue managers
├── dialogs.py                  # Custom popup and prompt dialogs
├── adb_manager.py              # ADB operations wrapper
├── gui/                        # Modular Interface Package
│   ├── __init__.py
│   ├── app.py                  # Main Window UI
│   ├── tab_decompile.py        # Decompilation interface
│   ├── tab_compile.py          # Compilation interface
│   ├── tab_sign.py             # Signing & Zipalign interface
│   ├── tab_merge.py            # Split-APK merger interface
│   ├── tab_baksmali.py         # DEX/Smali conversion interface
│   ├── tab_adb.py              # Device management interface
│   ├── tab_info.py             # APK metadata extraction interface
│   ├── tab_settings.py         # App settings & preferences
│   └── dialog_keystore.py      # .jks Keystore generator interface
├── Resources/                  # Pre-Bundled Core Engines & Assets
│   ├── APKEditor.jar, apktool.jar, baksmali.jar, smali.jar, apksigner.jar
│   ├── aapt.exe, aapt2.exe, adb.exe, zipalign.exe
│   ├── testkey.pk8, testkey.x509.pem
│   ├── AdbWinApi.dll, AdbWinUsbApi.dll, libwinpthread-1.dll
│   └── icon.ico, icon.png, splash.png
├── tools/                      # Additional Platform Tools
│   ├── custom/
│   ├── platform-tools/         # fastboot, sqlite3, mke2fs, etc.
│   └── uber-apk-signer.jar, APKEditor.jar
├── workspace/                  # Auto-created folder for decompiled files
├── output/backups/             # Auto-created folder for signed APKs
├── framework/                  # Extracted OEM framework resources
├── keys/                       # User-generated Keystore files
├── logs/                       # Activity log text files
└── __pycache__/                # Python compiled bytecode

```

---

<a id="requirements"></a>

## 📋 5. Requirements (المتطلبات)

### 1. Python Environment

* Python 3.10 or higher.
* Download from: [python.org/downloads](https://www.python.org/downloads/)

### 2. Java JDK

Required for `apktool.jar` and signing operations.

* 🔗 [Java 21 (LTS)](https://www.oracle.com/java/technologies/downloads/#java21)
* 🔗 [Java 25](https://www.oracle.com/java/technologies/downloads/#java25)
* 🔗 [Java 9 Archive](https://www.oracle.com/java/technologies/javase/javase9-archive-downloads.html)

### 3. Python Libraries

Installed via:

```bash
pip install -r requirements.txt

```

*(Or manually: `pip install customtkinter Pillow tkinterdnd2`)*

---

<a id="installation"></a>

## 🚀 6. Installation & Setup (التثبيت)

**Step 1: Clone the Repository**

```bash
git clone [https://github.com/AmrKhaled-Tech/ApkTool-Pro.git](https://github.com/AmrKhaled-Tech/ApkTool-Pro.git)
cd ApkTool-Pro

```

**Step 2: Install Python Libraries**

```bash
pip install -r requirements.txt

```

**Step 3: Verify Java Installation**
Open your terminal and type:

```bash
java -version

```

*If Java is not installed, download and install the Java JDK from the links provided above.*

*(Note: Unlike the old version, you **do not** need to download `apktool.jar` or `uber-apk-signer.jar` manually. They are already included in the `Resources/` and `tools/` folders!)*

---

<a id="usage"></a>

## 🎮 7. Usage & Workflow (الاستخدام)

**Running the Application:**

```bash
python main.py

```

**The Standard Workflow:**

1. **Startup Checks:** The application automatically verifies Java installation, required tools, and Python libraries.
2. **Select APK:** Click "Browse" or drag & drop an APK file into the UI.
3. **Decompile:** Click **"📦 Decompile"** to extract APK contents to the `workspace/` folder.
4. **✏️ Edit Files:** Modify the decompiled XML/Smali files using your code editor.
5. **Build:** Go to the Compile tab and click **"🔨 Build"** to recompile the APK.
6. **Auto-Sign:** If enabled, signing happens automatically after the build completes using `uber-apk-signer`.
7. **✅ Done:** Find your ready-to-install, signed APK in the `output/` folder.

---

<a id="build"></a>

## 🔨 8. Converting to EXE (تحويل لملف تنفيذي)

To create a standalone `.exe` file without needing users to install Python:

**1. Install PyInstaller**

```bash
pip install pyinstaller

```

**2. Build EXE**
We must include the bundled directories (`tools` and `Resources`) so the binary works properly:

```bash
pyinstaller --onefile --windowed --add-data "tools;tools" --add-data "Resources;Resources" --icon="Resources/icon.ico" --name "MyApkTool" main.py

```

* `--onefile`: Create a single `.exe` file.
* `--windowed`: No console window (hide background CMD).
* `--add-data`: Include the necessary external tool folders.

**After Building:** Find your executable in the `dist/` folder.


<a id="notes"></a>

## 📌 9. Important Notes (ملاحظات)

**ملاحظات مهمة (Arabic):**

* جميع أدوات الهندسة العكسية تم دمجها مسبقاً في مجلدي `Resources` و `tools`.
* يتطلب البرنامج تثبيت Java JDK لكي يعمل بشكل صحيح.
* عملية توقيع التطبيقات (Signing) تتم تلقائياً بعد نجاح البناء.
* جميع العمليات تعمل في الخلفية بفضل نظام `Threading` المتطور دون تجميد الواجهة.
* البرنامج يدعم بالكامل السحب والإفلات للملفات لتسهيل العمل.

**Important Notes (English):**

* Core tools are already pre-bundled inside `Resources` and `tools` directories.
* Requires Java JDK installed on your system to function.
* Auto-signing executes immediately after a successful build.
* All heavy operations run in the background via threading (no GUI freeze).
* Drag & drop support is fully implemented across the application.

<a id="troubleshooting"></a>

## 🐛 10. Troubleshooting (حل المشاكل)

* **Libraries Not Found (Missing customtkinter, Pillow, tkinterdnd2):**
* *Solution:* Run `pip install -r requirements.txt`


* **Java Not Found:**
* *Solution:* Install Java JDK from oracle.com and ensure `JAVA_HOME` is set in Windows.


* **Path Errors:**
* *Solution:* While the tool automatically handles paths with spaces, if you still get errors, avoid special/foreign characters in your Windows folder names and use English characters.


<a id="collaboration"></a>

## 🤝 11. The Masterminds & Collaboration (فريق التطوير)

This toolkit is the result of powerful collaboration, offering solutions across different programming languages to fit every developer's needs.

<table>
<tr>
<td align="center">
<h3>🐍 The Python Architect</h3>
<img src="https://www.google.com/search?q=https://github.com/AmrKhaled-Tech.png" width="100px;" alt="Amr Khaled"/><br />
<b>Amr Khaled</b><i>Creator of the Python / CustomTkinter Edition</i>

<a href="https://www.google.com/search?q=https://github.com/AmrKhaled-Tech">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/GitHub-Profile-181717%3Fstyle%3Dfor-the-badge%26logo%3Dgithub"/>
</a>
<p>Amr designed this incredibly smooth, multi-threaded Python edition. He focused on building an accessible, highly customizable, and automated Out-of-the-Box experience using CustomTkinter.</p>
</td>
<td align="center">
<h3>⚙️ The C++ & Qt Mastermind</h3>
<img src="https://www.google.com/search?q=https://github.com/alisakkaf.png" width="100px;" alt="Ali Sakkaf"/><br />
<b>Ali Sakkaf</b><i>Creator of the C++ / Qt Pro Edition</i>

<a href="https://www.google.com/search?q=https://github.com/alisakkaf">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/GitHub-Profile-181717%3Fstyle%3Dfor-the-badge%26logo%3Dgithub"/>
</a><a href="https://mysterious-dev.com/">
<img src="https://www.google.com/search?q=https://img.shields.io/badge/Website-mysterious--dev.com-00599C%3Fstyle%3Dfor-the-badge%26logo%3Dweb"/>
</a>
<p>Ali developed the ultra-high-performance <b>MyApkTool Pro</b> built entirely in C++ and Qt Framework, offering natively compiled, blazing-fast execution and true standalone portability.</p>
</td>
</tr>
</table>

### 🙏 Special Credits
* **[Apktool](https://ibotpeaches.github.io/Apktool/):** by iBotPeaches
* **[Uber-APK-Signer](https://github.com/patrickfav/uber-apk-signer):** by patrickfav
* **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter):** by TomSchimansky
