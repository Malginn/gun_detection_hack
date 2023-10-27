import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

import tensorflow.keras.applications as app
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications.resnet import preprocess_input
from keras.models import load_model

from pathlib import Path



IMG_HEIGHT, IMG_WIDTH = 600, 1000
image_path = Path('../uploads')

prod_gen_train = ImageDataGenerator(preprocessing_function=preprocess_input) 
prod_flow = prod_gen_train.flow_from_directory(
    batch_size=1,
    directory=image_path,
    shuffle=False,
    target_size=(IMG_HEIGHT, IMG_WIDTH),
    class_mode='sparse',
    )


# class RegressorMP4:
#     def __init__(self):
#         self.IMG_SHAPE = train_flow.image_shape
#         self.base_model = app.ResNet50(input_shape=self.IMG_SHAPE, include_top=False)

#     def extra_layers(self):
#         self.model = tf.keras.Sequential([
#             self.base_model,

#             tf.keras.layers.Dense(1)
#         ])
#         self.model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(), optimizer='Adam')


# reg = RegressorMP4()
# reg.extra_layers()



model = load_model('./resnet50-score10.11.hdf5')
pred = model.predict(prod_flow)