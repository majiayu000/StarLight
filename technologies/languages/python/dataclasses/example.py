from dataclasses import dataclass, field
import string
import random

def generate_id() -> str:
    return "".join(random.choices(string.ascii_uppercase, k=12))

@dataclass(frozen=False, slots=True)
class Person:
    # A old version usage
    # __slots__ = ["name", "address"] 
    
    name: str
    age: int = field()
    address: str
    active: bool = True
    email_address: list[str] = field(default_factory=list)
    id: str = field(init=False, default_factory=generate_id)
    _search_string: str = field(init=False, repr=False)
    
    def __post_init__(self) -> None:
        self._search_string = f"{self.name} {self.address}"
        if not isinstance(self.name, str):
            raise TypeError('Name should be of type str')

        if not isinstance(self.age, int):
            raise TypeError('Age should be of type int')

        if self.age < 0 or self.age > 150:
            raise ValueError('Age must be between 0 and 150')

json: dict = {
    "name": "bob",
    "age": -11,
    "address": "131 Main St"
}

def main() -> None:
    person = Person(name="JSON", age=115, address="123 Main St")
    print(person)
    
    # Here we can convert dict to property
    bob = Person(json["name"], 16, json["address"])
    print(bob.name)
    
    # A write-faster but unsafe unpacking method
    sam = Person(**json)
    print(sam)

if __name__ == "__main__":
    main()
    
