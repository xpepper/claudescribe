.PHONY: install build run dev

install:
	pip install -r requirements.txt
	cd frontend && npm install

build:
	cd frontend && npm run build

run: build
	python main.py

dev:
	@echo "Start backend: PORT=$(PORT) uvicorn backend.app:app --reload --port $${PORT:-8000}"
	@echo "Start frontend: PORT=$(PORT) npm run dev  (inside frontend/)"
