# Contributing to File Organizer

Thank you for your interest in contributing to File Organizer! This document provides guidelines and instructions for contributing to this Open Science initiative.

## Open Science Principles

As part of imediacorp's Open Science commitment, we value:

- **Reproducibility**: All changes should maintain or improve reproducibility features
- **Transparency**: Code should be well-documented and clear
- **Falsifiability**: Features should be testable and verifiable
- **Open Collaboration**: We welcome diverse perspectives and contributions

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check if the issue already exists in the GitHub Issues
2. If not, create a new issue with:
   - Clear description of the problem or feature
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Environment details (OS, Python version, etc.)

### Contributing Code

1. **Fork the repository** on GitHub
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following our coding standards
4. **Add tests** for new features or bug fixes
5. **Update documentation** as needed
6. **Commit your changes** with clear, descriptive commit messages
7. **Push to your fork** and create a Pull Request

### Coding Standards

- Follow PEP 8 style guidelines
- Write clear, self-documenting code
- Add docstrings to functions and classes
- Include type hints where appropriate
- Write tests for new functionality
- Ensure all tests pass before submitting

### Testing

Before submitting a PR:

```bash
# Run tests (when test suite is available)
python -m pytest

# Run linting
flake8 file_organizer/

# Check type hints (if using mypy)
mypy file_organizer/
```

### Documentation

- Update README.md if adding new features
- Add docstrings to new functions/classes
- Update configuration examples if changing config structure
- Keep the Open Science section accurate

### Commit Messages

Use clear, descriptive commit messages:

```
feat: Add support for custom file naming patterns
fix: Resolve transaction log corruption on Windows
docs: Update installation instructions for macOS
refactor: Simplify AI provider selection logic
```

## Areas for Contribution

We particularly welcome contributions in:

- **Reproducibility Features**: Improvements to transaction logging, rollback, dry-run
- **Documentation**: Examples, tutorials, use cases
- **Testing**: Test coverage, edge cases, integration tests
- **Performance**: Optimization, caching, large file handling
- **New Strategies**: Additional organization strategies
- **AI Integration**: Improvements to Eratosthenes agent
- **Cross-Platform**: Windows, macOS, Linux compatibility improvements

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Respect different perspectives and experiences

## Questions?

- Open an issue for questions or discussions
- Check existing issues and discussions
- Review the documentation in the README

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

*Thank you for helping make File Organizer a better tool for the Open Science community!*

