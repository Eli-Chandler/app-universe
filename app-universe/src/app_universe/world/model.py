from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

@dataclass
class Person:
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: str
    sex: Literal["male", "female"]
    payment_cards: list[PaymentCard]
    addresses: list[Address]

    mother_id: int | None
    father_id: int | None
    spouse_id: int | None
    sibling_ids: list[int]
    child_ids: list[int]
    friend_ids: list[int]

    workplace: Company | None
    manager_id: int | None
    coworker_ids: list[int]
    subordinate_ids: list[int]

@dataclass
class PaymentCard:
    id: int
    type: str
    card_number: str
    expiration_date: str
    cardholder_name: str

@dataclass
class Address:
    id: int
    street: str
    city: str
    state: str
    zip_code: str
    country: str

@dataclass
class Company:
    id: int
    name: str
    employee_ids: list[int]
    addresses: list[Address]

@dataclass
class World:
    people: dict[int, Person]
    companies: dict[int, Company]

