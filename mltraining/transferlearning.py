import numpy as np
import cv2
import PIL.Image as Image
import os, pathlib, time
import matplotlib.pylab as plt
import tensorflow as tf
import tensorflow_hub as hub
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from sklearn.model_selection import train_test_split

def create_classifier(IMAGE_SHAPE):
    classifier = tf.keras.Sequential([
        hub.KerasLayerhub.KerasLayer("https://tfhub.dev/google/tf2-preview/mobilenet_v2/classification/4", input_shape=IMAGE_SHAPE+(3,))
    ])
    return classifier

def create_classifier2(IMAGE_SHAPE, model_path):
    model = tf.keras.models.load_model(model_path)
    output_shape = model.layers[-1].output_shape
    num_classes = output_shape[-1]
    print('Number of classes:', num_classes)

    return model

def preprocess_image(image_path, IMAGE_SHAPE):
    image = Image.open(image_path).resize(IMAGE_SHAPE)
    image_arr = np.array(image)/255.0
    return image_arr

def predict_label(model, image_arr):
    result = model.predict(image_arr[np.newaxis, ...])
    predict_label_index = np.argmax(result)
    return predict_label_index

def load_image_labels(input_file):
    with open(input_file, 'r') as f:
        image_labels = f.read().splitlines()
    return image_labels

def load_data(data_dir):
    data_dir = pathlib.Path(data_dir)
    images_dict = {}
    labels_dict = {}

    for idx, sub_dir in enumerate(data_dir.glob('*')):
        label_name = sub_dir.name.split('\\')[-1]
        images_dict[label_name] = list(sub_dir.glob('*.jpg'))
        labels_dict[label_name] = idx
    labels_dict_inv = {v: k for k, v in labels_dict.items()}
    num_classes = len(labels_dict)

    images = []
    labels = []

    for label_name, image_files in images_dict.items():
        for img_file in image_files:
            try:
                img = cv2.imread(str(img_file))
                if img is None:
                    raise ValueError("Unable to read image file")
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img = cv2.resize(img, (224, 224))
                images.append(img)
                labels.append(labels_dict[label_name])
            except Exception as e:
                print("Error reading image file:", img_file)
                print(e)
    
    images = np.array(images)
    labels = np.array(labels)

    # Train test split
    X_train, X_test, y_train, y_test = train_test_split(images, labels, random_state=0)

    # Preprocessing scale images
    X_train_scaled = X_train/255.0
    X_test_scaled = X_test/255.0

    return X_train_scaled, X_test_scaled, y_train, y_test, num_classes, labels_dict, labels_dict_inv

def build_model(num_classes, save_path=None):
    feature_extractor_model = "https://tfhub.dev/google/imagenet/mobilenet_v3_small_100_224/feature_vector/5"
    pretrained_model_without_top_layer = hub.KerasLayer(
        feature_extractor_model, input_shape=(224, 224, 3), trainable=False)
    model = tf.keras.Sequential([
        pretrained_model_without_top_layer,
        tf.keras.layers.Dense(num_classes)
    ])

    summary = model.summary()

    if save_path:
        summary_path = os.path.join(save_path, 'model_summary.txt')
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        with open(summary_path, 'w') as f:
            model.summary(print_fn=lambda x: f.write(x + '\n'))
    
    return model, summary, summary_path

def train_model(model, X_train_scaled, X_test_scaled, y_train, y_test, epochs, validation_split, save_path=None):
    # Compile the model
    model.compile(
        optimizer=tf.keras.optimizers.Adam(),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=['accuracy'])
    
    start_time = time.time()
    # Train the model
    history = model.fit(X_train_scaled, y_train, epochs=epochs, validation_split=validation_split)
    end_time = time.time()

    # Evaluate the model
    test_loss, test_acc = model.evaluate(X_test_scaled, y_test)
    
    print(f'Test loss: {test_loss:.4f}, Test accuracy: {test_acc:.4f}')
    print(f'Time elapsed for training: {end_time - start_time:.2f} seconds')
    
    if save_path:
        model.save(save_path)
    
    return test_loss, test_acc, end_time - start_time
