from app_universe.world.generate import generate_world
from app_universe.paths import paths

if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Generate a random world.")
    parser.add_argument("--n_users", type=int, default=100, help="Number of users to generate.")
    parser.add_argument("--n_companies", type=int, default=10, help="Number of companies to generate.")
    parser.add_argument("--output", type=str, default=None, help="Output file path (default: data/world.json)")
    args = parser.parse_args()

    world = generate_world(n_users=args.n_users, n_companies=args.n_companies)

    # Use default path if not specified
    output_path = paths.world_json if args.output is None else paths.root / args.output

    # Ensure parent directory exists
    paths.ensure_exists(output_path, is_dir=False)

    with open(output_path, "w+") as f:
        json.dump(world, f, default=lambda o: o.__dict__, indent=2)

    print(f"World generated successfully: {output_path}")
