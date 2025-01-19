from dataclasses import dataclass
from core.models.step import Step


@dataclass
class Config:
    project_folder: str
    lsc_server_url: str
    topic_files: list[str]
    steps: list[Step]

    @staticmethod
    def from_json(json_data: dict, project_folder: str) -> "Config":
        steps = [Step.from_json(step) for step in json_data.get("steps", [])]
        return Config(**{
                **json_data,
                "steps": steps,
                "project_folder": project_folder
            }
        )