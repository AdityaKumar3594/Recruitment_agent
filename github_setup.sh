#!/bin/bash

# 🎯 Nightingale Recruitment Agent - GitHub Setup Script
# This script helps you push your project to GitHub

echo "🎯 Nightingale Recruitment Agent - GitHub Setup"
echo "=========================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
else
    echo "✅ Git repository already initialized"
fi

# Add all files
echo "📋 Adding files to Git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    echo "💾 Committing changes..."
    git commit -m "🎯 Nightingale Recruitment Agent: Complete AI-powered resume analysis system

Features:
- Resume analysis with skill scoring
- Interview question generation  
- Resume improvement suggestions
- ATS optimization
- Multiple export formats
- Industry-specific templates
- Modern Nightingale-themed UI

Tech Stack: Python, Streamlit, Groq AI, OpenAI (optional)
"
fi

# Check if remote origin exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "✅ Remote origin already configured"
    echo "🔄 Pushing to existing repository..."
    git push
else
    echo ""
    echo "🐙 GitHub Repository Setup Required"
    echo "=================================="
    echo ""
    echo "Please follow these steps:"
    echo ""
    echo "1. Go to https://github.com/new"
    echo "2. Create a new repository named: Nightingale-recruitment-agent"
    echo "3. Don't initialize with README (we already have files)"
    echo "4. Copy the repository URL (e.g., https://github.com/username/Nightingale-recruitment-agent.git)"
    echo ""
    read -p "Enter your GitHub repository URL: " repo_url
    
    if [ -n "$repo_url" ]; then
        echo "🔗 Adding remote origin..."
        git remote add origin "$repo_url"
        
        echo "🚀 Setting main branch and pushing..."
        git branch -M main
        git push -u origin main
        
        echo ""
        echo "🎉 Success! Your project is now on GitHub!"
        echo "📍 Repository URL: $repo_url"
        echo ""
        echo "Next steps:"
        echo "- Add repository description: 'Smart Resume Analysis & Interview Preparation System powered by Groq AI'"
        echo "- Add topics: ai, resume-analysis, streamlit, groq, recruitment, interview-prep"
        echo "- Enable Issues and Discussions"
        echo "- Consider deploying to Streamlit Cloud: https://share.streamlit.io"
    else
        echo "❌ No repository URL provided. Please run the script again."
    fi
fi

echo ""
echo "📚 Additional files created:"
echo "- LICENSE (MIT License)"
echo "- .env.example (Environment template)"
echo "- CONTRIBUTING.md (Contribution guidelines)"
echo "- ARCHITECTURE.md (Technical documentation)"
echo "- DEPLOY.md (Deployment guide)"
echo ""
echo "🔒 Security reminder:"
echo "- Your .env file is excluded from Git (contains API keys)"
echo "- Share .env.example with users instead"
echo ""
echo "✅ Setup complete! Happy coding! 🎯"