.PHONY: create-world

install:
	uv pip install -e app-universe

generate-world: install
	uv run generators/world/generate_world.py