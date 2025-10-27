#!/bin/bash
# Test runner script for Interview Tracker

echo "🧪 Interview Tracker Test Suite"
echo "================================"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not detected. Activating..."
    source .venv/bin/activate
fi

# Install test dependencies if needed
echo "📦 Installing test dependencies..."
pip install -q pytest pytest-cov

echo ""
echo "🏃 Running tests..."
echo ""

# Run different test suites based on argument
case "$1" in
    "unit")
        echo "Running unit tests only..."
        pytest tests/test_models.py tests/test_data_manager.py tests/test_analytics.py -v -m "unit"
        ;;
    "integration")
        echo "Running integration tests only..."
        pytest tests/test_integration.py -v -m "integration"
        ;;
    "fast")
        echo "Running fast tests only (excluding slow tests)..."
        pytest -v -m "not slow"
        ;;
    "coverage")
        echo "Running tests with coverage report..."
        pytest --cov=. --cov-report=html --cov-report=term-missing
        echo ""
        echo "📊 Coverage report generated in htmlcov/index.html"
        ;;
    "verbose")
        echo "Running all tests with verbose output..."
        pytest -v -s
        ;;
    *)
        echo "Running all tests..."
        pytest -v
        ;;
esac

echo ""
echo "✅ Test run completed!"
echo ""
echo "Available options:"
echo "  ./run_tests.sh unit        - Run unit tests only"
echo "  ./run_tests.sh integration - Run integration tests only" 
echo "  ./run_tests.sh fast        - Run fast tests (skip slow ones)"
echo "  ./run_tests.sh coverage    - Run with coverage report"
echo "  ./run_tests.sh verbose     - Run with verbose output"