import argparse
import numpy as np
import torch
from facenet_pytorch import MTCNN
from PIL import Image, ImageFilter

# Funktion zum Laden eines Bildes
def load_image(image_path):
    return Image.open(image_path)

# Funktion zum Blurren der Gesichter im Bild
def blur_faces(image_path, output_path):
    # Bild laden
    image = load_image(image_path)

    # MTCNN zur Gesichtserkennung initialisieren
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    mtcnn = MTCNN(keep_all=True, device=device)

    # Gesichter erkennen
    boxes, _ = mtcnn.detect(image)

    # Prüfen, ob Gesichter erkannt wurden
    if boxes is not None:
        # Jedes erkannte Gesicht unscharf machen
        for box in boxes:
            # Box-Koordinaten extrahieren
            xmin, ymin, xmax, ymax = [int(b) for b in box]
            # Bereich des Gesichts extrahieren
            face_region = image.crop((xmin, ymin, xmax, ymax))
            # Gesicht unscharf machen
            blurred_face = face_region.filter(ImageFilter.GaussianBlur(radius=15))
            # Unscharfes Gesicht ins ursprüngliche Bild einsetzen
            image.paste(blurred_face, (xmin, ymin))

    image.save(output_path)

def main():
    parser = argparse.ArgumentParser(description='Blur faces in an image with adjustable sensitivity.')
    parser.add_argument('input_path', type=str, help='Path to the input image')
    parser.add_argument('output_path', type=str, help='Path to save the output image')
    parser.add_argument('--scale_factor', type=float, default=1.1, help='Scale factor for the face detection process')
    parser.add_argument('--min_neighbors', type=int, default=5, help='Minimum number of neighbors each rectangle should have to retain it')
    parser.add_argument('--min_size', type=int, default=30, help='Minimum size of the detected faces')

    args = parser.parse_args()

    blur_faces(args.input_path, args.output_path)

if __name__ == "__main__":
    main()
