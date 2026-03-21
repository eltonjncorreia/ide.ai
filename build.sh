#!/bin/bash
# Build script for ide-ai PyInstaller executable
# Usage: ./build.sh [clean]

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPEC_FILE="$PROJECT_DIR/ide_ai.spec"
DIST_DIR="$PROJECT_DIR/dist"
BUILD_DIR="$PROJECT_DIR/build"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}[ide-ai] Building executable...${NC}"

# Clean if requested
if [[ "$1" == "clean" ]]; then
    echo "Cleaning build artifacts..."
    rm -rf "$BUILD_DIR" "$DIST_DIR"
fi

# Build using PyInstaller
python -m PyInstaller "$SPEC_FILE"

# Show result
EXECUTABLE="$DIST_DIR/ide-ai"
if [[ -f "$EXECUTABLE" ]]; then
    SIZE=$(ls -lh "$EXECUTABLE" | awk '{print $5}')
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo "Executable: $EXECUTABLE ($SIZE)"
else
    echo "❌ Build failed!"
    exit 1
fi
