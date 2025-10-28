# Contributing to TuxFw

Thank you for your interest in contributing to TuxFw! We welcome contributions from everyone, whether you're a developer, tester, documenter, or just someone with a great idea.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Requests](#pull-requests)
- [Development Setup](#development-setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running Tests](#running-tests)
- [Coding Standards](#coding-standards)
  - [Python](#python)
  - [Documentation](#documentation)
  - [Git Commit Messages](#git-commit-messages)
- [License](#license)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report any unacceptable behavior to [Nsfr750](mailto:nsfr750@yandex.com).

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check the [existing issues](https://github.com/Nsfr750/TuxFw/issues) to see if the problem has already been reported.

#### How to Submit a Good Bug Report

1. **Use a clear and descriptive title** for the issue to identify the problem.
2. **Describe the exact steps** to reproduce the problem in as much detail as possible.
3. **Provide specific examples** to demonstrate the steps.
4. **Describe the behavior you observed** after following the steps.
5. **Explain which behavior you expected** to see instead and why.
6. **Include screenshots and animated GIFs** if they help demonstrate the issue.
7. **List your environment** (OS, Python version, etc.).

### Suggesting Enhancements

We welcome enhancement suggestions. Before creating an enhancement suggestion, please check if the feature has already been requested.

#### How to Submit a Good Enhancement Suggestion

1. **Use a clear and descriptive title** for the feature request.
2. **Provide a step-by-step description** of the suggested enhancement.
3. **Explain why this enhancement would be useful** to most TuxFw users.
4. **List any alternative solutions** you've considered.
5. **Include any additional context** about the suggestion.

### Your First Code Contribution

Unsure where to begin contributing? You can start by looking through the `good first issue` and `help wanted` issues in our [issue tracker](https://github.com/Nsfr750/TuxFw/issues).

### Pull Requests

1. Fork the repository and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- pip
- Virtual environment (recommended)

### Installation

1. Fork the repository
2. Clone your fork:

   ```bash
   git clone https://github.com/your-username/TuxFw.git
   cd TuxFw
   ```

3. Set up a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

5. Add upstream remote (optional):

   ```bash
   git remote add upstream https://github.com/Nsfr750/TuxFw.git
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

### Running Tests

```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_module.py

# Run tests with coverage report
pytest --cov=firewall tests/
```

## Coding Standards

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for all function signatures
- Keep functions small and focused on a single task
- Write docstrings for all public modules, functions, classes, and methods
- Use absolute imports
- Keep lines under 100 characters

Example:
```python
def example_function(param1: str, param2: int = 42) -> bool:
    """
    Example function with proper formatting and documentation.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 42)

    Returns:
        bool: Description of return value
    """
    if not param1:
        return False
    
    return param2 > len(param1)
```

### Documentation

- Use Google style docstrings
- Document all public APIs
- Keep documentation up-to-date with code changes
- Write clear, concise, and complete docstrings
- Include examples for complex functions

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line
- Consider starting the commit message with an applicable emoji:
  - ✨ `:sparkles:` When adding a new feature
  - 🐛 `:bug:` When fixing a bug
  - 📝 `:memo:` When writing docs
  - ♻️ `:recycle:` When refactoring code
  - 🚧 `:construction:` When work is in progress
  - ✅ `:white_check_mark:` When adding tests
  - 🔧 `:wrench:` When fixing the build
  - ⚡ `:zap:` When improving performance

## License

By contributing to TuxFw, you agree that your contributions will be licensed under the [GPLv3 License](LICENSE).

---
© 2025 Nsfr750 - All rights reserved
