# Jobs Model Training Early Stopping by Metrics

## Introduction

Sometimes AI developers would prefer to stop the job model training on specific metric. For example, during the model training process, the developer may want to stop the model training by specific value of the loss function or when some level of accuracy is achieved. This could be done by implementing a the given framework callback. Following describes of how to achieve early stopping in `TF+Keras`. The technique is the same for other frameworks.

## Code Sample

Following is a generic example for early stopping using `TensorFlow` and `Keras`, notice the `EarlyStoppingByMetric` callback.

```python
import tensorflow as tf
import datetime
from keras.callbacks import Callback
 
mnist = tf.keras.datasets.mnist
 
(x_train, y_train),(x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0
 
def create_model():
  return tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(10, activation='softmax')
  ])
 
class EarlyStoppingByMetric(Callback):
    def __init__(self, monitor='val_loss', value=0.00001, verbose=0):
        super(Callback, self).__init__()
        self.monitor = monitor
        self.value = value
        self.verbose = verbose
 
    def on_epoch_end(self, epoch, logs={}):
        current = logs.get(self.monitor)
        if current is None:
            warnings.warn("Early stopping requires %s available!" % self.monitor, RuntimeWarning)
 
        if current < self.value:
            if self.verbose > 0:
                print("Epoch %05d: early stopping THR" % epoch)
            self.model.stop_training = True
             
             
             
model = create_model()
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
 
 model.fit(x=x_train,
          y=y_train,
          epochs=5,
          validation_data=(x_test, y_test),
          callbacks=[EarlyStoppingByMetric(monitor='loss', value=0.05, verbose=1)])
```

## Explanation

The code shown above is a standard TensorFlow/Keras getting started implementation using the MNIST dataset. Additionally in the code a custom callback function was introduced called `EarlyStoppingByMetric` that monitors the metric in question on epoch end and if the model training should be stopped when specific value of the metric is achieved.

## Job Ready

We do not need to change the code to work with the Job service, however if we want to make the implementation more dynamic and control what metrics to monitor and on what value of the metric to exit the job, we could add environment variables that we pass on JobRun. To achieve this, we would do the following:

- add env. variables for the metric name, value and comparison rule
  - `METRIC_NAME` - metric name that should be monitored
  - `METRIC_STOP_VALUE` - the metric float value to be use to compare
  - `METRIC_STOP_RULE_KEY` - comparison rule: lower, equal or greater

    ```python
    METRIC_NAME_KEY = "METRIC_NAME"
    METRIC_STOP_VALUE_KEY = "METRIC_STOP_VALUE"
    METRIC_STOP_RULE_KEY = "METRIC_STOP_RULE"
    
    METRIC_NAME = os.environ.get(METRIC_NAME_KEY, "val_loss")
    METRIC_STOP_VALUE = float(os.environ.get(METRIC_STOP_VALUE_KEY, 0.00001))
    METRIC_STOP_RULE = os.environ.get(METRIC_STOP_RULE_KEY, "LOWER")
    ```

- incorporate those variables in the code, see the `EarlyStoppingByMetric` in the full code sample below
- run jobs and pass those variables to control on which metric and value the model training should stop

`Full code sample` -> `tf-early-stopping.py`

```python
import warnings
import os
import tensorflow as tf
from keras.callbacks import Callback

print("starting ...")
METRIC_NAME_KEY = "METRIC_NAME"
METRIC_STOP_VALUE_KEY = "METRIC_STOP_VALUE"
METRIC_STOP_RULE_KEY = "METRIC_STOP_RULE"

METRIC_NAME = os.environ.get(METRIC_NAME_KEY, "val_loss")
METRIC_STOP_VALUE = float(os.environ.get(METRIC_STOP_VALUE_KEY, 0.00001))
METRIC_STOP_RULE = os.environ.get(METRIC_STOP_RULE_KEY, "LOWER")

print(f'METRIC_NAME: {METRIC_NAME}')
print(f'METRIC_STOP_VALUE: {METRIC_STOP_VALUE}')
print(f'METRIC_STOP_RULE: {METRIC_STOP_RULE}')

mnist = tf.keras.datasets.mnist

(x_train, y_train), (x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255.0, x_test / 255.0


def create_model():
    return tf.keras.models.Sequential(
        [
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(512, activation="relu"),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(10, activation="softmax"),
        ]
    )


class EarlyStoppingByMetric(Callback):
    def __init__(self, monitor="val_loss", value=0.00001, verbose=0):
        super(Callback, self).__init__()
        self.monitor = monitor
        self.value = value
        self.verbose = verbose

    def stopping(self, epoch):
        if self.verbose > 0:
            print("\nEpoch %05d: early stopping, achieved in epoch: " % self.value)
            print(epoch)
        self.model.stop_training = True

    def lower(self, current, epoch):
        if current < self.value:
            self.stopping(epoch=epoch)

    def equal(self, current, epoch):
        if current == self.value:
            self.stopping(epoch=epoch)

    def greater(self, current, epoch):
        if current > self.value:
            self.stopping(epoch=epoch)

    # options = {"LOWER": lower, "EQUAL": equal, "GREATER": greater}

    def on_epoch_end(self, epoch, logs={}):
        current = logs.get(self.monitor)
        if current is None:
            warnings.warn(
                "Early stopping requires %s available!" % self.monitor, RuntimeWarning
            )

        # self.options[METRIC_STOP_RULE](current, epoch)
        if METRIC_STOP_RULE.lower() == "lower":
            self.lower(current, epoch)
        elif METRIC_STOP_RULE.lower() == "equal":
            self.equal(current, epoch)
        elif METRIC_STOP_RULE.lower() == "greater":
            self.greater(current, epoch)
        else:
            print("\n Unable to identify stop rule metric METRIC_STOP_RULE")
            self.model.stop_training = True


print("create model")
model = create_model()

print("compile")
model.compile(
    optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
)

print("add the EarlyStoppingByMetric")
early_stop_callback = EarlyStoppingByMetric(
    monitor=METRIC_NAME, value=METRIC_STOP_VALUE, verbose=1
)

print("fit")
model.fit(
    x=x_train,
    y=y_train,
    epochs=10,
    validation_data=(x_test, y_test),
    callbacks=[early_stop_callback],
)
```

