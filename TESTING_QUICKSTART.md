# Testing Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Backend Tests

```bash
# 1. Navigate to backend
cd backend

# 2. Install dependencies (if not already installed)
pip install -r requirements.txt

# 3. Run all tests
pytest

# 4. Run with coverage
pytest --cov=app --cov-report=html

# 5. View coverage report
# Open htmlcov/index.html in your browser
```

### Frontend Tests

```bash
# 1. Install dependencies (if not already installed)
npm install

# 2. Run all tests
npm test

# 3. Run with coverage
npm run test:coverage

# 4. Run in watch mode (for development)
npm run test:watch
```

## 📋 Common Test Commands

### Backend

```bash
# Run specific test types
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m property          # Property-based tests only
pytest -m agent             # Agent tests only

# Run specific test file
pytest tests/unit/test_agents.py

# Run specific test
pytest tests/unit/test_agents.py::TestUserProfileAgent::test_calculate_proficiency_bounds

# Run with verbose output
pytest -v

# Run quick tests (skip slow ones)
pytest -m "not slow"
```

### Frontend

```bash
# Run specific test file
npm test -- tests/property/skill-assessment.test.ts

# Run tests matching pattern
npm test -- --testNamePattern="proficiency"

# Update snapshots
npm test -- -u

# Run with verbose output
npm test -- --verbose
```

## 🎯 Test Markers (Backend)

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.property` - Property-based tests
- `@pytest.mark.agent` - Agent tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.slow` - Slow tests (skip with `-m "not slow"`)

## 📊 Coverage Reports

### Backend
After running `pytest --cov=app --cov-report=html`:
- Open `backend/htmlcov/index.html` in browser
- View line-by-line coverage
- Identify untested code

### Frontend
After running `npm run test:coverage`:
- Open `coverage/lcov-report/index.html` in browser
- View component coverage
- Identify untested components

## 🐛 Debugging Tests

### Backend

```bash
# Run with debugger
pytest --pdb

# Run with print statements visible
pytest -s

# Run single test with full output
pytest -vv -s tests/unit/test_agents.py::TestUserProfileAgent::test_calculate_proficiency_bounds
```

### Frontend

```bash
# Run with Node debugger
node --inspect-brk node_modules/.bin/jest --runInBand

# Run single test
npm test -- --testNamePattern="should produce identical results"
```

## ✅ Verify Everything Works

### Quick Smoke Test

```bash
# Backend
cd backend
pytest -m unit --maxfail=1

# Frontend
npm test -- --maxWorkers=1
```

If these pass, your testing infrastructure is working!

## 📚 Learn More

- Full guide: `TESTING_GUIDE.md`
- Phase 4 summary: `PHASE_4_TESTING_SUMMARY.md`
- Property definitions: `.kiro/specs/adaptive-learning-platform/design.md`

## 🆘 Troubleshooting

### Backend: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Backend: "Database error"
Tests use in-memory SQLite, no setup needed. Check `conftest.py` if issues persist.

### Frontend: "Cannot find module"
```bash
npm install
```

### Frontend: "Test timeout"
Increase timeout in `jest.config.js`:
```javascript
testTimeout: 10000  // 10 seconds
```

### Tests are slow
```bash
# Backend: Run in parallel
pytest -n auto

# Frontend: Run with fewer workers
npm test -- --maxWorkers=2
```

## 🎉 Success!

If tests are running, you're all set! Check out `TESTING_GUIDE.md` for advanced usage.
