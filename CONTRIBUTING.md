# Contributing to Kiosk Clock

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to Kiosk Clock. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and what behavior you expected**
- **Include screenshots if applicable**
- **Specify your platform details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **List some other applications where this enhancement exists, if applicable**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Make your changes** and ensure they follow our coding standards
4. **Add tests** for your changes if applicable
5. **Update documentation** if necessary
6. **Ensure all tests pass**
7. **Create a pull request** with a clear description

## Development Setup

### Prerequisites

- Python 3.7+
- Git
- Virtual environment (recommended)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/your-username/kiosk-clock.git
cd kiosk-clock

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Install pre-commit hooks (if available)
pre-commit install
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test
python -m pytest tests/test_specific.py
```

### Code Style

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Use Black** for code formatting
- **Use flake8** for linting
- **Use type hints** where possible

```bash
# Format code
black .

# Check linting
flake8 .

# Type checking (if mypy is available)
mypy .
```

## Project Structure

```
kiosk-clock/
├── kiosk_clock_app.py          # Main application entry point
├── config.py                   # Configuration management
├── utils.py                    # Utility functions
├── *_manager.py               # Feature-specific managers
├── tests/                     # Test suite
├── docs/                      # Documentation
├── weather_icons/             # Asset files
└── examples/                  # Example configurations
```

## Coding Guidelines

### Python Code

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all classes and functions
- Use type hints for function parameters and return values
- Handle exceptions gracefully with proper logging

### Example Function

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
    """
    try:
        # Implementation here
        return True
    except Exception as e:
        logger.error(f"Error in example_function: {e}")
        return False
```

### Logging

Use the existing logging infrastructure:

```python
import logging

logger = logging.getLogger('kiosk_clock.module_name')

# Log levels
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
```

### Configuration

Add new configuration options to `config.py`:

```python
# Add to appropriate section
NEW_FEATURE_ENABLED = True
NEW_FEATURE_TIMEOUT = 30

# For user-configurable options, add to UserConfig class
class UserConfig:
    def __init__(self):
        # ... existing config ...
        self.new_feature_setting = os.getenv('KIOSK_NEW_FEATURE', 'default')
```

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies

```python
import pytest
from unittest.mock import Mock, patch

def test_example_function_success():
    """Test that example_function works correctly."""
    result = example_function("valid_input")
    assert result is True

def test_example_function_failure():
    """Test that example_function handles errors gracefully."""
    with pytest.raises(ValueError):
        example_function("invalid_input")
```

### Test Categories

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include examples in docstrings when helpful

### README Updates

When adding features:
- Update the feature list in README.md
- Add configuration examples
- Update troubleshooting section if needed

## Commit Messages

Use clear and descriptive commit messages:

```
feat: add weather radar display
fix: resolve calendar authentication issue
docs: update installation instructions
refactor: improve error handling in audio manager
test: add tests for alarm manager
```

Prefixes:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

## Review Process

### Pull Request Requirements

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] PR description explains changes

### Review Criteria

Reviewers will check:
- Code quality and style
- Test coverage
- Documentation completeness
- Backward compatibility
- Performance impact

## Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Getting Help

- 💬 **Discord**: [Join our Discord server](https://discord.gg/your-discord)
- 📧 **Email**: maintainer@example.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/kiosk-clock/issues)
- 💡 **Discussions**: [GitHub Discussions](https://github.com/your-username/kiosk-clock/discussions)

## Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Hall of Fame (coming soon!)

Thank you for contributing! 🚀 