ruff: 
	uv run ruff check --fix src/

semver:
	uv run semverer check src/