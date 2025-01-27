from core.processing_pipelines.base_pipeline import BasePipeline
from dotenv import load_dotenv
import datetime
import torch
from facenet_pytorch import MTCNN
from PIL import Image, ImageFilter

load_dotenv()


class BlurFacesPipeline(BasePipeline):

    def should_update(self, image, image_document, mongo_collection, valid_after_timestamp=None, *args, **kwargs) -> bool:
        blur_faces_metadata = image_document.get('metadata', {}).get('blur_faces_metadata', {})
        if valid_after_timestamp and blur_faces_metadata.get('blurred_at') < valid_after_timestamp:
            return True

        return not (blur_faces_metadata.get('is_blurred') is True)

    def process(self, image, image_document, mongo_collection, *args, **kwargs) -> tuple:
        current_time = datetime.datetime.now()

        self.blur_faces(image_path=image.filename, output_path=image.filename)

        mongo_collection.update_one({'_id': image_document.get('_id')}, {'$set': {
            'metadata.blur_faces_metadata': {
                'is_blurred': True,
                'blurred_at': current_time
            }
        }})
        # Re-fetch the updated document from MongoDB
        image_document = mongo_collection.find_one({'_id': image_document.get('_id')})

        return image, image_document

    def blur_faces(self, image_path, output_path):
        image = Image.open(image_path)

        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        mtcnn = MTCNN(keep_all=True, device=device)

        boxes, _ = mtcnn.detect(image)

        if boxes is not None:
            for box in boxes:
                xmin, ymin, xmax, ymax = [int(b) for b in box]
                face_region = image.crop((xmin, ymin, xmax, ymax))
                blurred_face = face_region.filter(ImageFilter.GaussianBlur(radius=15))
                image.paste(blurred_face, (xmin, ymin))

        image.save(output_path)
