#!/bin/bash
# Installation script for ide-ai (Linux)
# Usage: ./install-linux.sh [VERSION] [DEST]

set -e

VERSION="${1:-latest}"
DEST="${2:-/usr/local/bin}"

if [ "$VERSION" == "latest" ]; then
    echo "Fetching latest release info..."
    DOWNLOAD_URL=$(curl -s https://api.github.com/repos/seu-usuario/ide.ai/releases/latest | grep "ide-ai-linux-x64" | grep "browser_download_url" | cut -d '"' -f 4)
else
    DOWNLOAD_URL="https://github.com/seu-usuario/ide.ai/releases/download/v${VERSION}/ide-ai-linux-x64"
fi

if [ -z "$DOWNLOAD_URL" ]; then
    echo "❌ Error: Could not find download URL for ide-ai version $VERSION"
    exit 1
fi

echo "📥 Downloading ide-ai from: $DOWNLOAD_URL"
curl -L "$DOWNLOAD_URL" -o /tmp/ide-ai

echo "🔧 Installing to $DEST..."
if [ ! -w "$DEST" ]; then
    sudo mv /tmp/ide-ai "$DEST/ide-ai"
    sudo chmod +x "$DEST/ide-ai"
else
    mv /tmp/ide-ai "$DEST/ide-ai"
    chmod +x "$DEST/ide-ai"
fi

echo "✅ Installation complete!"
echo "Run 'ide-ai' from any terminal to start"
