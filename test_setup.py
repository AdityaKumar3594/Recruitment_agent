#!/usr/bin/env python3
"""
Test script to verify Nightingale Recruitment Agent setup.
Run this to check if everything is working correctly.
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test if all required packages are available."""
    print("🔍 Testing imports...")
    
    try:
        import streamlit
        print("✅ streamlit")
    except ImportError:
        print("❌ streamlit - Run: pip install streamlit")
        return False
    
    try:
        import PyPDF2
        print("✅ PyPDF2")
    except ImportError:
        print("❌ PyPDF2 - Run: pip install pypdf2")
        return False
    
    try:
        import requests
        print("✅ requests")
    except ImportError:
        print("❌ requests - Run: pip install requests")
        return False
    
    try:
        import plotly
        print("✅ plotly")
    except ImportError:
        print("❌ plotly - Run: pip install plotly")
        return False
    
    # Optional imports
    try:
        from langchain_groq import ChatGroq
        print("✅ langchain-groq (optional)")
    except ImportError:
        print("⚠️  langchain-groq (optional) - Enhanced features disabled")
    
    return True

def test_api_key():
    """Test if Groq API key is available."""
    print("\n🔑 Testing API key...")
    
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not groq_key:
        print("❌ GROQ_API_KEY not found in environment")
        print("   Add it to .env file or set as environment variable")
        return False
    
    if groq_key.startswith("gsk_"):
        print("✅ Groq API key format looks correct")
    else:
        print("⚠️  Groq API key format might be incorrect (should start with 'gsk_')")
    
    return True

def test_agent_creation():
    """Test if the ResumeAnalysisAgent can be created."""
    print("\n🤖 Testing agent creation...")
    
    try:
        from agents import ResumeAnalysisAgent
        
        load_dotenv()
        groq_key = os.getenv("GROQ_API_KEY")
        
        if not groq_key:
            print("❌ Cannot test agent - no API key")
            return False
        
        # Try to create agent
        agent = ResumeAnalysisAgent(groq_api_key=groq_key)
        print("✅ ResumeAnalysisAgent created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return False

def main():
    print("🎯 Nightingale Recruitment Agent - Setup Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test API key
    api_key_ok = test_api_key()
    
    # Test agent creation
    agent_ok = test_agent_creation()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"   API Key: {'✅ PASS' if api_key_ok else '❌ FAIL'}")
    print(f"   Agent:   {'✅ PASS' if agent_ok else '❌ FAIL'}")
    
    if imports_ok and api_key_ok and agent_ok:
        print("\n🎉 All tests passed! You can run the application with:")
        print("   streamlit run app.py")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        
        if not imports_ok:
            print("\n💡 To install missing packages:")
            print("   pip install -r requirements.txt")
        
        if not api_key_ok:
            print("\n💡 To set up API key:")
            print("   1. Get free key at: https://console.groq.com/")
            print("   2. Add to .env file: GROQ_API_KEY=your_key_here")

if __name__ == "__main__":
    main()