import logging
import torch
import open_clip

logging.basicConfig(level=logging.DEBUG)

class ClipContext:
    def __init__(self, model_name, weights_name):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"try to load model {model_name} with weights {weights_name} on device {self.device} ...")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(model_name, pretrained=weights_name, device=self.device)
        logging.info('model loaded')