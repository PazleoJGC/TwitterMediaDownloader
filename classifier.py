import numpy as np
import math
import tensorflow as tf
from PIL import Image
import os

class Classifier:
    tags = []
    model : tf.keras.Model = None

    def __init__(self, model_path_dir : str = None, allow_GPU = False):
        if not allow_GPU:
            os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        if model_path_dir == None:
            model_path_dir = f"{os.path.dirname(__file__)}/downloads"

        if not os.path.exists(f"{model_path_dir}/tags.txt") or not os.path.exists(f"{model_path_dir}/model-resnet_custom_v3.h5"):
            raise Exception(f"Please download and extract the trained model and tag list from https://github.com/KichangKim/DeepDanbooru/releases/tag/v3-20211112-sgd-e28 to {model_path_dir}")
        with open(f"{model_path_dir}/tags.txt", "rt") as file:
            self.tags = file.read().splitlines()
        self.model = tf.keras.models.load_model(f"{model_path_dir}/model-resnet_custom_v3.h5")

    def classify(self, imagePath : str):
        width = self.model.input_shape[2]
        height = self.model.input_shape[1]
        dtype = self.model.dtype

        img = self.resize_image(Image.open(imagePath), width, height).convert("RGB")
        image = np.asarray(img, dtype=dtype) / 255
        image_shape = image.shape
        image = image.reshape((1, image_shape[0], image_shape[1], image_shape[2]))

        output_data = self.model.predict(image, verbose=0)[0]
        results_ordered = np.flip(np.argsort(output_data))
        output = {}
        for result in results_ordered:
            output[self.tags[result]] = output_data[result]
        return output

    def classify_threshold(self, imagePath, threshold = 0.6):
        data = self.classify(imagePath)
        output = self.filterThreshold(data, threshold)
        return output

    def classify_tagList(self, imagePath, tagList):
        data = self.classify(imagePath)
        output = self.filterTagList(data, tagList)
        return output

    def filterThreshold(self, data : dict, threshold = 0.6):
        output = {}
        for result in data.keys():
            if data[result] > threshold:
                output[result] = data[result]
        return output

    def filterCount(self, data : dict, count = 20):
        output = {}
        for idx, result in enumerate(data.keys()):
            if idx < count:
                output[result] = data[result]
            else:
                break
        return output

    def filterTagList(self, data : dict, tagList : list):
        output = {}
        for result in data.keys():
            if result in tagList:
                output[result] = data[result]
        return output

    def resize_image(self, image, width, height):
        new_size = (width, height)
        if image.size[0] > image.size[1]:
            wpercent = (new_size[0] / float(image.size[0]))
            hsize = int((float(image.size[1]) * wpercent))
            image = image.resize((new_size[0], hsize), Image.NEAREST )
        else:
            hpercent = (new_size[1] / float(image.size[1]))
            wsize = int((float(image.size[0]) * hpercent))
            image = image.resize((wsize, new_size[1]), Image.NEAREST )

        x1 = int(math.floor((new_size[0] - image.size[0]) / 2))
        y1 = int(math.floor((new_size[1] - image.size[1]) / 2))

        new_image = Image.new("RGBA", new_size, "WHITE")
        new_image.paste(image, (x1, y1, x1 + image.size[0], y1 + image.size[1]))
        return new_image
