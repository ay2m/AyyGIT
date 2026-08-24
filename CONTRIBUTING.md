# 🤝 Contributing to AyyGIT

Thank you for your interest in contributing! This document provides guidelines and best practices for contributing to the AyyGIT repository.

## 📋 Before You Start

1. **Read the Documentation**
   - [PROJECTS.md](./PROJECTS.md) - Project overview
   - [SETUP.md](./SETUP.md) - Setup instructions
   - Individual project READMEs

2. **Understand the Repository**
   - AyyGIT is a collection of enhanced implementations
   - Focus on quality over quantity
   - Production-ready code is expected

3. **Choose Your Project**
   - VoiceStudio-Integrated is the main focus project
   - Other projects have their own maintenance status

---

## 🎯 Getting Started

### 1. Fork & Clone
```bash
git clone https://github.com/ay2m/AyyGIT.git
cd AyyGIT
git checkout -b feature/your-feature-name
```

### 2. Set Up Development Environment
```bash
# Follow project-specific setup from SETUP.md
cd VoiceStudio-Integrated
./start-dev.sh
```

### 3. Create a Feature Branch
```bash
git checkout -b feature/description-of-change
# or
git checkout -b fix/issue-number-description
```

---

## 💻 Code Standards

### Python
- **PEP 8 Compliance:** Use `black` for formatting
- **Linting:** Use `pylint` or `flake8`
- **Type Hints:** Use type annotations where applicable
- **Docstrings:** Follow Google-style docstrings

```python
def process_audio(file_path: str, sample_rate: int = 16000) -> np.ndarray:
    """
    Process audio file to numpy array.
    
    Args:
        file_path: Path to audio file
        sample_rate: Sample rate for loading (default: 16000)
    
    Returns:
        Audio data as numpy array
    
    Raises:
        FileNotFoundError: If audio file doesn't exist
    """
    pass
```

### JavaScript/React
- **ESLint:** Follow configured ESLint rules
- **Prettier:** Use Prettier for formatting
- **Comments:** Explain complex logic
- **Component Structure:** One component per file

```javascript
/**
 * VoiceCloning component - manages voice cloning workflow
 * @component
 * @example
 * return <VoiceCloning voiceId={123} />
 */
export const VoiceCloning = ({ voiceId }) => {
  // implementation
};
```

### Git Commits
- **Clear Messages:** Describe WHAT and WHY, not just WHAT
- **One Feature Per Commit:** Keep commits focused
- **Format:**
  ```
  feat: Add voice cloning feature
  
  - Implement basic cloning algorithm
  - Add parameter controls
  - Update database schema
  
  Fixes #123
  ```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting changes
- `refactor:` Code restructuring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

---

## 🧪 Testing

### Python
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test
pytest tests/test_engine.py::test_cloning
```

### JavaScript
```bash
# Run tests (if configured)
npm test

# Run with coverage
npm test -- --coverage
```

### Manual Testing
- Test locally before pushing
- Verify no console errors/warnings
- Test edge cases and error scenarios
- Test on multiple browsers (for frontend)

---

## 📝 Documentation

### For Code Changes
- Update relevant docstrings
- Add comments for complex logic
- Update type hints

### For New Features
- Update project README
- Add to API documentation (if applicable)
- Create/update relevant guides

### For Bug Fixes
- Document what was fixed
- Explain why the fix works
- Reference related issues

---

## 🔍 Pull Request Process

### 1. Before Creating PR
```bash
# Update your branch with latest changes
git fetch origin
git rebase origin/main

# Run tests
pytest
npm test

# Check formatting
black . --check
npm run lint
```

### 2. Create Pull Request
- **Title:** Descriptive, concise (e.g., "Add voice pitch control")
- **Description:** Include:
  - What changed and why
  - Related issues (Fixes #123)
  - Testing performed
  - Screenshots/demos (if UI change)

### 3. Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added
- [ ] Manual testing done
- [ ] No existing tests broken

## Screenshots (if applicable)
Include screenshots for UI changes

## Related Issues
Fixes #123
```

### 4. Code Review
- Address reviewer feedback
- Push updates to same branch
- Remain respectful and collaborative

### 5. Merge
- Requires approval from maintainers
- All CI checks must pass
- Branch will be deleted after merge

---

## ✅ Checklist Before Submitting

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No console errors/warnings
- [ ] Commit messages are clear
- [ ] No sensitive data in commits
- [ ] Changes don't break existing functionality

---

## 🐛 Bug Reports

### How to Report
1. Check existing issues first
2. Use bug report template
3. Include:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment (OS, Python version, etc.)
   - Logs/error messages

### Title Format
`[BUG] Brief description of issue`

---

## ✨ Feature Requests

### How to Suggest
1. Check existing issues/discussions
2. Provide clear use case
3. Explain why it's needed
4. Suggest implementation (if you have ideas)

### Title Format
`[FEATURE] Brief description of feature`

---

## 📚 Documentation Contributions

Help improve documentation by:
- Fixing typos/grammar
- Clarifying confusing sections
- Adding examples
- Creating tutorials
- Translating documentation

---

## 🎨 Code Review Guidelines

As a reviewer or reviewee:

### For Reviewers
- Be respectful and constructive
- Ask clarifying questions
- Suggest improvements, don't demand
- Acknowledge good solutions
- Test the changes locally

### For Authors
- Don't take feedback personally
- Explain your reasoning
- Ask for clarification if needed
- Make requested changes promptly

---

## 🚀 Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR:** Breaking changes
- **MINOR:** New features
- **PATCH:** Bug fixes

---

## 📧 Communication

- **Issues:** Technical discussions
- **Discussions:** Questions and ideas
- **Pull Requests:** Code changes
- **Email:** For private matters

---

## 🙏 Recognition

Contributors will be recognized in:
- README contributor section
- Release notes
- Project documentation

---

## ⚖️ Code of Conduct

- Be respectful and inclusive
- Welcome diverse perspectives
- Report inappropriate behavior
- Focus on constructive feedback
- No harassment or discrimination

---

## 🔐 Security

### Report Security Issues
- **DO NOT** open public issues for security vulnerabilities
- Email security@example.com with:
  - Description of vulnerability
  - Steps to reproduce
  - Potential impact
  - Suggested fix (optional)

---

## ❓ Questions?

- Check existing documentation
- Review similar projects/commits
- Ask in relevant issue/discussion
- Check project README

---

## 📖 Additional Resources

- [PROJECTS.md](./PROJECTS.md) - Project overview
- [SETUP.md](./SETUP.md) - Setup guide
- [Project READMEs](./VoiceStudio-Integrated/README.md)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)

---

## 🎉 Thank You!

Your contributions help make this project better for everyone. We appreciate your time and effort!

Happy coding! 🚀
