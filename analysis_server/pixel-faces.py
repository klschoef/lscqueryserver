import cv2
import argparse

def blur_faces(image_path, output_path, scale_factor=1.1, min_neighbors=5, min_size=30):
    # Load the image
    image = cv2.imread(image_path)

    # Load the pre-trained face detection model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Convert the image to grayscale (needed for face detection)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=scale_factor, minNeighbors=min_neighbors, minSize=(min_size, min_size), flags=cv2.CASCADE_SCALE_IMAGE)

    # Blur each face found
    for (x, y, w, h) in faces:
        face_roi = image[y:y+h, x:x+w]
        blurred_face = cv2.GaussianBlur(face_roi, (99, 99), 30)
        image[y:y+h, x:x+w] = blurred_face

    # Save the result
    cv2.imwrite(output_path, image)
    print(f"Blurred image saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Blur faces in an image with adjustable sensitivity.')
    parser.add_argument('input_path', type=str, help='Path to the input image')
    parser.add_argument('output_path', type=str, help='Path to save the output image')
    parser.add_argument('--scale_factor', type=float, default=1.1, help='Scale factor for the face detection process')
    parser.add_argument('--min_neighbors', type=int, default=5, help='Minimum number of neighbors each rectangle should have to retain it')
    parser.add_argument('--min_size', type=int, default=30, help='Minimum size of the detected faces')

    args = parser.parse_args()

    blur_faces(args.input_path, args.output_path, args.scale_factor, args.min_neighbors, args.min_size)

if __name__ == "__main__":
    main()
