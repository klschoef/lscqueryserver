import torch
import pandas as pd
import argparse
from lsc_shared.clip.core.clip_context import ClipContext
from lsc_shared.clip.core.index_context import IndexContext
from lsc_shared.clip.core.helpers.faiss_helper import prepare_folder_and_files
from lsc_shared.clip.core.helpers.clip_helper import get_clip_features_from_text

def main():
    """
    Main function to process images, extract features using OpenCLIP, and save the results to a CSV file.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Extract description features using OpenCLIP.")
    parser.add_argument("description_file", help="Path to the description csv file (id,\"description\")")
    parser.add_argument("faiss_folder", help="Path to faiss folder, which should be created")
    parser.add_argument("--model-name", default="ViT-H-14", help="Model name to use (default: 'ViT-H-14').")
    parser.add_argument("--store-at-end", default="True", help="Store the index at the end (default: 'True').")
    parser.add_argument("--model-weights", default="laion2b_s32b_b79k", help="Pretrained weights to use (default: 'laion2b_s32b_b79k').")
    args = parser.parse_args()

    # Load descriptions from CSV
    df = pd.read_csv(args.description_file)
    print(f"Processing descriptions from '{args.description_file}'")

    total_amount = len(df)

    clip_context = ClipContext(args.model_name, args.model_weights)
    store_at_end = args.store_at_end.lower() in ['true', '1', 't', 'y', 'yes']

    index_context = None
    counter = 0

    # Iterate through all images in the specified folder
    with torch.no_grad():
        for _, row in df.iterrows():
            description = row['description']
            if pd.isna(description):
                continue  # Skip empty descriptions

            print(f"Processing description for ID: {row['id']}")

            # Convert text to features
            text_features = get_clip_features_from_text(description, clip_context).numpy()

            if index_context is None:
                print("Creating index...")
                prepare_folder_and_files(args.faiss_folder, text_features.shape[1])
                index_context = IndexContext(args.faiss_folder)

            index_context.add_new_entry(text_features, row['id'], store=not store_at_end)

            counter += 1
            print(f"Processed {counter}/{total_amount} descriptions.")

    print("Storing index...")
    if store_at_end:
        index_context.store_index()

    print("Processing complete.")

if __name__ == "__main__":
    main()
