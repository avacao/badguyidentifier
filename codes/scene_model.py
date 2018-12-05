# Reference: this code is from [VGG-19 pre-trained model for Keras]
# https://gist.github.com/baraldilorenzo/8d096f48a1be4a2d660d

import keras
from keras.models import Sequential
from keras.layers.core import Flatten, Dense, Dropout
from keras.layers.convolutional import Convolution2D, MaxPooling2D, ZeroPadding2D
from keras.optimizers import SGD
import cv2, numpy, pickle
from keras.applications import vgg19

import os, commons, baseline, random
from datetime import datetime

# THIS IS JUST FOR TESTING
SCENE_DIR = os.path.join(commons.FEATURES_DIR, "scene")
TRAIN_X = "train_x.pickle"
TRAIN_Y = "train_y.pickle"
TRAIN_WHO = "train_who.txt"
TEST_X = "test_x.pickle"
TEST_Y = "test_y.pickle"
TEST_WHO = "test_who.txt"
SCENE_MODEL = SCENE_DIR + 'model.joblib'

VGG19_ILSVRC_WEIGHT_PATH = "./weights/VGG19_ILSVRC_keras_weights.h5"

def VGG_19(weights_path=VGG19_ILSVRC_WEIGHT_PATH):
    model = Sequential()
    model.add(ZeroPadding2D((1,1), input_shape=(224,224,3)))

    model.add(keras.layers.Conv2D(64, (3,3), activation='relu', padding='same', name='block1_conv1'))
    model.add(keras.layers.Conv2D(64, (3,3), activation='relu', padding='same', name='block1_conv2'))
    model.add(MaxPooling2D((2,2), strides=(2,2), name='block1_pool'))

    model.add(keras.layers.Conv2D(128, (3,3), activation='relu', padding='same', name='block2_conv1'))
    model.add(keras.layers.Conv2D(128, (3,3), activation='relu', padding='same', name='block2_conv2'))
    model.add(MaxPooling2D((2,2), strides=(2,2), name='block2_pool'))

    model.add(keras.layers.Conv2D(256, (3,3), activation='relu', padding='same', name='block3_conv1'))
    model.add(keras.layers.Conv2D(256, (3,3), activation='relu', padding='same', name='block3_conv2'))
    model.add(keras.layers.Conv2D(256, (3,3), activation='relu', padding='same', name='block3_conv3'))
    model.add(keras.layers.Conv2D(256, (3,3), activation='relu', padding='same', name='block3_conv4'))
    model.add(MaxPooling2D((2,2), strides=(2,2), name='block3_pool'))

    model.add(keras.layers.Conv2D(512, (3,3), activation='relu', padding='same', name='block4_conv1'))
    model.add(keras.layers.Conv2D(512, (3,3), activation='relu', padding='same', name='block4_conv2'))
    model.add(keras.layers.Conv2D(512, (3,3), activation='relu', padding='same', name='block4_conv3'))
    model.add(keras.layers.Conv2D(512, (3,3), activation='relu', padding='same', name='block4_conv4'))
    model.add(MaxPooling2D((2,2), strides=(2,2), name='block4_pool'))

    model.add(keras.layers.Conv2D(512, (3,3), activation='relu', padding='same', name='block5_conv1'))
    model.add(keras.layers.Conv2D(512, (3,3), activation='relu', padding='same', name='block5_conv2'))
    model.add(keras.layers.Conv2D(512, (3,3), activation='relu', padding='same', name='block5_conv3'))
    model.add(keras.layers.Conv2D(512, (3,3), activation='relu', padding='same', name='block5_conv4'))
    model.add(MaxPooling2D((2,2), strides=(2,2), name='block5_pool'))

    model.add(keras.layers.Flatten(name='flatten'))
    model.add(Dense(4096, activation='relu', name='fc1'))
    model.add(Dense(4096, activation='relu', name='fc2'))
    model.add(Dense(1000, activation='softmax', name='prediction'))

    if weights_path:
        model.load_weights(weights_path)

    return model

