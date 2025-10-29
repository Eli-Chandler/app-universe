import random
from typing import Literal

from app_universe.world.model import World, PaymentCard, Address, Person
import faker

fake = faker.Faker()

def random_payment_card(person_name: str, idx: int) -> PaymentCard:

    return PaymentCard(
        id=idx,
        type=random.choice(["Visa", "MasterCard", "Amex"]),
        card_number=fake.credit_card_number(),
        expiration_date=fake.credit_card_expire(),
        cardholder_name=person_name
    )

def random_address(idx: int) -> Address:
    return Address(
        id=idx,
        street=fake.street_address(),
        city=fake.city(),
        state=fake.state(),
        zip_code=fake.zipcode(),
        country=fake.country()
    )

def biased_random_count(min_val=1, max_val=3, bias_toward=1):
    weights = [3 if i == bias_toward else 1 for i in range(min_val, max_val + 1)]
    return random.choices(range(min_val, max_val + 1), weights=weights, k=1)[0]

def realistic_email(first_name: str, last_name: str, birth_year: int) -> str:
    domain = "@gmail.com"
    name_variants = [
        f"{first_name}.{last_name}",
        f"{first_name[0]}{last_name}",
        f"{first_name}{last_name[0]}"
    ]
    birth_year_variants = [
        "",
        str(birth_year),
        str(birth_year)[-2:]
    ]
    return f"{random.choice(name_variants)}{random.choice(birth_year_variants)}{domain}".lower()

def random_person(person_id: int) -> Person:
    first = fake.first_name()
    last = fake.last_name()
    sex: Literal['male', 'female'] = random.choice(["male", "female"])
    birthday = fake.date_of_birth(minimum_age=18, maximum_age=80)
    birth_year = birthday.year
    num_cards = biased_random_count()
    num_addresses = biased_random_count()

    return Person(
        id=person_id,
        first_name=first,
        last_name=last,
        email=realistic_email(first, last, birth_year),
        phone_number=fake.phone_number(),
        birthday=str(birthday),
        sex=sex,
        payment_cards=[random_payment_card(f"{first} {last}", i) for i in range(num_cards)],
        addresses=[random_address(i) for i in range(num_addresses)],
        mother_id=None,
        father_id=None,
        spouse_id=None,
        sibling_ids=[],
        child_ids=[],
        friend_ids=[],
        workplace=None,
        manager_id=None,
        coworker_ids=[],
        subordinate_ids=[]
    )

def generate_world(n_users: int, n_companies: int) -> World:
    # TODO: Actually populate the rest of the data

    world = World(people={}, companies={})

    for person_id in range(1, n_users + 1):
        person = random_person(person_id)
        world.people[person_id] = person

    return world

if __name__ == "__main__":
    import argparse
    import json
    import os
    parser = argparse.ArgumentParser(description="Generate a random world.")
    parser.add_argument("--n_users", type=int, default=100, help="Number of users to generate.")
    parser.add_argument("--n_companies", type=int, default=10, help="Number of companies to generate.")
    parser.add_argument("--output", type=str, required=True, help="Output file path.")
    args = parser.parse_args()

    world = generate_world(n_users=args.n_users, n_companies=args.n_companies)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    with open(args.output, "w+") as f:
        json.dump(world, f, default=lambda o: o.__dict__, indent=2)