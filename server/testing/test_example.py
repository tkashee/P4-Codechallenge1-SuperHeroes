# test_example.py
import pytest
from faker import Faker

def test_fake_name():
    fake = Faker()
    name = fake.name()
    assert isinstance(name, str)  # Check that the generated name is a string
