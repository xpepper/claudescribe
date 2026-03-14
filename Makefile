.PHONY: install build run dev

install:
	pip install -r requirements.txt
	cd frontend && npm install

build:
	cd frontend && npm run build

run: build
	python main.py

dev:
	@echo "Start backend: uvicorn backend.app:app --reload --port 8000"
	@echo "Start frontend: cd frontend && npm run dev"
