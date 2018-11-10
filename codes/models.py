import sklearn
from keras.applications import vgg16

def image_baseline():
	x = "tt0121766-0-29062.36666666667.jpg"
	
	cnn_model = vgg16.VGG16(weights='imagenet', include_top=False)
	