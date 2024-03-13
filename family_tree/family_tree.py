from __future__ import annotations

import json
import uuid
from dataclasses import InitVar, asdict, dataclass, field
from datetime import date
from enum import StrEnum, auto
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from pathlib import Path


class Gender(StrEnum):
    male = auto()
    female = auto()


@dataclass(eq=False)
class Person:
    id: uuid.UUID = field(default_factory=uuid.uuid4, init=False, repr=False)
    name: str
    gender: Gender
    dob: date | None = field(default=None, repr=False)
    children: InitVar[set[Person] | None] = field(default=None, repr=False)
    spouse: InitVar[Person | None] = field(default=None, repr=False)

    def __post_init__(
        self,
        children: set[Person] | None,
        spouse: Person | None,
    ) -> None:
        self._children = children
        self._spouse = spouse

    def get_children(self) -> set[Person]:
        if self._children:
            return self._children
        raise ValueError(
            f"{self.name!r} has no children. Use `Person.add_children` method."
        )

    def has_children(self) -> bool:
        return self._children is not None

    def add_children(self, *child: Person) -> Self:
        if self._children is None:
            self._children = set(child)
        else:
            self._children.update(child)

        # Add children in spouse
        if self._spouse and self._children != self._spouse._children:
            self._spouse._children = self._children
        return self

    def set_spouse(self, spouse: Person) -> Self:
        if self._spouse:
            raise ValueError(f"Spouse of {self.name!r} is {self._spouse.name!r}.")
        self._spouse = spouse
        spouse._spouse = self  # Connecting both spouses
        spouse._children = self._children  # Assign children to spouse
        return self

    def get_spouse(self) -> Person:
        if self._spouse:
            return self._spouse
        raise ValueError(
            f"{self.name!r} has no spouse. Use `Person.set_spouse` method."
        )

    def has_spouse(self) -> bool:
        return self._spouse is not None

    def to_dict(
        self,
        *,
        exclude_children: bool = False,
        exclude_spouse: bool = False,
        exclude_id: bool = True,
    ) -> dict[str, Any]:
        data = asdict(self)
        if not exclude_spouse and self._spouse:
            data["spouse"] = self._spouse.to_dict(
                exclude_children=True,
                exclude_spouse=True,
            )
        if not exclude_children and self._children:
            data["children"] = [child.to_dict() for child in self._children]
        if exclude_id:
            del data["id"]
        return data


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, uuid.UUID | date):
            return str(o)
        return super().default(o)


@dataclass(eq=False)
class FamilyTree:
    name: str
    main_member: InitVar[Person] = field(repr=False)

    def __post_init__(self, main_member: Person) -> None:
        self._main_member = main_member

    def to_dict(self) -> dict[str, Any]:
        return self._main_member.to_dict()

    def write_json(self, filename: Path) -> None:
        filename.write_text(json.dumps(self.to_dict(), indent=2, cls=CustomEncoder))
