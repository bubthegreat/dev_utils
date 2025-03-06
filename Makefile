ruff: 
	uv run ruff check --fix src/

check:
	uv run semverer check src/

update:
	uv run semverer update src/
