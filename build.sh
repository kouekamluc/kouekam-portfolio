#!/bin/bash
# Production build script for CSS
# This script builds the Tailwind CSS for production

set -e

echo "Building Tailwind CSS for production..."

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ ERROR: Node.js is not installed!"
    echo "   Please install Node.js to build CSS"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ ERROR: npm is not installed!"
    echo "   Please install npm to build CSS"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm ci --silent || npm install --silent
fi

# Build CSS
echo "Compiling Tailwind CSS..."
npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify

# Verify the build
if [ -f "static/css/output.css" ] && [ -s "static/css/output.css" ]; then
    CSS_SIZE=$(wc -c < static/css/output.css)
    echo "✓ CSS built successfully ($CSS_SIZE bytes)"
    exit 0
else
    echo "❌ ERROR: CSS build failed!"
    exit 1
fi

