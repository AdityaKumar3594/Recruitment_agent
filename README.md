# 🎯 Nightingale Recruitment Agent

Smart Resume Analysis & Interview Preparation System powered by Groq AI.

## 🚀 Quick Start

### 1. Create Environment

```bash
conda create -n Nightingale python==3.11 -y
conda activate Nightingale
```

### 2. Install Dependencies

```bash
# Install essential packages
pip install -r requirements.txt

# Install optional packages for enhanced features (recommended)
python install_optional.py
```

### 3. Configure API Keys

Create a `.env` file or set in the app:

```
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional for enhanced features
```

### 4. Run Application

**Option 1: Clean startup (recommended)**

```bash
python run_app.py
```

**Option 2: Direct streamlit**

```bash
streamlit run app.py
```

**Option 3: With custom port**

```bash
streamlit run app.py --server.port 8502
```

## 🎯 Features

- **Resume Analysis**: AI-powered skill assessment and scoring
- **Interview Questions**: Personalized question generation
- **Resume Q&A**: Interactive resume querying
- **Improvement Suggestions**: Detailed feedback and recommendations
- **Modern UI**: Professional Nightingale-themed interface

## 🔧 API Keys

- **Groq API**: Required - Get free key at [console.groq.com](https://console.groq.com/)
- **OpenAI API**: Optional - Enables enhanced vector embeddings

## 📋 Requirements

- Python 3.11+
- Streamlit
- Groq API Key (free)
- OpenAI API Key (optional)

## 🔧 Troubleshooting

### Common Issues

**Torch warnings**: These are harmless and don't affect functionality. Use `python run_app.py` for cleaner output.

**Import errors**: Run `python test_setup.py` to check your installation.

**API errors**: Verify your Groq API key at [console.groq.com](https://console.groq.com/)

**Port conflicts**: Use `streamlit run app.py --server.port 8502` to use a different port.

### Performance Tips

- Use both Groq + OpenAI API keys for best performance
- Ensure stable internet connection for API calls
- Keep resume files under 5MB for faster processing
