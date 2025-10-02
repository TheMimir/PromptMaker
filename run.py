#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Prompt Maker - Quick Launcher
"""
import subprocess
import sys
import os

if sys.platform == 'win32':
    os.system('chcp 65001 >nul')

def main():
    """Run the Streamlit application"""
    print(">> Starting AI Prompt Maker...")
    print("   URL: http://localhost:8501")
    print("   Press Ctrl+C to stop.\n")

    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run',
            'app.py',
            '--server.port', '8501',
            '--server.address', 'localhost',
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false',
            '--theme.base', 'light'
        ])
    except KeyboardInterrupt:
        print("\n>> Application stopped.")
    except Exception as e:
        print(f"!! Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
