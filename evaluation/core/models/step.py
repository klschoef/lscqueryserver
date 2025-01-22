from dataclasses import dataclass
from typing import Optional

from core.models.faiss_step_config import FaissStepConfig
from core.models.solr_step_config import SolrStepConfig


@dataclass
class Step:
    type: str
    name: Optional[str] = None
    stop_if_no_results: bool = True
    prefix: Optional[str] = None
    postfix: Optional[str] = None
    faiss: Optional[FaissStepConfig] = None
    solr: Optional[SolrStepConfig] = None

    def __post_init__(self):
        if not self.name:
            if self.type == 'faiss':
                self.name = f"{self.prefix or ''}{self.faiss.model}_{self.faiss.weights}{self.postfix or ''}"
            elif self.type == 'solr':
                self.name = f"{self.prefix or ''}solr-{self.solr.core}{self.postfix or ''}"
            else:
                self.name = f"{self.prefix or ''}{self.type}{self.postfix or ''}"

    @staticmethod
    def from_json(json_data: dict) -> "Step":
        faiss_config = (
            FaissStepConfig.from_json(json_data["faiss"])
            if "faiss" in json_data and json_data["faiss"]
            else None
        )
        solr_config = (
            SolrStepConfig.from_json(json_data["solr"])
            if "solr" in json_data and json_data["solr"]
            else None
        )
        return Step(
            type=json_data["type"],
            name=json_data.get("name"),
            stop_if_no_results=json_data.get("stop_if_no_results", True),
            prefix=json_data.get("prefix"),
            postfix=json_data.get("postfix"),
            faiss=faiss_config,
            solr=solr_config
        )
