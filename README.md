# 🔧 MyApkTool - Super Edition

<div dir="rtl">

أداة احترافية للهندسة العكسية لتطبيقات الأندرويد مع واجهة رسومية عصرية

</div>

A professional Android APK reverse engineering desktop tool with modern GUI and advanced automation features.

---

## ✨ Features (المميزات)

### 🎯 Super Features
- **Java Detector**: Automatic Java runtime detection with version display
- **Threading Engine**: Background processing with smooth GUI (no freezing)
- **Real-time Logger**: Color-coded output (Red: errors, Green: success, Yellow: warnings)
- **Auto-Signer**: Automatic APK signing after successful build
- **Smart Paths**: Handles Windows paths with spaces correctly
- **Drag & Drop**: Drop APK files directly into the application

### 🎨 Modern GUI
- Dark theme with modern aesthetics (CustomTkinter)
- Responsive design with resizable window
- Progress bar with real-time updates
- Activity log with timestamps

---

## 📋 Requirements (المتطلبات)

### 1. Python
- Python 3.10 or higher
- Download from: https://www.python.org/downloads/

### 2. Java JDK
- Required for apktool operations
- Download from: https://www.oracle.com/java/technologies/downloads/

### 3. Python Libraries
Install using pip:
```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install customtkinter Pillow tkinterdnd2
```

### 4. APK Tools
**IMPORTANT**: You must download these tools manually and place them in the `tools/` folder:

1. **apktool.jar**
   - Download from: https://ibotpeaches.github.io/Apktool/
   - Place in: `MyApkTool/tools/apktool.jar`

2. **uber-apk-signer.jar**
   - Download from: https://github.com/patrickfav/uber-apk-signer/releases
   - Place in: `MyApkTool/tools/uber-apk-signer.jar`

---

## 📁 Project Structure (البنية)

```
MyApkTool/
├── main.py                 # Main application
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── tools/                 # ⚠️ Place Java tools here
│   ├── apktool.jar       # Download manually
│   └── uber-apk-signer.jar  # Download manually
├── workspace/            # Decompiled APK files (auto-created)
└── output/               # Signed APK output (auto-created)
```

---

## 🚀 Installation & Setup (التثبيت)

### Step 1: Install Python Libraries
```bash
cd MyApkTool
pip install -r requirements.txt
```

### Step 2: Download Java Tools
1. Download `apktool.jar` and place in `tools/` folder
2. Download `uber-apk-signer.jar` and place in `tools/` folder

### Step 3: Verify Java Installation
```bash
java -version
```
If Java is not installed, download and install Java JDK.

---

## 🎮 Usage (الاستخدام)

### Running the Application
```bash
python main.py
```

### Workflow
1. **Select APK**: Click "Browse" or drag & drop APK file
2. **Decompile**: Click "📦 Decompile" to extract APK contents
3. ✏️ **Edit Files**: Modify the decompiled files in `workspace/` folder
4. **Build**: Click "🔨 Build" to recompile APK
5. **Auto-Sign**: Signing happens automatically after build
6. ✅ **Done**: Find signed APK in `output/` folder

### Features in Action

#### Startup Checks
The application automatically verifies:
- ✓ Java installation
- ✓ Required tools (apktool.jar, uber-apk-signer.jar)
- ✓ Python libraries

#### Real-time Logging
- 🔴 **Red**: Errors and failures
- 🟢 **Green**: Success messages
- 🟡 **Yellow**: Warnings
- ⚪ **White**: Info messages

#### Auto-Signing
After successful build, the tool automatically:
1. Detects the built APK
2. Runs uber-apk-signer
3. Saves signed APK to `output/` folder
4. Displays completion message

---

## 🔨 Converting to EXE (تحويل لملف تنفيذي)

To create a standalone .exe file:

### Install PyInstaller
```bash
pip install pyinstaller
```

### Build EXE
```bash
pyinstaller --onefile --windowed --add-data "tools;tools" --name "MyApkTool" main.py
```

### Options Explained
- `--onefile`: Create single .exe file
- `--windowed`: No console window
- `--add-data "tools;tools"`: Include tools folder
- `--name "MyApkTool"`: Output name

### After Building
1. Find EXE in `dist/` folder
2. Copy `tools/` folder next to the .exe
3. Distribute both together

---

## 🐛 Troubleshooting (حل المشاكل)

### Libraries Not Found
```
Missing: customtkinter, Pillow, tkinterdnd2
Solution: pip install -r requirements.txt
```

### Java Not Found
```
Java not installed
Solution: Install Java JDK from oracle.com
```

### Tools Not Found
```
apktool.jar not found in tools folder
Solution: Download and place in tools/ folder
```

### Path Errors
The tool automatically handles paths with spaces. If you still get errors:
- Avoid special characters in file names
- Use English characters in paths

---

## 📝 Technical Details (التفاصيل التقنية)

### Architecture
- **LibraryChecker**: Validates Python dependencies
- **JavaDetector**: Checks Java installation
- **PathManager**: Smart path handling for Windows
- **APKOperations**: Core decompile/build/sign logic
- **MyApkToolGUI**: CustomTkinter-based interface

### Threading Model
All long operations run in background threads:
- Main thread: GUI updates only
- Worker threads: Java subprocess execution
- Queue-based callbacks: Thread-safe communication

### Path Handling
- Supports paths with spaces
- Automatic quoting when needed
- PyInstaller-compatible relative paths
- Works in both script and .exe modes

---

## 📌 Notes (ملاحظات)

<div dir="rtl">

### ملاحظات مهمة
1. يجب تحميل ملفات الأدوات يدوياً (apktool.jar و uber-apk-signer.jar)
2. يتطلب Java JDK للعمل
3. التوقيع يتم تلقائياً بعد البناء
4. جميع العمليات تعمل في الخلفية دون تجميد الواجهة
5. يدعم السحب والإفلات للملفات

</div>

### Important Notes (English)
1. Tools must be downloaded manually (apktool.jar & uber-apk-signer.jar)
2. Requires Java JDK to function
3. Auto-signing after successful build
4. All operations run in background (no GUI freeze)
5. Drag & drop support included

---

## 📄 License

Free to use for educational and personal purposes.

---

## 🙏 Credits

- **apktool**: https://ibotpeaches.github.io/Apktool/
- **uber-apk-signer**: https://github.com/patrickfav/uber-apk-signer
- **CustomTkinter**: https://github.com/TomSchimansky/CustomTkinter

---

<div dir="rtl">

## 💡 نصائح للاستخدام

1. **قبل البدء**: تأكد من تثبيت Java و Python
2. **التحميل**: ضع ملفات الأدوات في مجلد tools
3. **التشغيل**: قم بتشغيل main.py
4. **التعديل**: بعد فك التطبيق، عدل الملفات في workspace
5. **البناء**: اضغط Build وسيتم التوقيع تلقائياً

</div>

---

**Made with ❤️ for Android Developers**
