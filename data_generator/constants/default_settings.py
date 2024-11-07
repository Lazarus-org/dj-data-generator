from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class DefaultCommandSettings:
    exclude_apps: List[str] = field(default_factory=lambda: [])
    exclude_models: List[str] = field(default_factory=lambda: [])
    custom_field_values: Dict[str, Dict] = field(default_factory=lambda: {})
