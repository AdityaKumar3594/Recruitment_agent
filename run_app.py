#!/usr/bin/env python3
"""
Clean startup script for Euron Recruitment Agent.
This script suppresses unnecessary warnings and starts the Streamlit app.
"""

import warnings
import os
import sys

# Suppress torch warnings and other unnecessary warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*torch.classes.*")
warnings.filterwarnings("ignore", message=".*_path.*")

# Set environment variables to suppress additional warnings
os.environ["PYTHONWARNINGS"] = "ignore"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

def main():
    """Run the Streamlit app with clean output."""
    print("🎯 Starting Euron Recruitment Agent...")
    print("📍 Open your browser to: http://localhost:8501")
    print("🔧 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Import and run streamlit
    try:
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", "app.py", "--server.headless", "true"]
        stcli.main()
    except KeyboardInterrupt:
        print("\n👋 Euron Recruitment Agent stopped.")
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        print("💡 Try running directly: streamlit run app.py")

if __name__ == "__main__":
    main()