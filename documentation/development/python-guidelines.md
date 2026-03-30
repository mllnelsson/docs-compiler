---
description: This skill details the code style of the python applications. It should be referenced when developing python applications
---

Use this skill when writing or reviewing python code. These are guiding principles — code breaking these standards is generally not accepted.

## Design philosophy
Everything should do one thing and one thing well. This applies to modules, classes, and methods. If a method does too much, split it into multiple methods.

```python
# bad
def process_user(user):
    user.name = user.name.strip()
    db.save(user)
    send_email(user.email)

# good
def normalize_user(user): ...
def save_user(user): ...
def notify_user(user): ...
```

## General code style
Write in an imperative / C-like manner: prefer functions that manipulate data classes over stateful classes with methods. Avoid classes unless using abstractions or 3rd party integrations.

```python
# preferred
def calculate_total(order: Order) -> float:
    return sum(item.price for item in order.items)

# avoid (unless abstraction warrants it)
class OrderService:
    def calculate_total(self, order): ...
```

## Config
Use pydantic `BaseSettings` loaded from a `.env` file. Multiple `BaseSettings` classes are fine; avoid multiple `.env` files.

```python
from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    database_url: str
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env")

config = AppConfig()
```

## Data classes
Use pydantic `BaseModel` for data classes. Keep logic minimal — put mapping and construction in separate functions.

```python
class User(BaseModel):
    id: int
    name: str
    email: str

def user_from_row(row: dict) -> User:
    return User(**row)
```

## Type hints
Use modern type hint syntax.

```python
# good
def find(id: int) -> User | None: ...
def merge(a: str | bytes) -> str: ...

# avoid
from typing import Optional, Union
def find(id: int) -> Optional[User]: ...
```

## Modules
Group shared logic into modules. Use `__init__.py` to define the public API — only export what callers should use.

```
users/
  __init__.py      # exports: get_user, create_user
  _queries.py      # internal DB queries
  _models.py       # internal models
```

## Private methods
Prefix with `_` any function used only within a single file.

```python
def _parse_raw(data: bytes) -> dict: ...  # internal
def load_config(path: str) -> Config: ... # public
```

## Error handling
Define custom exception classes rather than raising generic exceptions. Group them in an `errors.py` module within the relevant package.

```python
# errors.py
class AppError(Exception): ...
class UserNotFoundError(AppError): ...
class InvalidCredentialsError(AppError): ...

# usage
def get_user(id: int) -> User:
    user = db.find(id)
    if not user:
        raise UserNotFoundError(f"User {id} not found")
    return user
```

Catch exceptions at boundaries (API handlers, CLI entry points), not deep in business logic.

## Static / module-level constants
Always use UPPER_CASE for constants.

```python
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30.0
```

## OOP
Avoid oop and introducing those patterns as much as possible. 


## Str-Enum and match
Instead of repeatingi if / else if statments you will use `match` and `case` syntax together with enums to create the business logic of an application

