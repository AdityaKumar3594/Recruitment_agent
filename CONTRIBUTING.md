# Contributing to Euron Recruitment Agent

Thank you for your interest in contributing to the Euron Recruitment Agent! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/euron-recruitment-agent.git
   cd euron-recruitment-agent
   ```
3. **Set up the development environment**:
   ```bash
   conda create -n euron python==3.11 -y
   conda activate euron
   pip install -r requirements.txt
   python install_optional.py
   ```
4. **Copy the environment file**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## 🔧 Development Setup

### Testing Your Changes
```bash
# Run setup test
python test_setup.py

# Start the application
python run_app.py
```

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

## 📝 How to Contribute

### Reporting Bugs
1. Check if the bug is already reported in [Issues](https://github.com/your-username/euron-recruitment-agent/issues)
2. Create a new issue with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)

### Suggesting Features
1. Check existing [Issues](https://github.com/your-username/euron-recruitment-agent/issues) for similar requests
2. Create a new issue with:
   - Clear description of the feature
   - Use case and benefits
   - Possible implementation approach

### Submitting Changes
1. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes** with clear, focused commits
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Submit a pull request** with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots if UI changes

## 🎯 Areas for Contribution

### High Priority
- [ ] PDF/DOCX export functionality
- [ ] Additional industry templates
- [ ] Resume parsing improvements
- [ ] Performance optimizations

### Medium Priority
- [ ] Multi-language support
- [ ] Batch resume processing
- [ ] Advanced analytics dashboard
- [ ] Integration with job boards

### Low Priority
- [ ] Dark mode theme
- [ ] Mobile responsiveness
- [ ] Additional chart types
- [ ] Email integration

## 🧪 Testing

### Manual Testing
- Test with different resume formats (PDF, TXT)
- Try various job descriptions
- Test all tabs and features
- Verify API error handling

### Automated Testing
```bash
# Run basic tests
python test_setup.py

# Test specific components
python -m pytest tests/ (when available)
```

## 📚 Documentation

When contributing, please:
- Update README.md if adding new features
- Add docstrings to new functions
- Update requirements.txt if adding dependencies
- Include examples in your documentation

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain a professional tone

## 📞 Getting Help

- Create an issue for questions
- Check existing documentation
- Review closed issues for solutions

## 🏆 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to Euron Recruitment Agent! 🎯