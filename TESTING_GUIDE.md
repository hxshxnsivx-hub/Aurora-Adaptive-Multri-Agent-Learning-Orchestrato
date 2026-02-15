# Testing Guide - Adaptive Learning Platform

## Overview

This guide covers the comprehensive testing strategy for the Adaptive Learning Platform, including property-based testing, unit testing, integration testing, and end-to-end testing.

## Testing Philosophy

Our testing approach follows these principles:

1. **Property-Based Testing First**: Use Hypothesis (Python) and fast-check (TypeScript) to validate correctness properties
2. **Example-Based Testing**: Cover specific edge cases and integration scenarios
3. **Test Pyramid**: Many unit tests, fewer integration tests, minimal E2E tests
4. **Continuous Testing**: Run tests automatically on every commit

## Backend Testing (Python)

### Setup

```bash
cd backend
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m property          # Property-based tests only
pytest -m agent             # Agent tests only

# Run specific test file
pytest tests/unit/test_agents.py

# Run with verbose output
pytest -v

# Run in parallel (faster)
pytest -n auto
```

### Test Organization

```
backend/tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── unit/                          # Unit tests
│   ├── __init__.py
│   └── test_agents.py            # Agent unit tests
├── integration/                   # Integration tests
│   ├── __init__.py
│   └── test_api_endpoints.py     # API endpoint tests
└── property/                      # Property-based tests
    ├── __init__.py
    ├── test_skill_assessment.py  # Property 1
    └── test_learning_path_progression.py  # Property 2
```

### Property-Based Testing with Hypothesis

Property-based tests validate universal properties that must hold for all inputs:

```python
from hypothesis import given, strategies as st

@given(
    user_skills=user_skill_profile(),
    goals=learning_goals()
)
async def test_milestone_difficulty_monotonicity(user_skills, goals):
    """Milestone difficulty must be monotonically increasing."""
    agent = PathPlannerAgent()
    path = await agent.generate_path(user_profile={"skill_levels": user_skills}, goals=goals)
    
    milestones = path["milestones"]
    for i in range(len(milestones) - 1):
        assert milestones[i]["difficulty"] <= milestones[i + 1]["difficulty"]
```

### Writing New Tests

1. **Unit Tests**: Test individual functions/methods in isolation
2. **Integration Tests**: Test API endpoints and database interactions
3. **Property Tests**: Test universal properties that must always hold

Example unit test:

```python
@pytest.mark.unit
@pytest.mark.agent
async def test_user_profile_initialization():
    """Test user profile agent initializes correctly."""
    agent = UserProfileAgent()
    assert agent.agent_id == "user_profile"
    assert agent.name == "User Profile Agent"
```

## Frontend Testing (TypeScript)

### Setup

```bash
npm install
# or
yarn install
```

### Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run specific test file
npm test -- tests/property/skill-assessment.test.ts

# Run with verbose output
npm test -- --verbose
```

### Test Organization

```
tests/
├── property/                      # Property-based tests
│   └── skill-assessment.test.ts  # Skill assessment properties
├── unit/                          # Unit tests
│   ├── hooks.test.ts             # Custom hooks tests
│   └── services.test.ts          # Service layer tests
└── integration/                   # Integration tests
    └── components.test.tsx        # Component integration tests
```

### Property-Based Testing with fast-check

Property-based tests for frontend logic:

```typescript
import fc from 'fast-check';

