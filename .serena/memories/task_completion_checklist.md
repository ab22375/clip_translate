# Task Completion Checklist

When completing any development task, run these commands:

## 1. Code Quality Checks
```bash
# Format code
ruff format .

# Lint and auto-fix
ruff check . --fix

# Type check
mypy src/

# Ensure pre-commit hooks pass
pre-commit run --all-files
```

## 2. Testing
```bash
# Run full test suite
pytest

# Run with coverage (minimum 80% required)
pytest --cov=src --cov-fail-under=80
```

## 3. Manual Testing (if applicable)
```bash
# Test CLI functionality
clip_translate translate -s ja -t en --once

# Test GUI functionality  
clip_translate_gui -s ja -t en
```

## 4. Documentation Updates
- Update CLAUDE.md if project instructions change
- Update README.md if user-facing features change
- Update docstrings for new/modified functions

## 5. Git Workflow
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: description of changes"

# Only push when explicitly requested by user
```

## Required Passing Criteria
- All tests pass
- Coverage >= 80%
- No linting errors
- No type errors
- Pre-commit hooks pass
- Manual testing confirms functionality works