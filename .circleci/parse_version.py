from typing import Dict

import toml

config: Dict = toml.load("pyproject.toml")
print(config["tool"]["poetry"]["version"])
