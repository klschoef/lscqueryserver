from dataclasses import dataclass
from typing import Optional

from core.models.faiss_step_config import FaissStepConfig


@dataclass
class Step:
    type: str
    name: Optional[str] = None
    prefix: Optional[str] = None
    postfix: Optional[str] = None
    faiss: Optional[FaissStepConfig] = None

    def __post_init__(self):
        if not self.name:
            if self.type == 'faiss':
                self.name = f"{self.prefix or ''}{self.faiss.model}_{self.faiss.weights}{self.postfix or ''}"
            else:
                self.name = f"{self.prefix or ''}{self.type}{self.postfix or ''}"

    @staticmethod
    def from_json(json_data: dict) -> "Step":
        faiss_config = (
            FaissStepConfig.from_json(json_data["faiss"])
            if "faiss" in json_data and json_data["faiss"]
            else None
        )
        return Step(
            type=json_data["type"],
            name=json_data.get("name"),
            prefix=json_data.get("prefix"),
            postfix=json_data.get("postfix"),
            faiss=faiss_config,
        )
