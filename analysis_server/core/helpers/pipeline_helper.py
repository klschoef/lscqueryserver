from core.processing_pipelines.initial_pipeline import InitialPipeline
from core.processing_pipelines.open_clip_pipeline import OpenClipPipeline

pipelines = [
    InitialPipeline(),
    OpenClipPipeline()
]