#!/bin/bash

# Test runner script for Adaptive Learning Platform backend

set -e

echo "================================"
echo "Adaptive Learning Platform Tests"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
TEST_TYPE="${1:-all}"
COVERAGE="${2:-false}"

echo "Test Type: $TEST_TYPE"
echo "Coverage: $COVERAGE"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install dependencies if needed
if [ ! -d "venv" ] || [ ! -f "venv/bin/pytest" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt
fi

# Run tests based on type
case $TEST_TYPE in
    "all")
        echo -e "${GREEN}Running all tests...${NC}"
        if [ "$COVERAGE" = "true" ]; then
            pytest --cov=app --cov-report=html --cov-report=term-missing
        else
            pytest -v
        fi
        ;;
    
    "unit")
        echo -e "${GREEN}Running unit tests...${NC}"
        pytest -m unit -v
        ;;
    
    "integration")
        echo -e "${GREEN}Running integration tests...${NC}"
        pytest -m integration -v
        ;;
    
    "property")
        echo -e "${GREEN}Running property-based tests...${NC}"
        pytest -m property -v
        ;;
    
    "agent")
        echo -e "${GREEN}Running agent tests...${NC}"
        pytest -m agent -v
        ;;
    
    "api")
        echo -e "${GREEN}Running API tests...${NC}"
        pytest -m api -v
        ;;
    
    "quick")
        echo -e "${GREEN}Running quick tests (no slow tests)...${NC}"
        pytest -m "not slow" -v
        ;;
    
    "coverage")
        echo -e "${GREEN}Running tests with coverage report...${NC}"
        pytest --cov=app --cov-report=html --cov-report=term-missing
        echo ""
        echo -e "${GREEN}Coverage report generated in htmlcov/index.html${NC}"
        ;;
    
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: ./run_tests.sh [test_type] [coverage]"
        echo ""
        echo "Test types:"
        echo "  all         - Run all tests (default)"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  property    - Run property-based tests only"
        echo "  agent       - Run agent tests only"
        echo "  api         - Run API tests only"
        echo "  quick       - Run quick tests (exclude slow tests)"
        echo "  coverage    - Run all tests with coverage report"
        echo ""
        echo "Coverage: true|false (default: false)"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh all true"
        echo "  ./run_tests.sh unit"
        echo "  ./run_tests.sh property"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
