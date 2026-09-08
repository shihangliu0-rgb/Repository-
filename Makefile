.PHONY: install test demo report clean

install:
	python -m venv .venv
	.venv/bin/pip install -e ".[dev]"

test:
	.venv/bin/python -m pytest -q

demo:
	.venv/bin/python -m repolens . --no-color --todos

report:
	.venv/bin/python -m repolens . --html report.html --json repolens.json

serve:
	.venv/bin/python -m repolens serve . --port 8000

clean:
	rm -rf report.html repolens.json repolens.md .pytest_cache **/__pycache__
