#!/bin/bash
# Diagnostic script for AxleWave Discovery

echo "🔍 AxleWave Discovery Diagnostics"
echo "=================================="
echo ""

# Check if Docker is running
echo "1️⃣  Checking Docker..."
if docker info > /dev/null 2>&1; then
    echo "   ✅ Docker is running"
else
    echo "   ❌ Docker is not running"
    exit 1
fi
echo ""

# Check if container is running
echo "2️⃣  Checking container status..."
if docker-compose ps | grep -q "Up"; then
    echo "   ✅ Container is running"
    CONTAINER_STATUS=$(docker-compose ps | grep axlewave-discovery | awk '{print $4}')
    echo "   Status: $CONTAINER_STATUS"
else
    echo "   ❌ Container is not running"
    echo "   Run: docker-compose up -d"
    exit 1
fi
echo ""

# Check API keys
echo "3️⃣  Checking API keys..."
TAVILY_KEY=$(docker-compose exec -T axlewave-discovery env | grep TAVILY_API_KEY | cut -d= -f2)
OPENAI_KEY=$(docker-compose exec -T axlewave-discovery env | grep OPENAI_API_KEY | cut -d= -f2)

if [ -n "$TAVILY_KEY" ]; then
    echo "   ✅ TAVILY_API_KEY is set"
else
    echo "   ❌ TAVILY_API_KEY is missing"
fi

if [ -n "$OPENAI_KEY" ]; then
    echo "   ✅ OPENAI_API_KEY is set"
else
    echo "   ⚠️  OPENAI_API_KEY is missing (check other providers)"
fi
echo ""

# Check vector store
echo "4️⃣  Checking vector store..."
if [ -f "data/vector_store/chroma.sqlite3" ]; then
    SIZE=$(du -h data/vector_store/chroma.sqlite3 | cut -f1)
    echo "   ✅ Vector store exists ($SIZE)"
else
    echo "   ❌ Vector store not initialized"
    echo "   Run: docker-compose exec axlewave-discovery python setup_vectorstore.py"
fi
echo ""

# Check port availability
echo "5️⃣  Checking port 8501..."
if lsof -i :8501 > /dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":8501"; then
    echo "   ✅ Port 8501 is in use (app should be accessible)"
else
    echo "   ⚠️  Port 8501 is not in use"
fi
echo ""

# Check recent logs for errors
echo "6️⃣  Checking recent logs for errors..."
ERROR_COUNT=$(docker-compose logs --tail=100 axlewave-discovery 2>&1 | grep -i "error\|exception\|failed" | wc -l)
if [ "$ERROR_COUNT" -eq 0 ]; then
    echo "   ✅ No recent errors found"
else
    echo "   ⚠️  Found $ERROR_COUNT error messages"
    echo "   Run: ./view_logs.sh to investigate"
fi
echo ""

# Check Docker resources
echo "7️⃣  Checking Docker resources..."
STATS=$(docker stats --no-stream --format "{{.CPUPerc}} {{.MemUsage}}" axlewave-discovery 2>/dev/null)
if [ -n "$STATS" ]; then
    CPU=$(echo $STATS | awk '{print $1}')
    MEM=$(echo $STATS | awk '{print $2}')
    echo "   CPU: $CPU"
    echo "   Memory: $MEM"
else
    echo "   ⚠️  Could not get resource stats"
fi
echo ""

# Summary
echo "=================================="
echo "📊 Summary"
echo "=================================="
echo ""
echo "Access the app at: http://localhost:8501"
echo ""
echo "Useful commands:"
echo "  • View logs:    ./view_logs.sh"
echo "  • Restart:      docker-compose restart"
echo "  • Rebuild:      docker-compose up --build -d"
echo "  • Stop:         docker-compose down"
echo ""
echo "For detailed troubleshooting, see: TROUBLESHOOTING.md"
