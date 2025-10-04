# 🚀 Deployment Guide - Nightingale Recruitment Agent

This guide covers various deployment options for the Nightingale Recruitment Agent.

## 📋 Pre-deployment Checklist

- [ ] All code tested locally
- [ ] API keys configured in `.env`
- [ ] Dependencies listed in `requirements.txt`
- [ ] Documentation updated
- [ ] `.gitignore` configured properly

## 🐙 GitHub Setup

### 1. Create Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Initial commit
git commit -m "🎯 Initial commit: Nightingale Recruitment Agent v1.0"

# Add remote repository (replace with your GitHub repo URL)
git remote add origin https://github.com/your-username/Nightingale-recruitment-agent.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 2. Repository Settings

- Add repository description: "Smart Resume Analysis & Interview Preparation System powered by Groq AI"
- Add topics: `ai`, `resume-analysis`, `streamlit`, `groq`, `recruitment`, `interview-prep`
- Enable Issues and Discussions
- Set up branch protection rules

## ☁️ Streamlit Cloud Deployment

### 1. Connect to GitHub

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`

### 2. Configure Secrets

In Streamlit Cloud dashboard, add secrets:

```toml
[secrets]
GROQ_API_KEY = "your_groq_api_key_here"
OPENAI_API_KEY = "your_openai_api_key_here"
CUTOFF_SCORE = "75"
```

### 3. Deploy

- Click "Deploy"
- Your app will be available at: `https://your-app-name.streamlit.app`

## 🐳 Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Install optional packages
RUN pip install langchain langchain-community langchain-openai langchain-groq faiss-cpu openai groq

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. Build and Run

```bash
# Build image
docker build -t Nightingale-recruitment-agent .

# Run container
docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_key_here \
  -e OPENAI_API_KEY=your_key_here \
  Nightingale-recruitment-agent
```

## 🌐 Heroku Deployment

### 1. Create Heroku Files

**Procfile:**

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

**runtime.txt:**

```
python-3.11.6
```

### 2. Deploy to Heroku

```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set GROQ_API_KEY=your_key_here
heroku config:set OPENAI_API_KEY=your_key_here

# Deploy
git push heroku main
```

## ☁️ AWS Deployment

### 1. EC2 Instance

```bash
# Launch EC2 instance (Ubuntu 22.04)
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip nginx -y

# Clone repository
git clone https://github.com/your-username/Nightingale-recruitment-agent.git
cd Nightingale-recruitment-agent

# Install Python dependencies
pip3 install -r requirements.txt
python3 install_optional.py

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run with PM2 (process manager)
sudo npm install -g pm2
pm2 start "streamlit run app.py --server.port=8501" --name Nightingale-app
```

### 2. Configure Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 🔧 Environment Configuration

### Production Environment Variables

```bash
# Required
GROQ_API_KEY=your_production_groq_key
OPENAI_API_KEY=your_production_openai_key

# Optional
CUTOFF_SCORE=75
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

## 📊 Monitoring & Maintenance

### Health Checks

- Monitor API response times
- Check error rates
- Monitor resource usage
- Set up alerts for failures

### Updates

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Restart application
pm2 restart Nightingale-app  # For PM2
# or restart your deployment service
```

## 🔒 Security Best Practices

### Production Security

- Use HTTPS only
- Implement rate limiting
- Monitor API usage
- Regular security updates
- Backup strategies

### API Key Management

- Use environment variables
- Rotate keys regularly
- Monitor usage quotas
- Implement key rotation

## 📈 Scaling Considerations

### Horizontal Scaling

- Load balancer setup
- Multiple app instances
- Database for session storage
- CDN for static assets

### Performance Optimization

- Caching strategies
- API response optimization
- Resource monitoring
- Auto-scaling policies

## 🆘 Troubleshooting

### Common Issues

- **Port conflicts**: Change port in configuration
- **API limits**: Monitor usage and upgrade plans
- **Memory issues**: Increase instance size
- **SSL errors**: Check certificate configuration

### Debugging

```bash
# Check logs
streamlit run app.py --logger.level=debug

# Test API connections
python test_setup.py

# Monitor resources
htop  # or your preferred monitoring tool
```

Choose the deployment method that best fits your needs and infrastructure requirements!
