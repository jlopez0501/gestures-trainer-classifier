import numpy as np
from tensorflow import keras

confidence = 0.9
class_names = ['front_raise', 'non_exersice', 'shoulder_press']
gesture_model_path = './weights.best.hdf5'
gesture_model = keras.models.load_model(gesture_model_path)

loaded_array = np.load('model_input.npy')
print(loaded_array.shape)
print(loaded_array[0])
print(loaded_array[np.newaxis, :, :].shape)
y_pred = gesture_model.predict(loaded_array[np.newaxis, :, :]) 

max_confidence_index = np.argmax(y_pred, axis=1)[0]  # index with max confidence
max_confidence_value = np.max(y_pred, axis=1)[0]  # max confidence
print(max_confidence_value)
# Check confidence threshold
if max_confidence_value > confidence:
    y_pred_label = class_names[max_confidence_index]
    print('GESTURE: ', y_pred_label)
