#!/bin/bash
# Production build script for CSS and JS
# This script builds the Tailwind CSS and Tiptap editor JS for production

set -e

echo "Building assets for production..."

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ ERROR: Node.js is not installed!"
    echo "   Please install Node.js to build assets"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ ERROR: npm is not installed!"
    echo "   Please install npm to build assets"
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

# Build JS
echo "Bundling Tiptap editor JavaScript..."
npm run build:js

# Verify the builds
if [ -f "static/css/output.css" ] && [ -s "static/css/output.css" ]; then
    CSS_SIZE=$(wc -c < static/css/output.css)
    echo "✓ CSS built successfully ($CSS_SIZE bytes)"
else
    echo "❌ ERROR: CSS build failed!"
    exit 1
fi

if [ -f "static/js/tiptap-editor.js" ] && [ -s "static/js/tiptap-editor.js" ]; then
    JS_SIZE=$(wc -c < static/js/tiptap-editor.js)
    echo "✓ JavaScript built successfully ($JS_SIZE bytes)"
    exit 0
else
    echo "❌ ERROR: JavaScript build failed!"
    exit 1
fi



