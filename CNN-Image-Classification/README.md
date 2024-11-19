
# CNN Image Classification

## Overview

The "CNN Image Classification" project aims to classify images as either happy or sad using deep learning techniques, specifically Convolutional Neural Networks (CNNs). The implementation is in Python, utilizing TensorFlow and Keras. The model is trained on a dataset containing labeled happy and sad images and is then used to predict unseen images' emotions.

## Installation

To set up the project on your local machine, follow these steps:

Clone the GitHub repository:

git clone https://github.com/Rhythm1821/CNN-Image-Classification.git


### Install the required dependencies:

pip install tensorflow opencv-python numpy requests matplotlib pillow

## Usage

To run the image classification script, ensure you have Python installed on your system. Then, execute the  app.py script available in the cloned repository.

**python3 app.py**

## Implementation Details

The project was implemented using Google Colab, following these steps:

* Downloaded happy and sad images from Google and stored them separately.
* Zipped the image folders and hosted them on a GitHub repository.
* In the Colab environment, wrote a python script to unzip the data.
* The dataset was labeled using TensorFlow.
* Images with a size less than 10KB were removed to improve data quality.
* A deep CNN model was constructed, utilizing TensorFlow and Keras.
* The model was trained using the Adam optimizer, categorical cross-entropy loss function, and accuracy as the metric.
* After training, loss and accuracy metrics were calculated.
* Unseen happy and sad images were used to make predictions using the trained model.
* The model was saved for future use.


## Support

For any inquiries or assistance, please refer to the official documentation for TensorFlow and OpenCV:

TensorFlow Documentation: https://www.tensorflow.org/

OpenCV Documentation: https://docs.opencv.org/
