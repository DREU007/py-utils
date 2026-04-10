# Description

Commonly used python utils.

# Depends on `uv` package manager

# Installation

Include in uv `pyproject.toml` in `dependecies` and `[tool.uv.sources]`:

```
[project]
...
dependencies = [
    "py-utils",
]

[tool.uv.sources]
py-utils = { git = "https://github.com/dreu007/py-utils.git"}
```

In desired place specify class like object:
```python
# example.py

# Optional if python-dotenv is used
from dotenv import load_dotenv

load_dotenv()

class Config:
    ...
    name = APP_NAME
    tz = "Europe/Lisbon"
    chat_id = os.getenv("TG_CHAT_ID")
    message_thread_id = os.getenv("TG_MESSAGE_THREAD_ID")
```
