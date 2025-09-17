#!/bin/bash

# ZynxAGI Monorepo Validation Script
# First discovered by Chanont Waenkaew, Thailand
# License: ZPDL v1.0 © Chanont Waenkaew

set -e

echo "🔍 Validating ZynxAGI Monorepo Structure..."

# Check required files
echo "📋 Checking required files..."
if [ -f "LICENSE" ]; then
    echo "✅ LICENSE file found"
    grep -q "Chanont Waenkaew" LICENSE && echo "✅ Attribution found in LICENSE"
else
    echo "❌ LICENSE file missing"
    exit 1
fi

if [ -f "README.md" ]; then
    echo "✅ README.md found"
    grep -q "monorepo" README.md && echo "✅ Monorepo documentation found"
else
    echo "❌ README.md missing"
    exit 1
fi

# Check lovable.dev structure
echo "📋 Checking lovable.dev structure..."
if [ -d "lovable.dev" ]; then
    echo "✅ lovable.dev directory found"
    if [ -f "lovable.dev/manifest.yaml" ]; then
        echo "✅ lovable.dev manifest found"
    else
        echo "❌ lovable.dev manifest missing"
        exit 1
    fi
    if [ -f "lovable.dev/package.json" ]; then
        echo "✅ lovable.dev package.json found"
    else
        echo "❌ lovable.dev package.json missing"
        exit 1
    fi
else
    echo "❌ lovable.dev directory missing"
    exit 1
fi

# Check zynx_agi structure
echo "📋 Checking zynx_agi structure..."
if [ -d "zynx_agi" ]; then
    echo "✅ zynx_agi directory found"
    if [ -f "zynx_agi/manifest.yaml" ]; then
        echo "✅ zynx_agi manifest found"
    else
        echo "❌ zynx_agi manifest missing"
        exit 1
    fi
    if [ -f "zynx_agi/main.py" ]; then
        echo "✅ zynx_agi main.py found"
    else
        echo "❌ zynx_agi main.py missing"
        exit 1
    fi
else
    echo "❌ zynx_agi directory missing"
    exit 1
fi

# Test Python backend
echo "🐍 Testing Python backend..."
python -c "from zynx_agi.main import app; print('✅ Backend imports successfully')"

# Test lovable.dev build
echo "🏗️ Testing lovable.dev build..."
cd lovable.dev
npm run build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Frontend builds successfully"
else
    echo "❌ Frontend build failed"
    exit 1
fi
cd ..

# Test Python tests
echo "🧪 Running Python tests..."
python -m pytest tests/test_universal_dispatcher.py -v > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Backend tests pass"
else
    echo "❌ Backend tests failed"
    exit 1
fi

echo ""
echo "🎉 All validation checks passed!"
echo "📦 Monorepo structure is ready for deployment"
echo ""
echo "🚀 To start services:"
echo "   Backend:  uvicorn zynx_agi.main:app --host 0.0.0.0 --port 8000"
echo "   Frontend: cd lovable.dev && npm run dev"
echo ""
echo "🔗 Access points:"
echo "   Backend API: http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo "   Frontend:    http://localhost:5173"
echo ""
echo "✨ First discovered by Chanont Waenkaew, Thailand"