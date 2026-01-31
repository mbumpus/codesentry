# Test file for CS002 - Legitimate stub patterns that should NOT trigger CS002
# These are valid Python patterns, not placeholder code

from abc import ABC, abstractmethod
from typing import Protocol, overload


# === ABSTRACT METHODS (should NOT trigger) ===

class Animal(ABC):
    @abstractmethod
    def speak(self) -> str:
        """Animals must implement speak."""
        pass  # OK - abstractmethod requires empty body
    
    @abstractmethod
    def move(self) -> None:
        ...  # OK - ellipsis is idiomatic for abstract methods


class Vehicle(ABC):
    @property
    @abstractmethod
    def wheels(self) -> int:
        """Number of wheels."""
        ...  # OK - abstract property
    
    @staticmethod
    @abstractmethod
    def fuel_type() -> str:
        pass  # OK - abstract staticmethod
    
    @classmethod
    @abstractmethod
    def create(cls, config: dict) -> "Vehicle":
        ...  # OK - abstract classmethod


# === PROTOCOLS (should NOT trigger) ===

class Readable(Protocol):
    def read(self, size: int = -1) -> bytes:
        ...  # OK - Protocol stubs are structural typing hints


class Writable(Protocol):
    def write(self, data: bytes) -> int:
        ...  # OK


class SupportsClose(Protocol):
    def close(self) -> None:
        pass  # OK - Protocol method stub


# === OVERLOADS (should NOT trigger) ===

@overload
def process(data: str) -> str: ...  # OK - overload type stub

@overload
def process(data: bytes) -> bytes: ...  # OK

@overload
def process(data: int) -> int: ...  # OK

def process(data):
    """Actual implementation."""
    if isinstance(data, str):
        return data.upper()
    elif isinstance(data, bytes):
        return data.upper()
    else:
        return data * 2


@overload
def get_value(key: str, default: None = None) -> str | None: ...

@overload  
def get_value(key: str, default: str) -> str: ...

def get_value(key, default=None):
    return _store.get(key, default)


# === MIXED PATTERNS (should NOT trigger) ===

class FileHandler(ABC):
    @abstractmethod
    def open(self, path: str) -> None:
        """Open a file."""
        pass
    
    @abstractmethod
    def read(self) -> bytes:
        ...
    
    @abstractmethod
    def close(self) -> None:
        pass


class Serializable(Protocol):
    def to_json(self) -> str:
        ...
    
    def from_json(self, data: str) -> "Serializable":
        ...
