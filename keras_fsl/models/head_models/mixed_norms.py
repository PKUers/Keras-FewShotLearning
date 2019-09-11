import tensorflow as tf
from tensorflow.python.keras.layers import Input, Concatenate, Lambda, Reshape, Flatten, Conv2D, Dense
from tensorflow.python.keras.models import Model


def MixedNorms(input_shape, norms=None):
    """
    Head inspired by
    [this kaggle notebook](https://www.kaggle.com/martinpiotte/whale-recognition-model-with-score-0-78563)
    on whale identification

    Args:
        input_shape (tuple): arg to be passed to keras.layer.Input
        norms (List[function]): list of function to be applied to the list of tensors [query, support] in a Lambda layer
    """
    if norms is None:
        norms = [
            lambda x: x[0] * x[1],
            lambda x: x[0] + x[1],
            lambda x: tf.math.abs(x[0] - x[1]),
            lambda x: tf.math.square(x[0] - x[1])
        ]

    query = Input(input_shape)
    support = Input(input_shape)
    prediction = Concatenate()([Lambda(norm)([query, support]) for norm in norms])
    prediction = Reshape((len(norms), input_shape[0], 1), name='reshape1')(prediction)

    # Per feature NN with shared weight is implemented using CONV2D with appropriate stride.
    prediction = Conv2D(32, (len(norms), 1), activation='relu', padding='valid')(prediction)
    prediction = Reshape((input_shape[0], 32, 1))(prediction)
    prediction = Conv2D(1, (1, 32), activation='linear', padding='valid')(prediction)
    prediction = Flatten(name='flatten')(prediction)

    # Weighted sum implemented as a Dense layer.
    prediction = Dense(1, use_bias=True, activation='sigmoid', name='weighted-average')(prediction)
    return Model(inputs=[query, support], outputs=prediction)