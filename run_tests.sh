#!/bin/bash
# run_tests.sh
# This script activates the virtual environment and runs pytest.
# It exits with 0 if all tests pass, or 1 if any test fails.

echo "🔹 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source .venv/bin/activate 2>/dev/null || echo "⚠️  No virtual environment found, continuing..."

echo "🔹 Running test suite..."
pytest -v
RESULT=$?

if [ $RESULT -eq 0 ]; then
  echo "✅ All tests passed!"
else
  echo "❌ Some tests failed!"
fi

echo "🔹 Exiting with code $RESULT"
exit $RESULT
