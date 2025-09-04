#!/usr/bin/env python3
"""
Setup script for HTML to Google Forms Converter
Checks dependencies and guides through setup process
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - Compatible")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'beautifulsoup4',
        'google-api-python-client', 
        'google-auth-httplib2',
        'google-auth-oauthlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - Installed")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    return missing_packages

def install_packages(packages):
    """Install missing packages"""
    if not packages:
        return True
    
    print(f"\n📦 Installing missing packages...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'
        ] + packages)
        print("✅ All packages installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages")
        return False

def check_credentials():
    """Check if credentials.json exists"""
    if os.path.exists('credentials.json'):
        print("✅ credentials.json found")
        return True
    else:
        print("❌ credentials.json not found")
        print("\n📋 Setup Instructions:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create/select project")
        print("3. Enable Google Forms API") 
        print("4. Create OAuth 2.0 Desktop credentials")
        print("5. Download and rename to 'credentials.json'")
        print("6. Add your email as test user in OAuth consent screen")
        return False

def check_html_forms():
    """Check if HTML forms exist"""
    forms_dir = Path("old-forms")
    if not forms_dir.exists():
        print("❌ old-forms directory not found")
        return False
    
    html_files = list(forms_dir.glob("*.html"))
    if not html_files:
        print("❌ No HTML files found in old-forms/")
        return False
    
    print(f"✅ Found {len(html_files)} HTML forms:")
    for file in html_files:
        print(f"   - {file.name}")
    return True

def main():
    """Main setup function"""
    print("🌾 HTML to Google Forms Converter - Setup Check")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    print("\n📦 Checking Dependencies:")
    missing = check_dependencies()
    
    if missing:
        response = input(f"\nInstall missing packages? (y/n): ").lower()
        if response == 'y':
            if not install_packages(missing):
                return
        else:
            print("❌ Cannot proceed without required packages")
            return
    
    print("\n🔑 Checking Credentials:")
    has_credentials = check_credentials()
    
    print("\n📁 Checking HTML Forms:")
    has_forms = check_html_forms()
    
    print("\n" + "=" * 50)
    
    if has_credentials and has_forms:
        print("🎉 Setup Complete! You can now run:")
        print("   python ultimate_html_to_google_form_converter.py")
    else:
        print("⚠️  Setup incomplete. Please follow the instructions above.")

if __name__ == "__main__":
    main()
