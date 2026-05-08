"""Factory helpers for generating test payloads."""

from faker import Faker

fake = Faker()


def make_user(**overrides) -> dict:
    data = {
        "name": fake.name(),
        "username": fake.user_name(),
        "email": fake.email(),
        "phone": fake.phone_number(),
        "website": fake.domain_name(),
        "address": {
            "street": fake.street_name(),
            "suite": fake.secondary_address(),
            "city": fake.city(),
            "zipcode": fake.zipcode(),
        },
        "company": {
            "name": fake.company(),
            "catchPhrase": fake.catch_phrase(),
            "bs": fake.bs(),
        },
    }
    data.update(overrides)
    return data


def make_post(user_id: int = 1, **overrides) -> dict:
    data = {
        "userId": user_id,
        "title": fake.sentence(nb_words=6),
        "body": fake.paragraph(nb_sentences=3),
    }
    data.update(overrides)
    return data
