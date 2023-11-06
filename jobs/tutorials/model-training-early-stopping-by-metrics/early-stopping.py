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

print(f"METRIC_NAME: {METRIC_NAME}")
print(f"METRIC_STOP_VALUE: {METRIC_STOP_VALUE}")
print(f"METRIC_STOP_RULE: {METRIC_STOP_RULE}")

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
