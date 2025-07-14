from dataclasses import dataclass

@dataclass
class ModernPerson:
    name: str  # You define your data fields with type hints
    age: int
    email: str = "no-email@example.com" # You can even add default values!
