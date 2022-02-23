import argparse
import os
import mimetypes
from Neuro_dop.utils.transforms import get_no_aug_transform
import torch
from Neuro_dop.models.generator import Generator
import numpy as np
import torchvision.transforms.functional as TF
from torchvision import transforms
import cv2
import subprocess
import tempfile
import re
from tqdm import tqdm
import time


def inv_normalize(img):
    # Adding 0.1 to all normalization values since the model is trained (erroneously) without correct de-normalization
    mean = torch.Tensor([0.485, 0.456, 0.406]).to(device)
    std = torch.Tensor([0.229, 0.224, 0.225]).to(device)

    img = img * std.view(1, 3, 1, 1) + mean.view(1, 3, 1, 1)
    img = img.clamp(0, 1)
    return img


def predict_images(image_list):
    trf = get_no_aug_transform()
    image_list = torch.from_numpy(np.array([trf(img).numpy() for img in image_list])).to(device)

    with torch.no_grad():
        generated_images = netG(image_list)
    generated_images = inv_normalize(generated_images)

    pil_images = []
    for i in range(generated_images.size()[0]):
        generated_image = generated_images[i].cpu()
        pil_images.append(TF.to_pil_image(generated_image))
    return pil_images


def main(img, batch_size=4, user_stated_device="cuda"):
    torch.cuda.empty_cache()
    global device
    device = torch.device(user_stated_device)
    pretrained_dir = "./Neuro_dop/checkpoints/trained_netG.pth"
    global netG
    netG = Generator().to(device)
    netG.eval()

    # Load weights
    if user_stated_device == "cuda":
        netG.load_state_dict(torch.load(pretrained_dir))
    else:
        netG.load_state_dict(torch.load(pretrained_dir, map_location=torch.device('cpu')))

    return np.asarray(predict_images([img])[0])


if __name__ == "__main__":
    input_path = "C:/PNGLIVE/test4.jpg"
    output_path = "C:/PNGLIVE"
    if mimetypes.guess_type(input_path)[0].startswith("image"):
        from PIL import Image
        image = Image.open(input_path).convert('RGB')
        predicted_image = main([image])
        predicted_image.save(output_path)
        cv2.imshow('image', image)
        cv2.imshow('predicted_image', predicted_image[0])
        cv2.waitKey(0)
        cv2.destroyAllWindows()
