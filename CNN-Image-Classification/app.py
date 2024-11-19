from flask import Flask, request, render_template, jsonify
import tensorflow as tf
from PIL import Image
import numpy as np
import cv2

app = Flask(__name__)

# Load the model
model = tf.keras.models.load_model('happysadmodel.h5')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'prediction': 'No file uploaded'})
    
    file = request.files['file']
    img = Image.open(file.stream)
    # img = cv2.imread(file.stream)
    img = tf.image.resize(img,(256,256))
    # img = img.resize((256, 256))  # Resize to match the input size of your model
    # img = img / 255  # Normalize the image to [0, 1]
    img = np.array(img) / 255.0  # Normalize the image to [0, 1]
    img = np.expand_dims(img,0)  # Add batch dimension

    prediction = model.predict(img)
    label = 'happy' if prediction[0][0] <= 0.5 else 'sad'
    print(prediction[0][0])
    try:
        return jsonify({'prediction': label})
    except Exception as e:
        print(e)


if __name__ == '__main__':
    app.run(debug=True)
