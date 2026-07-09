#!/bin/bash

# Toronto Kids Events Scrapers Setup Script

echo "🎯 Toronto Kids Events Data Scrapers Setup"
echo "=============================="
echo ""

# Check Python version
echo "🐍 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ Found: $PYTHON_VERSION"
else
    echo "   ❌ Python 3 not found!"
    echo "   Install from: https://www.python.org/downloads/"
    exit 1
fi

echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "   ✅ Dependencies installed"
else
    echo "   ❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Check for EventBrite token
echo "🔑 Checking for EventBrite API token..."
if [ -z "$EVENTBRITE_TOKEN" ]; then
    echo "   ⚠️  No EventBrite token found"
    echo "   📝 To get live EventBrite data:"
    echo "      1. Visit: https://www.eventbrite.com/platform/api"
    echo "      2. Create an API key"
    echo "      3. Set environment variable:"
    echo "         export EVENTBRITE_TOKEN='your_token_here'"
    echo ""
    echo "   ℹ️  Sample data will be used for now"
else
    echo "   ✅ EventBrite token configured"
fi

echo ""

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x *.py
echo "   ✅ Done"

echo ""

# Run test
echo "🧪 Running test aggregation..."
python3 data_aggregator.py

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✅ Setup complete!"
    echo "================================"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Review generated files:"
    echo "      - events.json (for production)"
    echo "      - events_full.json (with metadata)"
    echo ""
    echo "   2. To update events daily, add to crontab:"
    echo "      0 6 * * * cd $(pwd) && python3 data_aggregator.py"
    echo ""
    echo "   3. Or use GitHub Actions (see README.md)"
    echo ""
else
    echo ""
    echo "❌ Setup failed"
    echo "Check error messages above"
    exit 1
fi
