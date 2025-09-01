#!/bin/bash

# Script to run tests with coverage reporting

set -e

echo "Running authentication tests with coverage..."

# Clean previous coverage data
coverage erase

# Run tests with coverage
coverage run -m pytest . -v

echo ""
echo "Coverage Report Summary:"
echo "=========================="

# Show overall coverage
coverage report

echo ""
echo "Complete Coverage:"
echo "======================="

# Show auth-specific coverage
coverage report --include="." --omit="*/tests/*" --show-missing

echo ""
echo "Generating HTML Report..."

# Generate HTML report
coverage html --include="." --omit="*/tests/*"

echo ""
echo "Coverage analysis complete!"
echo "HTML report available at: htmlcov/index.html"
echo "Open with: open htmlcov/index.html"

# Try to open the report automatically (macOS)
if command -v open &> /dev/null; then
    echo "Opening coverage report in browser..."
    open htmlcov/index.html
fi
