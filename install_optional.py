#!/usr/bin/env python3
"""
Installation script for optional Euron Recruitment Agent dependencies.
Run this script to install enhanced features like vector embeddings.
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    print("🚀 Euron Recruitment Agent - Optional Dependencies Installer")
    print("=" * 60)
    
    # Essential packages for enhanced functionality
    optional_packages = [
        "langchain>=0.1.0",
        "langchain-community>=0.0.15", 
        "langchain-openai>=0.0.5",
        "langchain-groq>=0.1.0",
        "faiss-cpu>=1.8.0",
        "openai>=1.10.0",
        "groq>=0.4.0"
    ]
    
    print("Installing optional packages for enhanced functionality...")
    print("This will enable:")
    print("• Vector embeddings for better semantic analysis")
    print("• Advanced RAG (Retrieval Augmented Generation)")
    print("• Enhanced question-answering capabilities")
    print()
    
    success_count = 0
    for package in optional_packages:
        print(f"Installing {package}...")
        if install_package(package):
            success_count += 1
    
    print()
    print("=" * 60)
    print(f"Installation complete! {success_count}/{len(optional_packages)} packages installed successfully.")
    
    if success_count == len(optional_packages):
        print("🎉 All optional packages installed! You now have full functionality.")
    else:
        print("⚠️  Some packages failed to install. The app will still work with basic functionality.")
    
    print()
    print("To run the application:")
    print("streamlit run app.py")

if __name__ == "__main__":
    main()