def generate_vggface_data():
    if not os.path.exists(commons.FEATURES_DIR):
        os.mkdir(commons.FEATURES_DIR)

    if not os.path.exists(SCENE_DIR):
        os.mkdir(SCENE_DIR)

    # if we already got them...
    generated = (
        os.path.exists(SCENE_DIR + '/' + TRAIN_X) and
        os.path.exists(SCENE_DIR + '/' + TRAIN_Y) and
        os.path.exists(SCENE_DIR + '/' + TRAIN_WHO) and
        os.path.exists(SCENE_DIR + '/' + TEST_X) and
        os.path.exists(SCENE_DIR + '/' + TEST_Y) and
        os.path.exists(SCENE_DIR + '/' + TEST_WHO)
        )

    if generated:
        return

    # generate them, save, and return them!
    train_ids = set([])
    with open(commons.TRAIN_FILE, 'r') as f:
        for line in f.readlines():
            train_ids.add(line.strip())
    train_ids = set(random.sample(train_ids, 80))

    test_ids = set([])
    with open(commons.TEST_FILE, 'r') as f:
        for line in f.readlines():
            test_ids.add(line.strip())
    test_ids = set(random.sample(test_ids, 20))

    # encoding and separate (data, label)
    train_x, train_y, train_who, test_x, test_y, test_who = [], [], [], [], [], []
    labelof = commons.get_label()

    IMAGE_SIZE = 224
    vgg_model = VGG_19()
    
    # cnn_model = vgg19.VGG19(weights=VGG19_ILSVRC_WEIGHT_PATH, include_top=False)

    # vgg_model = vgg19.VGG19(weights=VGG19_ILSVRC_WEIGHT_PATH, input_shape=(IMAGE_SIZE, IMAGE_SIZE, 3))
    print(vgg_model.summary())
    cnn_model = keras.models.Model(inputs=vgg_model.input, outputs=vgg_model.get_layer('fc2').output)
    print(cnn_model.summary())

    print("Loading scene data...", datetime.now())

    image_filenames = [x for x in sorted(os.listdir(commons.TRAIN_IMAGES_DIR)) if len(x) > 4 and x[-4:] == '.jpg']
    for i in range(len(image_filenames)):
        print("{}/{}...".format(i, len(image_filenames)), end='\r')

        image_filename = image_filenames[i]
        imdb_id, character_id, timestamp = image_filename[:-4].split('-')
        character_id = int(character_id)

        # if this movie is not yet labeled
        if imdb_id not in labelof:
            continue

        if imdb_id not in train_ids and imdb_id not in test_ids:
            continue

        image = keras.preprocessing.image.load_img(
            os.path.join(commons.TRAIN_IMAGES_DIR, image_filename), 
            target_size=(IMAGE_SIZE, IMAGE_SIZE))

        x = keras.preprocessing.image.img_to_array(image)
        
        # VGG19 requires input to be zero-centered by mean pixel
        x[:,:,0] -= 103.939
        x[:,:,1] -= 116.779
        x[:,:,2] -= 123.68

        x = numpy.expand_dims(x, axis=0)
        x = vgg19.preprocess_input(x)
        x = cnn_model.predict(x)
        
        y = labelof[imdb_id][character_id]

        if imdb_id in train_ids:
            train_x.append(x)
            train_y.append(y)
            train_who.append(image_filename[:-4])
        else:
            test_x.append(x)
            test_y.append(y)
            test_who.append(image_filename[:-4])

    print("Done. ", datetime.now())

    with open(SCENE_DIR + '/' + TRAIN_X, 'wb') as f:
        pickle.dump(train_x, f)
    with open(SCENE_DIR + '/' + TRAIN_Y, 'wb') as f:
        pickle.dump(train_y, f) 
    with open(SCENE_DIR + '/' + TRAIN_WHO, 'w') as f:
        for who in test_who:
            f.write("{}\n".format(who))
    with open(SCENE_DIR + '/' + TEST_X, 'wb') as f:
        pickle.dump(test_x, f)
    with open(SCENE_DIR + '/' + TEST_Y, 'wb') as f:
        pickle.dump(test_y, f)
    with open(SCENE_DIR + '/' + TEST_WHO, 'w') as f:
        for who in test_who:
            f.write("{}\n".format(who))

def load_training_data():
    generate_vggface_data()
    with open(SCENE_DIR + '/' + TRAIN_X, 'rb') as f:
        train_x = pickle.load(f)
    with open(SCENE_DIR + '/' + TRAIN_Y, 'rb') as f:
        train_y = pickle.load(f)
    with open(SCENE_DIR + '/' + TRAIN_WHO, 'r') as f:
        train_who = []
        for line in f.readlines():
            train_who.append(line.strip())
    return (train_x, train_y, train_who)

def load_test_data():
    generate_vggface_data()
    with open(SCENE_DIR + '/' + TEST_X, 'rb') as f:
        test_x = pickle.load(f)
    with open(SCENE_DIR + '/' + TEST_Y, 'rb') as f:
        test_y = pickle.load(f)
    with open(SCENE_DIR + '/' + TEST_WHO, 'r') as f:
        test_who = []
        for line in f.readlines():
            test_who.append(line.strip())
    return (test_x, test_y, test_who)

if __name__ == '__main__':
    baseline.train(data=load_training_data(), model_path=SCENE_MODEL)
    baseline.test(data=load_test_data(), model_path=SCENE_MODEL)
