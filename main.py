"""
MyApkTool - Professional Edition v3.0

Entry point for the application.
"""
import sys
from pathlib import Path

# Ensure the gui package is importable
# Add the current directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from gui.app import MyApkToolPro
except ImportError as e:
    print(f"Error importing MyApkToolPro: {e}")
    print("Ensure all modules (gui, config, managers, dialogs) are present.")
    input("Press Enter to exit...")
    sys.exit(1)

def main():
    """Main entry point"""
    app = MyApkToolPro()
    app.mainloop()

if __name__ == "__main__":
    main()
