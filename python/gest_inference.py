import numpy as np
from tensorflow import keras

confidence = 0.9
class_names = ['front_raise', 'non_exersice', 'shoulder_press']
gesture_model_path = 'weights.best.hdf5'
gesture_model = keras.models.load_model(gesture_model_path)

loaded_array = np.load('model_input.npy')

y_pred = gesture_model.predict(loaded_array[np.newaxis, :, :]) 

max_confidence_index = np.argmax(y_pred, axis=1)[0]  # index with max confidence
max_confidence_value = np.max(y_pred, axis=1)[0]  # max confidence
# Check confidence threshold
if max_confidence_value > confidence:
    y_pred_label = class_names[max_confidence_index]
    print('GESTURE: ', y_pred_label)
