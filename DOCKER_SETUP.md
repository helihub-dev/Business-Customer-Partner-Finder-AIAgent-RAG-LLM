# Docker Setup Guide

## Quick Start (3 Commands)

```bash
# 1. Start the application
docker-compose up -d

# 2. Initialize vector store (one-time)
docker-compose exec axlewave-discovery python setup_vectorstore.py

# 3. Open browser
# http://localhost:8501
```

That's it! Your app is now running with Python 3.11 + ChromaDB + Persistent Storage.

---

## What Docker Does

✅ **Automatic:**
- Installs Python 3.11
- Installs ChromaDB + sentence-transformers
- Installs all dependencies
- Sets up persistent volumes
- Runs Streamlit app

✅ **Persistent Data:**
- Vector store survives restarts (./data/vector_store/)
- Documents mounted (./data/axlewave_docs/)
- Logs preserved (./logs/)
- No venv needed (Docker isolation)

---

## Commands

### Start the app:
```bash
docker-compose up -d
```

### Initialize vector store (one-time):
```bash
docker-compose exec axlewave-discovery python setup_vectorstore.py
```

### Stop the app:
```bash
docker-compose down
```

### Rebuild after code changes:
```bash
docker-compose up --build -d
```

### Rebuild without cache (clean build):
```bash
docker-compose build --no-cache
docker-compose up -d
```

### View logs:
```bash
docker-compose logs -f axlewave-discovery
```

### Restart container:
```bash
docker-compose restart
```

---

## What You'll See

```
✓ Using ChromaDB with semantic embeddings
✓ Loaded 9 documents
✓ Vector store persisted to ./data/vector_store/
✓ Streamlit running on http://localhost:8501
```

**On subsequent restarts:**
```
✓ Vector store loaded in <1s (no rebuild needed)
```

---

## File Structure

```
axlewave-discovery/
├── Dockerfile              ← Docker config
├── docker-compose.yml      ← Container orchestration
├── .dockerignore          ← Ignore files
├── .env                   ← Your API keys
├── data/
│   ├── axlewave_docs/     ← Documents (mounted)
│   └── vector_store/      ← ChromaDB (persistent volume)
├── logs/
│   └── prompt_traces.json ← Trace history (mounted)
├── utils/                 ← Your code
├── agents/                ← Your code
└── app.py                 ← Your code
```

---

## Troubleshooting

### Port already in use:
```bash
# Change port in docker-compose.yml
ports:
  - "8502:8501"  # Use 8502 instead
```

### Vector store not loading:
```bash
# Initialize it
docker-compose exec axlewave-discovery python setup_vectorstore.py
```

### Need to reset everything:
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d
docker-compose exec axlewave-discovery python setup_vectorstore.py
```

### Check if Docker is running:
```bash
docker --version
docker-compose --version
docker-compose ps
```

### Container won't start:
```bash
# Check logs
docker-compose logs axlewave-discovery

# Rebuild
docker-compose down
docker-compose up --build -d
```

---

## Comparison

| Feature | Local Python | Docker |
|---------|-------------|--------|
| Python Version | 3.7+ | 3.11 ✓ |
| ChromaDB | Manual install | ✓ |
| Semantic Search | Manual setup | ✓ |
| Persistence | Manual | Automatic ✓ |
| Isolation | venv | Container ✓ |
| Setup Time | 10-15 min | 2 minutes |
| Portability | Low | High ✓ |

---

## Benefits

**Persistence:**
- Vector store survives restarts
- No rebuild needed (<1s load time)
- Data in ./data/vector_store/

**Isolation:**
- No venv needed
- No Python version conflicts
- Clean environment

**Portability:**
- Works on any machine with Docker
- Consistent across all environments
- Easy deployment

---

## Next Steps

1. **Make sure Docker is installed:**
   ```bash
   docker --version
   docker-compose --version
   ```

2. **Start the application:**
   ```bash
   docker-compose up -d
   ```

3. **Initialize vector store (one-time):**
   ```bash
   docker-compose exec axlewave-discovery python setup_vectorstore.py
   ```

4. **Access the app:**
   - Open: http://localhost:8501
   - You'll see "Using ChromaDB with semantic embeddings"
   - Vector store loads in <1s on subsequent runs

That's all! Your app is production-ready with Docker.
