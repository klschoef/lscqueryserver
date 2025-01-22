from dataclasses import dataclass

@dataclass
class SolrStepConfig:
    core: str

    @staticmethod
    def from_json(json_data: dict) -> "SolrStepConfig":
        return SolrStepConfig(**json_data)