describe('Skill Assessment Property Tests', () => {
  it('should produce identical results for identical inputs', () => {
    fc.assert(
      fc.property(
        fc.array(questionArbitrary, { minLength: 5, maxLength: 20 }),
        (questions) => {
          const result1 = calculateProficiency(questions, responses);
          const result2 = calculateProficiency(questions, responses);
          expect(result1).toEqual(result2);
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

### Writing New Tests

1. **Component Tests**: Test React components with React Testing Library
2. **Hook Tests**: Test custom hooks with @testing-library/react-hooks
3. **Service Tests**: Test API service layer
4. **Property Tests**: Test universal properties with fast-check

Example component test:

```typescript
import { render, screen } from '@testing-library/react';
import { Dashboard } from '@/components/dashboard/dashboard';

describe('Dashboard Component', () => {
  it('should render user progress', () => {
    render(<Dashboard />);
    expect(screen.getByText(/progress/i)).toBeInTheDocument();
  });
});
```

## Correctness Properties

The platform validates 12 correctness properties through property-based testing:

### Property 1: Skill Assessment Consistency
- **Validates**: Requirements 1.2, 1.3
- **Tests**: `test_skill_assessment.py`, `skill-assessment.test.ts`
- **Property**: Proficiency calculations must be deterministic and within [0.0, 1.0]

### Property 2: Learning Path Progression Validity
- **Validates**: Requirements 2.1, 2.2, 2.5
- **Tests**: `test_learning_path_progression.py`
- **Property**: Paths must follow progressive difficulty, all milestones reachable

### Property 3: Resource Curation Relevance
- **Validates**: Requirements 2.3, 4.5
- **Tests**: `test_resource_curation.py`
- **Property**: Resources must be semantically relevant and high quality

### Property 4: Schedule Optimization Feasibility
- **Validates**: Requirements 2.6, 3.2
- **Tests**: `test_schedule_optimization.py`
- **Property**: Schedules must respect availability and dependencies

### Property 5: Reallocation Coherence
- **Validates**: Requirements 3.1, 3.4
- **Tests**: `test_reallocation.py`
- **Property**: Reallocations must preserve goals and progression

### Property 6: Integration Synchronization Consistency
- **Validates**: Requirements 5.1, 5.4
- **Tests**: `test_integration_sync.py`
- **Property**: Sync operations must be consistent and lossless

### Property 7: Voice Command Processing Accuracy
- **Validates**: Requirements 6.2, 6.4
- **Tests**: `test_voice_processing.py`
- **Property**: Commands must be accurately extracted and executed

### Property 8: Real-time Update Propagation
- **Validates**: Requirements 7.2, 7.6
- **Tests**: `test_realtime_updates.py`
- **Property**: Updates must propagate within 5 seconds, preserve ordering

### Property 9: Multi-Agent Coordination Correctness
- **Validates**: Requirements 9.2, 9.5
- **Tests**: `test_agent_coordination.py`
- **Property**: Agent workflows must be correct and idempotent

### Property 10: Data Persistence Integrity
- **Validates**: Requirements 10.1, 10.2
- **Tests**: `test_data_persistence.py`
- **Property**: Data operations must be ACID compliant

### Property 11: Authentication Security
- **Validates**: Requirements 11.2, 11.3
- **Tests**: `test_authentication.py`
- **Property**: Auth must be secure, rate-limited, and properly enforced

### Property 12: Performance Bounds
- **Validates**: Requirements 12.1, 12.4
- **Tests**: `test_performance.py`
- **Property**: Operations must meet response time and scalability requirements

## Test Coverage Goals

### Backend
- **Overall Coverage**: 80%+
- **Critical Paths**: 95%+
- **Agents**: 85%+
- **API Endpoints**: 90%+

### Frontend
- **Overall Coverage**: 70%+
- **Components**: 75%+
- **Hooks**: 85%+
- **Services**: 90%+

## Continuous Integration

Tests run automatically on:
- Every commit to feature branches
- Pull requests to main
- Scheduled nightly runs

### CI Configuration

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run backend tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run frontend tests
        run: |
          npm install
          npm run test:coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Debugging Tests

### Backend

```bash
# Run with debugger
pytest --pdb

# Run with print statements visible
pytest -s

# Run specific test with verbose output
pytest -vv tests/unit/test_agents.py::TestUserProfileAgent::test_calculate_proficiency_bounds
```

### Frontend

```bash
# Run with debugger
node --inspect-brk node_modules/.bin/jest --runInBand

# Run specific test
npm test -- --testNamePattern="should produce identical results"
```

## Best Practices

1. **Write Tests First**: TDD approach for new features
2. **Test Behavior, Not Implementation**: Focus on what, not how
3. **Use Descriptive Names**: Test names should explain what they test
4. **Keep Tests Independent**: No shared state between tests
5. **Mock External Dependencies**: Use mocks for external APIs
6. **Test Edge Cases**: Cover boundary conditions
7. **Property Tests for Invariants**: Use PBT for universal properties
8. **Example Tests for Specifics**: Use example tests for specific scenarios

## Common Issues

### Issue: Tests Timeout
**Solution**: Increase timeout in pytest.ini or jest.config.js

### Issue: Async Tests Fail
**Solution**: Ensure proper async/await usage and event loop configuration

### Issue: Database Tests Fail
**Solution**: Check database fixtures and ensure proper cleanup

### Issue: Property Tests Find Edge Cases
**Solution**: This is good! Fix the code or adjust the property if needed

## Resources

- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [fast-check Documentation](https://fast-check.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
- [React Testing Library](https://testing-library.com/react)

## Getting Help

- Check test output for detailed error messages
- Review test fixtures in `conftest.py` and `jest.setup.js`
- Consult property definitions in `design.md`
- Ask team members for guidance on complex test scenarios
