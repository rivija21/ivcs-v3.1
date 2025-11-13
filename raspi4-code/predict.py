import sys
import os
import time  #for the FAKE prediction.
import random 

# This prevents log messages from being mixed with your output
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import preprocess_input

USE_FAKE_MODEL = False

MODEL_PATH = './inceptionv3_finalised.h5' 
model = tf.keras.models.load_model(MODEL_PATH)


CLASS_NAMES = ['car_crash', 'normal_road', 'road_maintenance']
IMAGE_WIDTH = 299
IMAGE_HEIGHT = 299

def predict_image(image_path):
    try:
        if USE_FAKE_MODEL:
            time.sleep(1) # Simulate model processing time
            predicted_class_name = random.choice(CLASS_NAMES)
        
        else:
            img = image.load_img(image_path, target_size=(IMAGE_WIDTH, IMAGE_HEIGHT))
            
            # pre-process
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0) # Create a batch
            img_array = preprocess_input(img_array)  
            
            # hide the progress bar with verbose=0
            predictions = model.predict(img_array, verbose=0)
            predicted_index = np.argmax(predictions[0])
            predicted_class_name = CLASS_NAMES[predicted_index]
           
        return predicted_class_name

    except Exception as e:
        print(f"Error during prediction: {e}", file=sys.stderr)
        return "normal_road" # Default to 'normal_road' on error

if __name__ == "__main__":
    # The script is called with the image path as an argument
    if len(sys.argv) < 2:
        print("normal_road") # Output default if no path
        sys.exit(1)

    image_path_from_php = sys.argv[1]
    
    # Add verbose=0 to run in silent mode
    prediction = predict_image(image_path_from_php)
    # This is the only thing PHP's shell_exec() will capture.
    print(prediction)