from dataclasses import dataclass

@dataclass
class FaissStepConfig:
    path: str
    model: str
    weights: str

    @staticmethod
    def from_json(json_data: dict) -> "FaissStepConfig":
        return FaissStepConfig(**json_data)