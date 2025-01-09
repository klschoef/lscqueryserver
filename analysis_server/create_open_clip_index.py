import torch
from PIL import Image
import os
import glob
import argparse
from lsc_shared.clip.core.clip_context import ClipContext
from lsc_shared.clip.core.index_context import IndexContext
from lsc_shared.clip.core.helpers.faiss_helper import prepare_folder_and_files

def main():
    """
    Main function to process images, extract features using OpenCLIP, and save the results to a CSV file.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Extract image features using OpenCLIP.")
    parser.add_argument("input_folder", help="Path to the folder containing images.")
    parser.add_argument("faiss_folder", help="Path to faiss folder, which should be created")
    parser.add_argument("--model-name", default="ViT-H-14", help="Model name to use (default: 'ViT-H-14').")
    parser.add_argument("--model-weights", default="laion2b_s32b_b79k", help="Pretrained weights to use (default: 'laion2b_s32b_b79k').")
    args = parser.parse_args()

    clip_context = ClipContext(args.mode_name, args.model_weights)

    prepare_folder_and_files(args.faiss_folder)
    index_context = IndexContext(args.faiss_folder)

    print(f"Writing results to '{args.faiss_folder}'...")
    # Define the search pattern based on recursive option
    search_pattern = os.path.join(args.input_folder, '**', '*.jpg')

    counter = 0
    total_amount = 0
    print("Counting images...")
    for _ in glob.iglob(search_pattern, recursive=True):
        total_amount += 1

    # Iterate through all images in the specified folder
    for filename in glob.iglob(search_pattern, recursive=True):
        print(f"Processing: {filename}")
        try:
            relpath = os.path.relpath(filename, args.input_folder)
            print(f"Processing: {relpath}")

            # Load and preprocess the image
            image = clip_context.preprocess(Image.open(filename)).unsqueeze(0).to(clip_context.device)

            # Encode image features
            with torch.no_grad():
                image_features = clip_context.model.encode_image(image).cpu().numpy()
                index_context.add_new_entry(image_features, relpath)

            counter += 1
            print(f"Processed {counter}/{total_amount} images.")
        except Exception as e:
            print(f"Error processing '{filename}': {e}")

    print("Processing complete.")

if __name__ == "__main__":
    main()
