import torch
import open_clip
from PIL import Image
import os
import glob
import csv
import argparse

def main():
    """
    Main function to process images, extract features using OpenCLIP, and save the results to a CSV file.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Extract image features using OpenCLIP.")
    parser.add_argument("input_folder", help="Path to the folder containing images.")
    parser.add_argument("output_prefix", help="Prefix for the output CSV file.")
    parser.add_argument("--model-name", default="ViT-H-14", help="Model name to use (default: 'ViT-H-14').")
    parser.add_argument("--model-weights", default="laion2b_s32b_b79k", help="Pretrained weights to use (default: 'laion2b_s32b_b79k').")
    parser.add_argument("--recursive", action="store_true", help="Recursively search for images in subdirectories.")
    args = parser.parse_args()

    # Set device: use CUDA if available, otherwise CPU
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"

    # Load the model and preprocessing pipeline
    print(f"Loading model '{args.model_name}' with weights '{args.model_weights}'...")
    model, _, preprocess = open_clip.create_model_and_transforms(
        args.model_name,
        pretrained=args.model_weights,
        device=device
    )

    # Create output CSV file
    output_file = f"{args.output_prefix}-{args.model_name}_{args.model_weights}.csv"
    print(f"Writing results to '{output_file}'...")
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        # Define the search pattern based on recursive option
        search_pattern = os.path.join(args.input_folder, '**', '*.jpg') if args.recursive else os.path.join(args.input_folder, '*.jpg')

        counter = 0

        # Iterate through all images in the specified folder
        for filename in glob.iglob(search_pattern, recursive=args.recursive):
            try:
                relpath = os.path.relpath(filename, args.input_folder)
                print(f"Processing: {relpath}")

                # Load and preprocess the image
                image = preprocess(Image.open(filename)).unsqueeze(0).to(device)

                # Encode image features
                with torch.no_grad():
                    image_features = model.encode_image(image).cpu().squeeze(0).tolist()

                # Write relative path and features to CSV
                writer.writerow([relpath] + image_features)
                counter += 1
                print(f"Processed {counter} images.")
            except Exception as e:
                print(f"Error processing '{filename}': {e}")

    print("Processing complete.")

if __name__ == "__main__":
    main()
