import argparse

import torch
import open_clip
from PIL import Image
import os
import glob
import csv
import logging
logging.basicConfig(level=logging.DEBUG)
import psutil
memory = psutil.virtual_memory()
logging.info(f"Available Memory: {memory.available / (1024 ** 3):.2f} GB")

parser = argparse.ArgumentParser(description='Extract open_clip image features to a csv file out of a given folder with images.')
parser.add_argument('rootdir', help='Folder with images.')
parser.add_argument('file_name', help='Filename without suffix. ("openclip-{args.file_name}-{args.model_name}_{args.pretrained_name}.csv")')
parser.add_argument('--model_name', default="ViT-H-14", help='Model name like "ViT-H-14"')
parser.add_argument('--pretrained_name', default="laion2b_s32b_b79k", help='Pretrained model name like "laion2b_s32b_b79k"')
parser.add_argument('--image_suffix', default="jpg", help='Image suffix like "jpg" or "png"')
args = parser.parse_args()

rootdir = args.rootdir
modelname = args.model_name
modelweights = args.pretrained_name
device = "cuda" if torch.cuda.is_available() else "cpu"

logging.info(f"create model ... ({modelname}, {modelweights}) with {device} ...")

try:
    model, _, preprocess = open_clip.create_model_and_transforms(modelname, pretrained=modelweights, device=device)
except Exception as e:
    logging.info(f"Loading Model Error: {e}")
    exit(1)

logging.info(f"open csv writer ...")
csvfile = open(f'openclip-lsc-{args.file_name}-{modelname}_{modelweights}.csv', 'w')
writer = csv.writer(csvfile, delimiter=',')

image_suffix = args.image_suffix

logging.info(f"iterate through filenames ...")
for filename in glob.iglob(rootdir + f'**/**/*.{image_suffix}', recursive=True):
    basename = os.path.basename(filename)
    relpath = os.path.relpath(filename, rootdir)
    logging.info(filename)

    image = preprocess(Image.open(filename)).unsqueeze(0).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image)
        image_features = image_features.cpu()
        mylist = image_features[0].tolist()
        mylist.insert(0, relpath)
        writer.writerow(mylist)

        logging.info(relpath)

csvfile.close()
