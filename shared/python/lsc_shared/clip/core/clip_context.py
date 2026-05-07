import logging
import torch
import open_clip
from transformers import AutoModel, AutoProcessor
from lsc_shared.clip.core.helpers.siglip_helper import project_siglip_features

logging.basicConfig(level=logging.DEBUG)

class ClipContext:
    def __init__(self, model_name, weights_name):
        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        logging.info(f"try to load model {model_name} with weights {weights_name} on device {self.device} ...")
        self.model_name = model_name
        self.weights_name = weights_name
        self.is_siglip2 = "siglip2" in (model_name or "").lower()

        if self.is_siglip2:
            self.model = AutoModel.from_pretrained(model_name).to(self.device)
            self.model.eval()
            self.processor = AutoProcessor.from_pretrained(model_name)
            self.preprocess = None
            self.tokenizer = None
        else:
            self.model, _, self.preprocess = open_clip.create_model_and_transforms(model_name, pretrained=weights_name, device=self.device)
            self.tokenizer = open_clip.get_tokenizer(model_name)
            self.processor = None

        self.model_name = model_name
        self.weights_name = weights_name
        logging.info('model loaded')

    def _extract_siglip_text_features(self, inputs):
        # Use text-only API so we don't require image inputs.
        text_features = self.model.get_text_features(**inputs)
        return project_siglip_features(self.model, text_features, kind="text")

    def _extract_siglip_image_features(self, inputs):
        # Use image-only API so we don't require text inputs.
        image_features = self.model.get_image_features(**inputs)
        return project_siglip_features(self.model, image_features, kind="image")

    def encode_text_query(self, query):
        with torch.no_grad():
            if self.is_siglip2:
                inputs = self.processor(
                    text=[query],
                    return_tensors="pt",
                    padding="max_length",
                    truncation=True,
                    max_length=64,
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                text_features = self._extract_siglip_text_features(inputs)
                text_features = text_features.float()
                return torch.nn.functional.normalize(text_features, dim=-1).cpu()
            else:
                input_tokens = self.tokenizer(query).to(self.device)
                text_features = self.model.encode_text(input_tokens)
                return text_features.cpu()

    def encode_image_from_pil(self, image):
        with torch.no_grad():
            if self.is_siglip2:
                inputs = self.processor(images=image.convert("RGB"), return_tensors="pt")
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                image_features = self._extract_siglip_image_features(inputs)
                image_features = image_features.float()
                return torch.nn.functional.normalize(image_features, dim=-1).cpu()
            else:
                image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
                image_features = self.model.encode_image(image_tensor)
                return image_features.cpu()
