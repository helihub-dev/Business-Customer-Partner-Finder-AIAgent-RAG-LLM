#!/bin/bash
# View real-time logs from Docker container

echo "📋 Viewing AxleWave Discovery logs..."
echo "Press Ctrl+C to stop"
echo ""

docker-compose logs -f --tail=100 axlewave-discovery
