'''
Created on 30.04.2019
Updated on 20.05.2019

@author: reijo.korhonen@gmail.com
'''

import os
import time
import io
import time
import math

###
import numpy as np
#import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

from distutils.version import StrictVersion
from collections import defaultdict
from io import StringIO
#from matplotlib import pyplot as plt
from PIL import Image
#from utils import label_map_util

#from utils import visualization_utils as vis_util
###

#import tensorflow as tf

from Robot import  Robot
from Config import Config, Capabilities
from Sensation import Sensation



class TensorFlowClassification(Robot):
    '''    
    Process basic functionality is validate meaning level of the sensation.
    We should remember meaningful sensations and ignore (forget) less
    meaningful sensations. Implementation is dependent on memory level.
    
    When in Sensory level, we should process sensations very fast and
    detect changes.
    
    When in Work level, we are processing meanings of sensations.
    If much reference with high meaning level, also this sensation is meaningful
    
    When in Longterm level, we process memories. Which memories are still important
    and which memories we should forget.
    
    TODO above implementation is mostly for Hearing Sensory and
    Moving Sensory and should be move to those implementations.  
    '''
    
    
    FORMAT='jpeg'
    DATADIR='data'
    COMPARE_SQUARES=20
    CHANGE_RANGE=3000000
    SLEEP_TIME=10
    
    # For the sake of simplicity we will use only 2 images:
    # image1.jpg
    # image2.jpg
    # If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
    
    # What model to download.
    MODEL_NAME = 'ssd_mobilenet_v1_coco_2017_11_17'
    MODEL_FILE = MODEL_NAME + '.tar.gz'
    DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

    # Path to frozen detection graph. This is the actual model that is used for the object detection.
    PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'

    # List of the strings that is used to add correct label for each box.
    PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')

    PATH_TO_TEST_IMAGES_DIR = 'test_images'
    #TEST_IMAGE_PATHS = [ os.path.join(PATH_TO_TEST_IMAGES_DIR, 'image{}.jpg'.format(i)) for i in range(1, 3) ]
    TEST_IMAGE_PATHS = [ os.path.join('test_images', 'image{}.jpg'.format(i)) for i in range(1, 3) ]
    
    # Size, in inches, of the output images.
    IMAGE_SIZE = (12, 8)
  
    def __init__(self,
                 parent=None,
                 instanceName=None,
                 instanceType = Sensation.InstanceType.SubInstance,
                 level=0):
        print("We are in TensorFlowClassification, not Robot")
        Robot.__init__(self,
                       parent=parent,
                       instanceName=instanceName,
                       instanceType=instanceType,
                       level=level)
        

