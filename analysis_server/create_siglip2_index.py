import argparse
import glob
import os

import torch
from PIL import Image
from transformers import AutoModel, AutoProcessor

from lsc_shared.clip.core.helpers.faiss_helper import prepare_folder_and_files
from lsc_shared.clip.core.index_context import IndexContext


def build_parser():
    parser = argparse.ArgumentParser(description="Extract image features using SigLIP2.")
    parser.add_argument("input_folder", help="Path to the folder containing images.")
    parser.add_argument("faiss_folder", help="Path to faiss folder, which should be created")
    parser.add_argument(
        "--model-id",
        default="google/siglip2-base-patch16-224",
        help="Hugging Face model id for SigLIP2 (default: google/siglip2-base-patch16-224).",
    )
    parser.add_argument(
        "--store-at-end",
        default="True",
        help="Store the index at the end (default: 'True').",
    )
    parser.add_argument(
        "--recursive",
        default="True",
        help="Search recursively in input folder (default: 'True').",
    )
    return parser


def list_images(input_folder, recursive):
    patterns = ["*.jpg", "*.jpeg", "*.png", "*.webp"]
    files = []
    for pattern in patterns:
        search_pattern = os.path.join(input_folder, "**", pattern) if recursive else os.path.join(input_folder, pattern)
        files.extend(glob.glob(search_pattern, recursive=recursive))
    return sorted(files)


def _resolve_projection(model, kind="image"):
    projection_attr_candidates = (
        ["text_projection", "text_proj"] if kind == "text"
        else ["visual_projection", "vision_projection", "image_projection", "visual_proj", "vision_proj"]
    )
    for attr in projection_attr_candidates:
        proj = getattr(model, attr, None)
        if proj is not None:
            return proj
    return None


def _project_features(model, output_obj, kind="image"):
    if isinstance(output_obj, torch.Tensor):
        return output_obj

    embed_attr_candidates = (
        ["text_embeds", "embeds"] if kind == "text"
        else ["image_embeds", "embeds"]
    )
    for attr in embed_attr_candidates:
        embeds = getattr(output_obj, attr, None)
        if embeds is not None:
            return embeds

    pooled = getattr(output_obj, "pooler_output", None)
    if pooled is not None:
        projection = _resolve_projection(model, kind=kind)
        if projection is not None:
            if callable(projection):
                return projection(pooled)
            if isinstance(projection, torch.Tensor):
                return pooled @ projection
        return pooled

    if isinstance(output_obj, (tuple, list)) and len(output_obj) > 0:
        return output_obj[0]

    raise TypeError(f"Unsupported SigLIP2 {kind} feature output type: {type(output_obj)}")


def _extract_image_features(model, inputs):
    # Use image-only API so indexing doesn't require text tokens.
    image_features = model.get_image_features(**inputs)
    return _project_features(model, image_features, kind="image")


def main():
    args = build_parser().parse_args()
    store_at_end = args.store_at_end.lower() in ["true", "1", "t", "y", "yes"]
    recursive = args.recursive.lower() in ["true", "1", "t", "y", "yes"]

    image_paths = list_images(args.input_folder, recursive)
    if len(image_paths) == 0:
        print("No images found. Nothing to process.")
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading SigLIP2 model '{args.model_id}' on device '{device}' ...")
    processor = AutoProcessor.from_pretrained(args.model_id)
    model = AutoModel.from_pretrained(args.model_id).to(device)
    model.eval()

    print(f"Writing results to '{args.faiss_folder}' ...")
    index_context = None
    total_amount = len(image_paths)
    counter = 0

    with torch.no_grad():
        for filename in image_paths:
            try:
                relpath = os.path.relpath(filename, args.input_folder)
                print(f"Processing: {relpath}")
                image = Image.open(filename).convert("RGB")
                inputs = processor(images=image, return_tensors="pt")
                inputs = {k: v.to(device) for k, v in inputs.items()}

                image_features = _extract_image_features(model, inputs)
                image_features = torch.nn.functional.normalize(image_features, dim=-1)
                image_features = image_features.cpu().numpy()

                if index_context is None:
                    feature_size = image_features.shape[1]
                    print(f"Creating index... with size {feature_size}")
                    prepare_folder_and_files(args.faiss_folder, feature_size)
                    index_context = IndexContext(args.faiss_folder)

                index_context.add_new_entry(image_features, relpath, store=not store_at_end)

                counter += 1
                print(f"Processed {counter}/{total_amount} images.")
            except Exception as e:
                print(f"Error processing '{filename}': {e}")

    if store_at_end and index_context is not None:
        print("Storing index ...")
        index_context.store_index()

    print("Processing complete.")


if __name__ == "__main__":
    main()
