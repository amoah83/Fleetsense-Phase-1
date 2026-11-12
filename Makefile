setup:
	pip install -r requirements.txt
ingest:
	python Src/ingestion.py
lint:
	ruff check Src/
test:
	pytest