#         # this is dataset we use for training the model          
#         mnist = tf.keras.datasets.mnist
#         
#         (x_train, y_train),(x_test, y_test) = mnist.load_data()
# 
# #         # Feature columns describe how to use the input.
# #         my_feature_columns = []
# #         for key in x_train.keys():
# #             my_feature_columns.append(tf.feature_column.numeric_column(key=key))
# #             self.log("key " + str(key))      
# 
# 
#         
#         x_train, x_test = x_train / 255.0, x_test / 255.0
#         
#         model = tf.keras.models.Sequential([
#           tf.keras.layers.Flatten(input_shape=(28, 28)),
#           # 512 units
#           tf.keras.layers.Dense(512, activation=tf.nn.relu),
#           tf.keras.layers.Dropout(0.2),
#           tf.keras.layers.Dense(10, activation=tf.nn.softmax)
#         ])
#         model.compile(optimizer='adam',
#                       loss='sparse_categorical_crossentropy',
#                       metrics=['accuracy'])
#                    # data. labels, epochs, batch_size
#         model.fit(x_train, y_train, epochs=5)
#         model.evaluate(x_test, y_test)

        
        opener = urllib.request.URLopener()
        opener.retrieve(self.DOWNLOAD_BASE + self.MODEL_FILE, self.MODEL_FILE)
        tar_file = tarfile.open(self.MODEL_FILE)
        for file in tar_file.getmembers():
            file_name = os.path.basename(file.name)
            if 'frozen_inference_graph.pb' in file_name:
                tar_file.extract(file, os.getcwd())
                
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(self.PATH_TO_FROZEN_GRAPH, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
                
#        category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

    def load_image_into_numpy_array(image):
      (im_width, im_height) = image.size
      return np.array(image.getdata()).reshape(
          (im_height, im_width, 3)).astype(np.uint8)

              
    def run_inference_for_single_image(image, graph):
        with graph.as_default():
            with tf.Session() as sess:
                # Get handles to input and output tensors
                ops = tf.get_default_graph().get_operations()
                all_tensor_names = {output.name for op in ops for output in op.outputs}
                tensor_dict = {}
                for key in [
                    'num_detections', 'detection_boxes', 'detection_scores',
                    'detection_classes', 'detection_masks'
                    ]:
                    tensor_name = key + ':0'
                    if tensor_name in all_tensor_names:
                        tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                            tensor_name)
                if 'detection_masks' in tensor_dict:
                    # The following processing is only for single image
                    detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                    detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                    # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                    real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                    detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                    detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                        detection_masks, detection_boxes, image.shape[1], image.shape[2])
                    detection_masks_reframed = tf.cast(
                        tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                    # Follow the convention by adding back the batch dimension
                    tensor_dict['detection_masks'] = tf.expand_dims(
                        detection_masks_reframed, 0)
                image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

                # Run inference
                output_dict = sess.run(tensor_dict,
                             feed_dict={image_tensor: image})

                # all outputs are float32 numpy arrays, so convert types as appropriate
                output_dict['num_detections'] = int(output_dict['num_detections'][0])
                output_dict['detection_classes'] = output_dict[
                    'detection_classes'][0].astype(np.int64)
                output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
                output_dict['detection_scores'] = output_dict['detection_scores'][0]
                if 'detection_masks' in output_dict:
                    output_dict['detection_masks'] = output_dict['detection_masks'][0]
        return output_dict
  
    def run(self):
        self.log(" Starting robot who " + self.getWho() + " kind " + self.config.getKind() + " instanceType " + str(self.config.getInstanceType()))      
        
        # starting other threads/senders/capabilities
        
        self.running=False
                
        # live until stopped
        self.mode = Sensation.Mode.Normal
#         stream = io.BytesIO()
#         self.camera.start_preview()
#         # Camera warm-up time
#         time.sleep(2)

        for image_path in self.TEST_IMAGE_PATHS:
            image = Image.open(image_path)
            # the array based representation of the image will be used later in order to prepare the
            # result image with boxes and labels on it.
            image_np = TensorFlowClassification.load_image_into_numpy_array(image)
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            # Actual detection.
            # TODO detection_graph where it is defined
            output_dict = TensorFlowClassification.run_inference_for_single_image(image_np_expanded, self.detection_graph)
            # Visualization of the results of a detection.
# rko commented out
#             vis_util.visualize_boxes_and_labels_on_image_array(
#                 mage_np,
#                 output_dict['detection_boxes'],
#                 output_dict['detection_classes'],
#                 output_dict['detection_scores'],
#                 category_index,
#                 instance_masks=output_dict.get('detection_masks'),
#                 use_normalized_coordinates=True,
#                 line_thickness=8)
#             plt.figure(figsize=IMAGE_SIZE)
#             plt.imshow(image_np)

        while self.running:
            # as a leaf sensor robot default processing for sensation we have got
            # in practice we can get stop sensation
            if not self.getAxon().empty():
                sensation=self.getAxon().get()
                self.log("got sensation from queue " + sensation.toDebugStr())      
                self.process(sensation)
            else:
                self.log("self.camera.capture_continuous(stream, format=FORMAT)")
                stream = io.BytesIO()
                self.camera.capture(stream, format=self.FORMAT)
                self.camera.stop_preview()
                stream.seek(0)
                image = Image.open(stream)
                if self.isChangedImage(image):
                    self.log("self.getParent().getAxon().put(sensation) stream {}".format(len(stream.getvalue())))
                    sensation = Sensation.create(sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.Sensory, direction = Sensation.Direction.Out, data=stream.getvalue())
                    self.log("self.getParent().getAxon().put(sensation) getData")
#                    self.saveData(sensation)
                    self.saveData(sensation=sensation, image=image)
                    self.getParent().getAxon().put(sensation) # or self.process
                    self.camera.start_preview()
                time.sleep(self.SLEEP_TIME)
        self.log("Stopping TensorFlowClassification")
        self.mode = Sensation.Mode.Stopping
#         self.camera.close() 
       
        self.log("run ALL SHUT DOWN")

    '''
    compare image to previous one
    '''
           
    def isChangedImage(self, image):
        if self.lastImage is None:
            self.lastImage = image
            return True
        else:
            # calculate histogram change by squares color
            # we simply multiply color byt ins pixel count so we get roughly
            # how dark this square is
            y_size = image.size[1]/self.COMPARE_SQUARES
            x_size = image.size[0]/self.COMPARE_SQUARES
            change = 0
            for y in range(0,self.COMPARE_SQUARES):
                for x in range(0,self.COMPARE_SQUARES):
                    box = (x*x_size, y*y_size, (x+1)*x_size, (y+1)*y_size)
                    region = image.crop(box)
                    histogram = region.histogram()
                    last_region = self.lastImage.crop(box)
                    last_histogram = last_region.histogram()
                    sum=0
                    last_sum=0
                    for i in range(0,len(histogram)):
                        sum = sum+i*histogram[i]
                        last_sum = last_sum+i*last_histogram[i]
                    change = change + abs(sum-last_sum)

#             self.log("isChangedImage final change " + str(change) + ' change > self.CHANGE_RANGE '+ str(change > self.CHANGE_RANGE))
            if change > self.CHANGE_RANGE:
                self.lastImage = image
                return True
            return False


        
    def saveData(self, sensation, image=None):
        fileName = self.DATADIR + '/' + '{}'.format(sensation.getNumber()) + \
                   '.' +  self.FORMAT
        try:
            with open(fileName, "wb") as f:
                if image is None:
                    written=0
                    data = sensation.getData()
                    try:
                        while written < len(data):
                            written = written + f.write(data[written:])
                    except IOError as e:
                        self.log("f.write(data[written:]) error " + str(e))
                    finally:
                        f.close()
                else:
                    try:
                        image.save(f)
                    except IOError as e:
                        self.log("image.save(f) error " + str(e))
                    finally:
                        f.close()
        except Exception as e:
                self.log("open(fileName, wb) as f error " + str(e))
      

if __name__ == "__main__":
    TensorFlowClassification = tensorFlowClassification()
#    tensorFlowClassification.start()  