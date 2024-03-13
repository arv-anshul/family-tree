import json
from datetime import date
from pathlib import Path

import pytest
from family_tree.family_tree import FamilyTree, Gender, Person


@pytest.fixture
def sample_person() -> Person:
    return Person(name="John Doe", gender=Gender.male, dob=date(1980, 1, 1))


@pytest.fixture
def sample_family_tree(sample_person: Person) -> FamilyTree:
    return FamilyTree(name="Doe Family", main_member=sample_person)


def test_person_creation(sample_person: Person):
    assert sample_person.name == "John Doe"
    assert sample_person.gender == Gender.male
    assert sample_person.dob == date(1980, 1, 1)


def test_add_children_to_person(sample_person: Person):
    child1 = Person(name="Child1", gender=Gender.male)
    child2 = Person(name="Child2", gender=Gender.female)
    sample_person.add_children(child1, child2)

    children = sample_person.get_children()
    if children is None:
        raise ValueError("children is None")
    assert child1 in children and child2 in children


def test_set_spouse_for_person(sample_person: Person):
    spouse = Person(name="Jane Doe", gender=Gender.female)
    sample_person.set_spouse(spouse)

    assert sample_person.get_spouse() == spouse
    assert spouse.get_spouse() == sample_person


def test_export_family_tree_to_json(tmp_path: Path, sample_family_tree: FamilyTree):
    expected_output = {
        "name": "John Doe",
        "gender": "male",
        "dob": "1980-01-01",
    }
    sample_family_tree.write_json(tmp_path / "output.json")
    output_content = json.loads((tmp_path / "output.json").read_text())
    assert output_content == expected_output


@pytest.mark.parametrize(
    ["exclude_children", "expected_children"],
    [
        (True, []),
        (
            False,
            [
                {"name": "Child1", "gender": "male", "dob": None},
                {"name": "Child2", "gender": "female", "dob": None},
            ],
        ),
    ],
)
def test_to_dict_method_of_person_with_exclude_children(
    sample_person: Person, exclude_children: bool, expected_children: list[dict] | None
):
    child1 = Person(name="Child1", gender=Gender.male)
    child2 = Person(name="Child2", gender=Gender.female)
    sample_person.add_children(child1, child2)

    person_dict = sample_person.to_dict(exclude_children=exclude_children)
    assert all(i in expected_children for i in person_dict.get("children", []))


@pytest.mark.parametrize(
    ["exclude_spouse", "expected_spouse"],
    [
        (True, None),
        (False, {"name": "Jane Doe", "gender": "female", "dob": None}),
    ],
)
def test_to_dict_method_of_person_with_exclude_spouse(
    sample_person: Person,
    exclude_spouse: bool,
    expected_spouse: dict | None,
):
    spouse = Person(name="Jane Doe", gender=Gender.female)
    sample_person.set_spouse(spouse)
    person_dict = sample_person.to_dict(exclude_spouse=exclude_spouse)
    assert person_dict.get("spouse") == expected_spouse