## Local or Notebooks Test

`You can test this example by using our Oracle Cloud Infrastructure Data Science Notebooks with the` **tensorflow28_p38_cpu_v1** `activated!`. For a local test make sure you either install and use TensorFlow locally, via Conda or using our ADS OPCTL for local job runs: <https://accelerated-data-science.readthedocs.io/en/latest/user_guide/cli/opctl/localdev/local_jobs.html>

**Stop** on **loss** function `0.05`

Export following env. variables in your terminal

```bash
export METRIC_STOP_VALUE=0.05
export METRIC_NAME="loss"
export METRIC_STOP_RULE="LOWER"
```

Run the code in your terminal, **make sure* you've `setup` for example `conda environment` with `TensorFlow`!

```bash
python tf-early-stopping.py
start
create model
2022-04-22 14:41:10.551562: I tensorflow/core/platform/cpu_feature_guard.cc:151] This TensorFlow binary is optimized with oneAPI Deep Neural Network Library (oneDNN) to use the following CPU instructions in performance-critical operations:  AVX2 FMA
To enable them in other operations, rebuild TensorFlow with the appropriate compiler flags.
compile
callbacks
fit
Epoch 1/10
1875/1875 [==============================] - 5s 3ms/step - loss: 0.2203 - accuracy: 0.9359 - val_loss: 0.1068 - val_accuracy: 0.9676
Epoch 2/10
1875/1875 [==============================] - 5s 3ms/step - loss: 0.0973 - accuracy: 0.9692 - val_loss: 0.0746 - val_accuracy: 0.9770
Epoch 3/10
1875/1875 [==============================] - 5s 3ms/step - loss: 0.0683 - accuracy: 0.9785 - val_loss: 0.0709 - val_accuracy: 0.9773
Epoch 4/10
1875/1875 [==============================] - 5s 3ms/step - loss: 0.0538 - accuracy: 0.9831 - val_loss: 0.0667 - val_accuracy: 0.9785
Epoch 5/10
1857/1875 [============================>.] - ETA: 0s - loss: 0.0435 - accuracy: 0.9859
Epoch 00000: early stopping, achieved epoch value:
4
1875/1875 [==============================] - 6s 3ms/step - loss: 0.0436 - accuracy: 0.9859 - val_loss: 0.0617 - val_accuracy: 0.9801
```

**Stop** on **accuracy** function `0.97`

Set the new values in your terminal

```bash
export METRIC_STOP_VALUE=0.97
export METRIC_NAME="accuracy"
export METRIC_STOP_RULE="GREATER"
```

Run again the example

```bash
python tf-early-stopping.py
start
create model
2022-04-22 15:06:09.637962: I tensorflow/core/platform/cpu_feature_guard.cc:151] This TensorFlow binary is optimized with oneAPI Deep Neural Network Library (oneDNN) to use the following CPU instructions in performance-critical operations:  AVX2 FMA
To enable them in other operations, rebuild TensorFlow with the appropriate compiler flags.
compile
callbacks
fit
Epoch 1/10
1875/1875 [==============================] - 5s 3ms/step - loss: 0.2213 - accuracy: 0.9341 - val_loss: 0.0991 - val_accuracy: 0.9700
Epoch 2/10
1875/1875 [==============================] - 5s 2ms/step - loss: 0.0981 - accuracy: 0.9696 - val_loss: 0.0797 - val_accuracy: 0.9750
Epoch 3/10
1874/1875 [============================>.] - ETA: 0s - loss: 0.0685 - accuracy: 0.9781
Epoch 00000: early stopping, achieved in epoch:
2
1875/1875 [==============================] - 4s 2ms/step - loss: 0.0685 - accuracy: 0.9781 - val_loss: 0.0710 - val_accuracy: 0.9793
```

## Job Test

We would use following job environment variables:

`METRIC_STOP_VALUE=0.97`
`METRIC_NAME=accuracy`
`METRIC_STOP_RULE=GREATER`

`For the job test we would need additionally a Conda Environment that has TensorFlow and Keras installed. If you use BYOC, make sure you have TF and Keras installed in your container image.`

In our case we would use one of the pre-configured OCI Data Science Service Conda Environments, which can be set with the following environment variables on the job:

`CONDA_ENV_TYPE=service`
`CONDA_ENV_SLUG=tensorflow28_p38_cpu_v1`
