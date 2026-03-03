<div align="center">

# 🐍 MyApkTool - Super Edition (Python)

**The Ultimate, Automated, and Most Comprehensive Android Reverse Engineering Toolkit**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-CustomTkinter-2E3440?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D7?style=for-the-badge&logo=windows)](https://www.microsoft.com/windows)
[![Architecture](https://img.shields.io/badge/Architecture-Multi--Threaded-FF6F00?style=for-the-badge&logo=opslevel)](https://docs.python.org/3/library/threading.html)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---
*A Masterpiece Developed by **Amr Khaled** in Collaboration with **Ali Sakkaf***
*Python Edition | Out-of-the-Box Ready*
</div>

## 📖 Comprehensive Table of Contents
1. [Introduction & Philosophy](#introduction)
2. [Why Choose MyApkTool Super Edition?](#why-choose)
3. [Deep-Dive: Core Features & Capabilities](#features)
   - [A. The Dual-Decompilation Engine](#feat-engine)
   - [B. Cryptography, Keystores & Signing](#feat-crypto)
   - [C. DEX/Smali Bytecode Manipulation](#feat-dex)
   - [D. Universal ADB Device Management](#feat-adb)
4. [Prerequisites & System Requirements](#prerequisites)
5. [Step-by-Step Installation Guide](#installation)
6. [The Professional Workflow (How to Use)](#workflow)
7. [Project Architecture & Directory Tree](#architecture)
8. [Building a Standalone Executable (PyInstaller)](#build)
9. [Troubleshooting & FAQ](#troubleshooting)
10. [The Masterminds & Collaboration](#collaboration)

---

<a id="introduction"></a>
## 🚀 1. Introduction & Philosophy

Welcome to **MyApkTool - Super Edition**, a meticulously crafted Python desktop application designed for professional Android developers, security researchers, malware analysts, and reverse engineers. 

Historically, reverse engineering Android applications required juggling multiple Command Line Interface (CLI) tools—typing lengthy commands, managing environment variables, and dealing with frozen terminals. **MyApkTool Super Edition** eliminates this friction entirely. By wrapping the world's most powerful Android CLI tools into a highly fluid, stunning, and modern Graphical User Interface (GUI) powered by `CustomTkinter`, we bring unprecedented efficiency to your workspace.

This tool is **100% Out-of-the-Box Ready**. You do not need to hunt down external `.jar` binaries or configure complex system paths. Everything you need (`apktool`, `APKEditor`, `zipalign`, `apksigner`, `baksmali`, `adb`) is already bundled inside the repository!

---

<a id="why-choose"></a>
## 🎯 2. Why Choose MyApkTool Super Edition?

* **Zero GUI Freezing:** Unlike poorly optimized scripts, MyApkTool features a highly advanced multi-threading manager (`managers.py`). Every heavy background task (decompiling 100MB+ APKs, signing, building) runs on isolated worker threads. Your UI remains perfectly smooth and responsive at all times.
* **Intelligent Path Management:** Windows path limitations are a thing of the past. The tool handles spaces, special characters, and long directory names automatically without breaking Java subprocesses.
* **Real-Time Rich Logging:** A built-in graphical console terminal that captures `stdout` and `stderr` live. It color-codes the output: 🟢 **Green** for Success, 🔴 **Red** for Errors, and 🟡 **Yellow** for Warnings, giving you instant visual feedback.

---

<a id="features"></a>
## ✨ 3. Deep-Dive: Core Features & Capabilities

<a id="feat-engine"></a>
### A. The Dual-Decompilation Engine
Not all APKs are created equal. Some use modern App Bundles, while others employ anti-decompilation tricks. MyApkTool gives you choices:
* **Apktool Engine:** The industry standard. Perfect for deep resource extraction, translating `resources.arsc` to readable XML, and extracting `AndroidManifest.xml` flawlessly.
* **APKEditor Engine:** Specifically optimized for raw speed and bypassing certain obfuscation methods that crash Apktool. 
* **Framework Installer:** Working with Samsung, Xiaomi, or custom ROM system apps? Simply use the built-in Framework manager to install OEM `.apk` framework files so you can decompile proprietary applications without resource missing errors.

<a id="feat-crypto"></a>
### B. Cryptography, Keystores & Signing
Modern Android (Android 11+) enforces strict cryptographic signatures.
* **V1, V2, and V3 Signing Supported:** Automatically utilizes `apksigner.jar` or `uber-apk-signer.jar` to ensure your modified APKs install without parsing errors.
* **Automated Signing Flow:** Check the "Auto-Sign" box before hitting Build. Once compilation is successful, the app instantly signs it and drops it in the `output/` folder.
* **Visual Keystore Generator:** Stop typing `keytool` commands! Use the GUI to generate `.jks` (Java KeyStore) files. Fill out your Alias, Password, and Distinguished Names (CN, OU, O, L, ST, C) through clean text fields.
* **Zipalign Engine:** Automatically aligns uncompressed data within the APK on 4-byte boundaries, significantly reducing RAM usage on the target Android device.

<a id="feat-dex"></a>
### C. DEX/Smali Bytecode Manipulation
* **Direct Baksmali / Smali:** Skip the full decompilation! If you only need to modify logic, jump to the Baksmali tab. Disassemble a standalone `classes.dex` file into a Smali directory, edit the bytecode, and recompile it back to a `.dex` file with a single click.
* **App Bundle / Split-APK Merger:** Extracted an app from your phone only to find it consists of `base.apk`, `config.xxhdpi.apk`, and `config.en.apk`? Use the Merge Tab. The tool will fuse all split components into a single, standalone, installable APK.
* **Metadata Extractor:** Use the Info tab to execute `aapt dump badging` and extract package names, version codes, requested permissions, and launchable activities instantly.

<a id="feat-adb"></a>
### D. Universal ADB Device Management
Manage your Android devices without touching the terminal.
* **Auto-Discovery:** Automatically detects connected USB or Wi-Fi paired devices.
* **Visual Package Manager:** View every installed app on your phone. Filter by system apps or user apps.
* **One-Click Operations:** Pull (extract) APKs directly from the device to your PC workspace. Push (install) modified APKs from your PC directly to the device. Uninstall packages instantly.

---

<a id="prerequisites"></a>
## ⚙️ 4. Prerequisites & System Requirements

Because we have bundled the core binary tools, you only need to prepare your base operating system environment:

### Step 1: Python Installation
The application UI and logic are powered by Python.
* **Requirement:** Python 3.10, 3.11, or 3.12 (Make sure to check "Add Python to PATH" during installation).
* **Download:** [Python Official Site](https://www.python.org/downloads/)

### Step 2: Java Runtime Environment (JDK)
Java is strictly necessary because `apktool`, `apksigner`, and `APKEditor` are `.jar` (Java Archive) applications.
* **Requirement:** Any modern JDK version (JDK 8, 17, 21, or 25).
* **Verify:** Open CMD and type `java -version`.
* **Official Downloads:**
  * 🔗 [Java 21 (LTS)](https://www.oracle.com/java/technologies/downloads/#java21)
  * 🔗 [Java 25](https://www.oracle.com/java/technologies/downloads/#java25)
  * 🔗 [Java 9 Archive](https://www.oracle.com/java/technologies/javase/javase9-archive-downloads.html)

---

<a id="installation"></a>
## 🛠️ 5. Step-by-Step Installation Guide

Setting up MyApkTool Super Edition takes less than two minutes.

**1. Clone the Source Code**
Open your terminal (CMD, PowerShell, or Git Bash) and run:
```bash
git clone [https://github.com/AmrKhaled-Tech/ApkTool-Pro.git](https://github.com/AmrKhaled-Tech/ApkTool-Pro.git)
cd ApkTool-Pro
