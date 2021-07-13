# Oracle Cloud Infrastructure Data Science Demo Notebook
#
# Copyright (c) 2021 Oracle, Inc.<br>
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.


import numpy as np
from skimage import io 
from matplotlib import pyplot as plt
from seaborn import heatmap
from sklearn.metrics import confusion_matrix
import keras
import matplotlib.gridspec as gridspec
import glob
import pandas as pd
import os
from skimage import transform
import random


def create_df(dirpath):
    """
    """
    path_to_train_dataset = os.path.join(dirpath, "chest_xray", "train/")
    path_to_test_dataset = os.path.join(dirpath, "chest_xray", "test/")

    pneumonia_train_list = glob.glob(path_to_train_dataset + 'PNEUMONIA/*')
    normal_train_list = glob.glob(path_to_train_dataset + 'NORMAL/*')
    train_list = pneumonia_train_list + normal_train_list
    print("Training sample size = {}, Pneumonia = {}, Normal = {}".format(len(train_list),
                                                                          len(pneumonia_train_list),
                                                                          len(normal_train_list)))

    train_df = pd.DataFrame(data={"path": train_list})
    # Sampling - reduce memory requirements:
    train_df = train_df.sample(100, axis=0)

    # apply transformations
    train_df["class"] = train_df["path"].apply(lambda x: 0 if "/NORMAL/" in x else 1)
    train_df["extension"] = train_df["path"].apply(lambda x: os.path.splitext(x)[1])
    train_df["original_dims"] = train_df["path"].apply(lambda x: io.imread(x).shape)
    train_df['original_xsize'] = train_df["original_dims"].apply(lambda x: x[0])
    train_df['original_ysize'] = train_df["original_dims"].apply(lambda x: x[1])
    train_df['original_nchannels'] = train_df["original_dims"].apply(lambda x: x[2] if len(x) > 2 else 1)
    train_df['original_axis_ratio'] = train_df['original_ysize'] / train_df['original_xsize']

    train_df['resized_image'] = train_df['path'].apply(lambda x: transform.resize(io.imread(x),
                                                                                  output_shape=(200, 300)))

    # select a single channel:
    train_df['resized_image'] = train_df['resized_image'].apply(lambda x: x[:, :, 0] if len(x.shape) > 2 else x)

    # Recomputing the dimensions, xsize, ysize, and nchannels.
    train_df["dims"] = train_df.apply(lambda x: x['resized_image'].shape, axis=1)
    train_df['xsize'] = train_df["dims"].apply(lambda x: x[0])
    train_df['ysize'] = train_df["dims"].apply(lambda x: x[1])
    train_df['nchannels'] = train_df["dims"].apply(lambda x: x[2] if len(x) > 2 else 1)

    valid_fraction = 0.2
    train_df['valid'] = 0
    train_df['valid'] = train_df['valid'].apply(lambda x: random.random() <= valid_fraction)

    return train_df


def display_xray_image(xray_image): 
    """ utility function to display the x-ray image. 
    """
    if isinstance(xray_image, str):
        img1 = io.imread(xray_image)
        io.imshow(img1)
    elif isinstance(xray_image, np.ndarray): 
        img1 = xray_image
        io.imshow(img1)
    else: 
        raise TypeError("xray_image should be a path or a numpy array")


def display_rows_images(train_df2):
    """
    """

    nb_images = 8
    nbx = int(nb_images / 4)
    nby = 4
    fig = plt.figure(figsize=(16, 8))
    gs = gridspec.GridSpec(nbx, nby)
    gs.update(wspace=0.02, hspace=0.02)

    for i in range(nb_images):
        ax = plt.subplot(gs[i])
        plt.axis('on')
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_aspect('equal')
        ax.imshow(train_df2['resized_image'].iloc[i])
    plt.show()


def evaluate_model_performance(model_path, Xtest, Ytest, class_ids, labels=["normal", "pneumonia"]):
    """
    """
    print("- - - | For model {}".format(model_path))
    model = keras.models.load_model(model_path)
    loss, accuracy = model.evaluate(x=Xtest, y=Ytest)
    print("loss = {}, accuracy = {}".format(loss, accuracy))
    Ypred = model.predict_classes(Xtest)

    cm = confusion_matrix(class_ids, Ypred, labels=[0, 1])

    ax = heatmap(cm, annot=True, fmt='d',
                 linewidths=.2,
                 xticklabels=labels,
                 yticklabels=labels)

    ax.set(xlabel='predicted', ylabel='observed')