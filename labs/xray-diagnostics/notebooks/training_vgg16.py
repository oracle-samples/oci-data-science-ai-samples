import os 
import ocifs
from ocifs import OCIFileSystem
from zipfile import ZipFile 
import random
import shutil
from ads.dataset.factory import DatasetFactory

import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt

fs = OCIFileSystem()

# Creating the local directory 
dirpath = f"./data/"
if not os.path.exists(dirpath):
    os.makedirs(dirpath)

# Downloading the data from Object Storage using OCIFS (https://github.com/oracle/ocifs)
if os.path.exists(os.path.join(dirpath, "chest_xrays.zip")):
    with ZipFile(os.path.join(dirpath, "chest_xrays.zip"), 'r') as zipf:
        zipf.extractall(dirpath)
else:
    fs.download('oci://hosted-ds-datasets@bigdatadatasciencelarge/chest-xrays/ChestXRay2017.zip',os.path.join(dirpath, "chest_xrays.zip"))
    with ZipFile(os.path.join(dirpath, "chest_xrays.zip"), 'r') as zipf:
        zipf.extractall(dirpath)
        
train_dir = "./data/chest_xray/train/"
test_dir = "./data/chest_xray/test/"
valid_dir = f"./data/chest_xray/validation/"
if not os.path.exists(valid_dir):
    os.makedirs(valid_dir)
    
normal_train = "./data/chest_xray/train/NORMAL/"
pneumonia_train = "./data/chest_xray/train/PNEUMONIA/"

normal_images = os.listdir(normal_train)
pneumonia_images = os.listdir(pneumonia_train)

valid_dir_normal = os.path.join(valid_dir,"NORMAL")
if not os.path.exists(valid_dir_normal):
    os.makedirs(valid_dir_normal)

valid_dir_pneumonia = os.path.join(valid_dir,"PNEUMONIA")
if not os.path.exists(valid_dir_pneumonia):
    os.makedirs(valid_dir_pneumonia) 
        
# validation sample:     
nb_validation_normal = 8 
nb_validation_pneumonia = 8 

validation_normal_files = random.sample(normal_images, k=nb_validation_normal)
validation_pneumonia_files = random.sample(pneumonia_images, k=nb_validation_pneumonia) 

for x in validation_normal_files: 
    shutil.move(os.path.join(normal_train,x),os.path.join(valid_dir_normal,x))

for x in validation_pneumonia_files: 
    shutil.move(os.path.join(pneumonia_train,x),os.path.join(valid_dir_pneumonia,x))
    
f_pneumonia_training = len(os.listdir(pneumonia_train)) / (len(os.listdir(pneumonia_train)) + len(os.listdir(normal_train)))
f_normal_training = 1.0 - f_pneumonia_training
print(f'fraction pneumonia in training dataset : {f_pneumonia_training}')
print(f'fraction normal in training dataset : {f_normal_training}')

from keras.preprocessing.image import ImageDataGenerator

image_generator = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.1,
    samplewise_center=True,
    samplewise_std_normalization=True
)

train = image_generator.flow_from_directory(train_dir, 
                                            batch_size=8, 
                                            shuffle=True, 
                                            class_mode='binary',
                                            target_size=(180, 180))

validation = image_generator.flow_from_directory(valid_dir, 
                                                batch_size=1, 
                                                shuffle=False, 
                                                class_mode='binary',
                                                target_size=(180, 180))


test = image_generator.flow_from_directory(test_dir, 
                                            batch_size=1, 
                                            shuffle=False, 
                                            class_mode='binary',
                                            target_size=(180, 180))


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.applications import VGG16, InceptionV3
from tensorflow.keras.layers import Dense, Conv2D, MaxPool2D, Dropout, Flatten, BatchNormalization
from tensorflow.keras.metrics import Accuracy, Precision, Recall
from tensorflow.keras.optimizers import Adam

vgg16_base_model = VGG16(input_shape=(180,180,3),
                         include_top=False, 
                         weights='imagenet')

vgg16_model = Sequential([
        vgg16_base_model,
        GlobalAveragePooling2D(),
        Dense(512, activation="relu"),
        BatchNormalization(),
        Dropout(0.6),
        Dense(128, activation="relu"),
        BatchNormalization(),
        Dropout(0.4),
        Dense(64,activation="relu"),
        BatchNormalization(),
        Dropout(0.3),
        Dense(1,activation="sigmoid")
    ])


optimizer = Adam(learning_rate=0.001)
METRICS = ['accuracy', 
           Precision(name='precision'),
           Recall(name='recall')]

vgg16_model.compile(optimizer=optimizer,
                    loss='binary_crossentropy',
                    metrics=METRICS)

class_weight = {0: f_pneumonia_training, 1: f_normal_training}

r = vgg16_model.fit(train,
          epochs=10,
          validation_data=validation,
          class_weight=class_weight,
          steps_per_epoch=100,
          validation_steps=25)

evaluation =vgg16_model.evaluate(test)
print(f"Test Accuracy: {evaluation[1] * 100:.2f}%")

evaluation = vgg16_model.evaluate(train)
print(f"Train Accuracy: {evaluation[1] * 100:.2f}%")

vgg16_model.save("./vgg16.tf",save_format='tf')

print('uploading model to object storage')

fs.upload("./vgg16.tf", "oci://ds-models@bigdatadatasciencelarge/vgg16.tf", recursive=True)

print('uploaded the model to object storage')