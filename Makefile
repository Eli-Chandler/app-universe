.PHONY: create-world

create-world:
	cd app-universe && uv run -m src.app_universe.world.generate --n_users 100 --output ../generate/world.json