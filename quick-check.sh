#!/bin/bash

# 1. Build & start
docker compose up -d --build

sleep 10


# 2. Happy path
curl -s 'http://localhost:8000/scrape?category=Apparel'

sleep 10

# 3. Lint & tests
docker compose exec api pytest -q
docker compose exec api ruff check .

# 4. Shutdown
docker compose down