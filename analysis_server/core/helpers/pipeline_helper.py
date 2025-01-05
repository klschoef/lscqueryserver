from core.processing_pipelines.blip2_pipeline import Blip2Pipeline
from core.processing_pipelines.blip_pipeline import BlipPipeline
from core.processing_pipelines.initial_pipeline import InitialPipeline
from core.processing_pipelines.open_clip_pipeline import OpenClipPipeline

pipelines = [
    InitialPipeline(),
    OpenClipPipeline(),
    #BlipPipeline(),
    #Blip2Pipeline()
]