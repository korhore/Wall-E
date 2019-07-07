'''
Created on 30.04.2019
Updated on 26.05.2019

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
#import zipfile

#from distutils.version import StrictVersion
#from collections import defaultdict
#from io import StringIO
#from matplotlib import pyplot as plt
from PIL import Image as PIL_Image
from object_detection.utils import label_map_util
# from object_detection.utils import visualization_utils as vis_util
###
#from cognitive_planning import cognitive_planning

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
    
    NAME =              'name'
    DETECTION_SCORES =  'detection_scores'
    NUM_DETECTIONS =    'num_detections'
    DETECTION_CLASSES = 'detection_classes'
    DETECTION_BOXES =   'detection_boxes'
    DETECTION_MASKS =   'detection_masks'
    IMAGE_TENSOR =      'image_tensor:0'
    
    # For the sake of simplicity we will use only 2 images:
    # image1.jpg
    # image2.jpg
    # If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
    
    # What model to download.
    MODEL_NAME =            'ssd_mobilenet_v1_coco_2017_11_17'
    MODEL_FILE =            MODEL_NAME + '.tar.gz'
    DOWNLOAD_BASE =         'http://download.tensorflow.org/models/object_detection/'
    FROZEN_GRAPH_PB_NAME =  'frozen_inference_graph.pb'
    LIVE_GRAPH_PB_NAME =    'live_inference_graph.pb'
    DETECTION_SCORE_LIMIT = 0.1 #may be too low, but for testing purposes we want to detect something

    PATH_TO_GRAPH_DIR = os.path.join(Sensation.DATADIR, MODEL_NAME)
    # Path to frozen detection graph. This is the actual model that is used for the object detection.
    PATH_TO_FROZEN_GRAPH = os.path.join(Sensation.DATADIR, MODEL_NAME, FROZEN_GRAPH_PB_NAME)
    # Path to frozen detection graph. This will the actual model that is used for the object detection.
    PATH_TO_LIVE_GRAPH = os.path.join(PATH_TO_GRAPH_DIR, LIVE_GRAPH_PB_NAME)

    # List of the strings that is used to add correct label for each box.
    PATH_TO_LABELS = os.path.join(Sensation.DATADIR, 'mscoco_label_map.pbtxt')

    PATH_TO_TEST_IMAGES_DIR = 'test_images'
    #TEST_IMAGE_PATHS = [ os.path.join(PATH_TO_TEST_IMAGES_DIR, 'image{}.jpg'.format(i)) for i in range(1, 3) ]
    TEST_IMAGE_PATHS = [ os.path.join('test_images', 'image{}.jpg'.format(i)) for i in range(1, 3) ]
    
    # Size, in inches, of the output images.
    IMAGE_SIZE = (12, 8)

    # Seems that at least raspberry keep to restart it very often when running this Rpbot,
    # So the to sleep between runs    
    SLEEP_TIME_BETWEEN_PROCESSES =   1.0
  
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

        
#         opener = urllib.request.URLopener()
#         opener.retrieve(TensorFlowClassification.DOWNLOAD_BASE + TensorFlowClassification.MODEL_FILE, TensorFlowClassification.MODEL_FILE)
#         tar_file = tarfile.open(TensorFlowClassification.MODEL_FILE)
#         for file in tar_file.getmembers():
#             file_name = os.path.basename(file.name)
#             if 'frozen_inference_graph.pb' in file_name:
#                 tar_file.extract(file, os.getcwd())
#                 
#         TensorFlowClassification.detection_graph = tf.Graph()
#         with TensorFlowClassification.detection_graph.as_default():
#             od_graph_def = tf.GraphDef()
#             with tf.gfile.GFile(TensorFlowClassification.PATH_TO_FROZEN_GRAPH, 'rb') as fid:
#                 serialized_graph = fid.read()
#                 od_graph_def.ParseFromString(serialized_graph)
#                 tf.import_graph_def(od_graph_def, name='')
#                 
#         TensorFlowClassification.category_index = label_map_util.create_category_index_from_labelmap(TensorFlowClassification.PATH_TO_LABELS, use_display_name=True)
        #TensorFlowClassification.category_index = TensorFlowClassification.create_category_index_from_labelmap(TensorFlowClassification.PATH_TO_LABELS, use_display_name=True)

    def load_image_into_numpy_array(self, image):
      (im_width, im_height) = image.size
      return np.array(image.getdata()).reshape(
          (im_height, im_width, 3)).astype(np.uint8)

              
    def run_inference_for_single_image(self, image, graph):
        with graph.as_default():
            with tf.Session() as sess:
                # Get handles to input and output tensors
                ops = tf.get_default_graph().get_operations()
                all_tensor_names = {output.name for op in ops for output in op.outputs}
                tensor_dict = {}
                for key in [
                    self.NUM_DETECTIONS, self.DETECTION_BOXES, self.DETECTION_SCORES,
                    self.DETECTION_CLASSES, self.DETECTION_MASKS
                    ]:
                    tensor_name = key + ':0'
                    if tensor_name in all_tensor_names:
                        tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                            tensor_name)
                if self.DETECTION_MASKS in tensor_dict:
                    # The following processing is only for single image
                    detection_boxes = tf.squeeze(tensor_dict[self.DETECTION_BOXES], [0])
                    detection_masks = tf.squeeze(tensor_dict[self.DETECTION_MASKS], [0])
                    # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                    real_num_detection = tf.cast(tensor_dict[self.NUM_DETECTIONS][0], tf.int32)
                    detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                    detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                        detection_masks, detection_boxes, image.shape[1], image.shape[2])
                    detection_masks_reframed = tf.cast(
                        tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                    # Follow the convention by adding back the batch dimension
                    tensor_dict[self.DETECTION_MASKS] = tf.expand_dims(
                        detection_masks_reframed, 0)
                image_tensor = tf.get_default_graph().get_tensor_by_name(self.IMAGE_TENSOR)

                # Run inference
                output_dict = sess.run(tensor_dict,
                             feed_dict={image_tensor: image})

                # all outputs are float32 numpy arrays, so convert types as appropriate
                output_dict[self.NUM_DETECTIONS] = int(output_dict[self.NUM_DETECTIONS][0])
                output_dict[self.DETECTION_CLASSES] = output_dict[
                    self.DETECTION_CLASSES][0].astype(np.int64)
                output_dict[self.DETECTION_BOXES] = output_dict[self.DETECTION_BOXES][0]
                output_dict[self.DETECTION_SCORES] = output_dict[self.DETECTION_SCORES][0]
                if self.DETECTION_MASKS in output_dict:
                    output_dict[self.DETECTION_MASKS] = output_dict[self.DETECTION_MASKS][0]
        return output_dict
    
    

  
    def run(self):
        self.log(" Starting robot who " + self.getWho() + " kind " + self.config.getKind() + " instanceType " + str(self.config.getInstanceType()))      
        
        if not os.path.exists(TensorFlowClassification.PATH_TO_FROZEN_GRAPH):
            opener = urllib.request.URLopener()
            opener.retrieve(TensorFlowClassification.DOWNLOAD_BASE + TensorFlowClassification.MODEL_FILE, TensorFlowClassification.MODEL_FILE)
            tar_file = tarfile.open(TensorFlowClassification.MODEL_FILE)
            for file in tar_file.getmembers():
                file_name = os.path.basename(file.name)
                if TensorFlowClassification.FROZEN_GRAPH_PB_NAME in file_name:
                    tar_file.extract(file, Sensation.DATADIR)
                    
        TensorFlowClassification.detection_graph = tf.Graph()
        with TensorFlowClassification.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(TensorFlowClassification.PATH_TO_FROZEN_GRAPH, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
                
        TensorFlowClassification.category_index = label_map_util.create_category_index_from_labelmap(TensorFlowClassification.PATH_TO_LABELS, use_display_name=True)

        self.running=True
                
        # live until stopped
        self.mode = Sensation.Mode.Normal

        for image_path in self.TEST_IMAGE_PATHS:
            image = PIL_Image.open(image_path)
            # the array based representation of the image will be used later in order to prepare the
            # result image with boxes and labels on it.
            image_np = self.load_image_into_numpy_array(image)
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            # Actual detection.
            # TODO detection_graph where it is defined
            output_dict = self.run_inference_for_single_image(image_np_expanded, self.detection_graph)
            i=0  
            for classInd in output_dict[self.DETECTION_CLASSES]:
                self.log("image className " + self.category_index[classInd][self.NAME] + ' score ' + str(output_dict[self.DETECTION_SCORES][i]) +\
                         ' box ' + str(output_dict[self.DETECTION_BOXES][i]))
                i = i+1   

        while self.running:
            transferDirection, sensation = self.getAxon().get()
            self.log("got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())      
            self.process(transferDirection=transferDirection, sensation=sensation)
        self.log("Stopping TensorFlowClassification")
        self.mode = Sensation.Mode.Stopping
#         self.camera.close() 
       
        self.log("run ALL SHUT DOWN")

    def process(self, transferDirection, sensation):
        #run default implementation first
        super(TensorFlowClassification, self).process(transferDirection=transferDirection, sensation=sensation)
        if self.running:    # if still running
            self.log('TensorFlowClassification process: ' + time.ctime(sensation.getTime()) + ' ' + str(sensation.getDirection()) + ' ' + sensation.toDebugStr())
            # we can process this
            if sensation.getDirection() == Sensation.Direction.Out and \
               sensation.getSensationType() == Sensation.SensationType.Image and \
               sensation.getMemory() == Sensation.Memory.Sensory:
                #sensation.save()    # save to file TODO, not needed, but we need
                                    # numpy representation and example code does it from a file
                                    #Nope, just det it
                # image = PIL_Image.open(image_path)
                # the array based representation of the image will be used later in order to prepare the
                # result image with boxes and labels on it.
                image_np = self.load_image_into_numpy_array(sensation.getImage())
                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(image_np, axis=0)
                # Actual detection.
                # TODO detection_graph where it is defined
                output_dict = self.run_inference_for_single_image(image_np_expanded, self.detection_graph)
                i=0  
                for classInd in output_dict[self.DETECTION_CLASSES]:
                    if output_dict[self.DETECTION_SCORES][i] > TensorFlowClassification.DETECTION_SCORE_LIMIT:
                        # create new sensation of detected area and category
                        # subimage
                        im_width, im_height = sensation.getImage().size
                        ymin, xmin, ymax, xmax = output_dict[self.DETECTION_BOXES][i]
                        size = (xmin * im_width, ymin * im_height,
                                xmax * im_width, ymax * im_height)
                        score = output_dict[self.DETECTION_SCORES][i]
                        self.log('SEEN image FOR SURE className ' + self.category_index[classInd][self.NAME] + ' score ' + str(score) + \
                                 ' box ' + str(output_dict[self.DETECTION_BOXES][i]) + ' size ' + str(size))
                        subimage = sensation.getImage().crop(size)
                        subsensation = Sensation.create(sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.LongTerm, direction = Sensation.Direction.Out,\
                                                        image=subimage, associations=[Sensation.Association(sensation=sensation, score=score)])
                        subsensation.save()
                        # Item
                        itemsensation = Sensation.create(sensationType = Sensation.SensationType.Item, memory = Sensation.Memory.LongTerm, direction = Sensation.Direction.Out,\
                                                         name=self.category_index[classInd][self.NAME], associations=[Sensation.Association(sensation=subsensation, score=score)])
                        self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=subsensation)
                        self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=itemsensation)
                        self.log("Created LongTerm subImage and item sensation for this")
                        # TODO WE should classify this item also by className to detect separate item inside a class like 'Martha' in 'person'
                    i = i+1   
                # Seems that at least raspberry keep to restart it very often when riing thos Rpbot,
                # So the to sleep between runs
                # TODO, if this works, make sleep time as Configuration parameter  
                self.log("Sleeping " + str(TensorFlowClassification.SLEEP_TIME_BETWEEN_PROCESSES))
                time.sleep(TensorFlowClassification.SLEEP_TIME_BETWEEN_PROCESSES)
            
if __name__ == "__main__":
    TensorFlowClassification = tensorFlowClassification()
#    tensorFlowClassification.start()  
