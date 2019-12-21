'''
Created on 30.04.2019
Updated on 28.07.2019

@author: reijo.korhonen@gmail.com
'''

import os
import io
import time as systemTime
import math

import numpy as np
import six.moves.urllib as urllib
import sys
import tarfile
import zipfile
#import tensorflow as tf
from PIL import Image as PIL_Image
#from object_detection.utils import label_map_util
import label_map_util


from Robot import  Robot
from Config import Config, Capabilities
from Sensation import Sensation

TensorFlow_LITE=False

if TensorFlow_LITE:
    try:
        print("TensorFlowClassification import tflite_runtime.interpreter as tflite")
        import tflite_runtime as tflite
        print("TensorFlowClassification import tflite_runtime.interpreter as tflite OK")
    except ImportError as e:
        print("TensorFlowClassification import tflite_runtime.interpreter as tflite error " + str(e))
        TensorFlow_LITE=False

if not TensorFlow_LITE:
    try:
        print("TensorFlowClassification import tensorflow as tf")
        import tensorflow as tf
        print("TensorFlowClassification import tensorflow as tf OK")
    except ImportError as e:
        print("TensorFlowClassification import tensorflow as tf error " + str(e))

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
    
    Get TF Lite model and labels
curl -O https://storage.googleapis.com/download.tensorflow.org/models/tflite/mobilenet_v1_1.0_224_quant_and_labels.zip
    
    '''

    TensorFlow_TEST = True                 # TensorFlow code test
                                           # allow this, if problems
    TensorFlow_LITE = False                # use Tensorflow lite
           
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
    
    # Normal live model handles as frozen model to download.
    MODEL_NAME =            'ssd_mobilenet_v1_coco_2017_11_17'
    MODEL_FILE =            MODEL_NAME + '.tar.gz'
    DOWNLOAD_BASE =         'http://download.tensorflow.org/models/object_detection/'
    FROZEN_GRAPH_PB_NAME =  'frozen_inference_graph.pb'
    LIVE_GRAPH_PB_NAME =    'live_inference_graph.pb'
    LITE_GRAPH_NAME =       'inference_graph..tflite'
    
    # LITE model to download, this can't be trained, so it is frozen
    LITE_MODEL_ZIP_NAME =       'mobilenet_v1_1.0_224_quant_and_labels.zip'
    LITE_MODEL_NAME =           'mobilenet_v1_1.0_224'
    LITE_MODEL_QUANT_NAME =     'mobilenet_v1_1.0_224_quant.tflite'
    LITE_MODEL_LABELS_NAME =    'labels_mobilenet_quant_v1_224.txt'
    LITE_DOWNLOAD_BASE =        'https://storage.googleapis.com/download.tensorflow.org/models/tflite/'
    LITE_PATH_TO_GRAPH_DIR = os.path.join(Sensation.DATADIR, LITE_MODEL_NAME)
    LITE_PATH_TO_FROZEN_GRAPH = os.path.join(Sensation.DATADIR, LITE_MODEL_NAME, LITE_MODEL_QUANT_NAME)
    LITE_PATH_TO_LABELS = os.path.join(Sensation.DATADIR, LITE_MODEL_NAME, LITE_MODEL_LABELS_NAME)
    
    
    DETECTION_SCORE_LIMIT = 0.4 # Maybe this is reasonable limit

    PATH_TO_GRAPH_DIR = os.path.join(Sensation.DATADIR, MODEL_NAME)
    # Path to frozen detection graph. This is the actual model that is used for the object detection.
    PATH_TO_FROZEN_GRAPH = os.path.join(Sensation.DATADIR, MODEL_NAME, FROZEN_GRAPH_PB_NAME)
    # Path to frozen detection graph. This will the actual model that is used for the object detection.
    PATH_TO_LIVE_GRAPH = os.path.join(PATH_TO_GRAPH_DIR, LIVE_GRAPH_PB_NAME)
    # Path to liten detection graph. This is the actual model that is used for the object detection.
    PATH_TO_LITE_GRAPH = os.path.join(Sensation.DATADIR, MODEL_NAME, LITE_GRAPH_NAME)

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
    
    present = {}       # which items are present
    
#     if TensorFlow_LITE:
#         try:
#             print("TensorFlowClassification import tflite_runtime.interpreter as tflite")
#             import tflite_runtime.interpreter as tflite
#             print("TensorFlowClassification import tflite_runtime.interpreter as tflite OK")
#         except ImportError as e:
#             print("TensorFlowClassification import tflite_runtime.interpreter as tflite error " + str(e))
#             TensorFlow_LITE=False
#     import tflite_runtime.interpreter as tflite
    
    '''
    presence of Item.name
    '''
    
    class Item():
        def __init__(self,
                     name,
                     presense):
            self.name = name
            self.presence = presence
            
        def getName(self):
            return self.name
        def setName(self, name):
            self.name = name

        def getPresence(self):
            return self.presence
        def setPresence(self, presence):
            self.npresence= presence
  
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
        self.lastImageTime=None
        self.tflite_model=None
        self.detection_graph = None
        

    def load_image_into_numpy_array(self, image):
      (im_width, im_height) = image.size
      return np.array(image.getdata()).reshape(
          (im_height, im_width, 3)).astype(np.uint8)

              
    def run_inference_for_single_image(self, image, graph):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='run_inference_for_single_image')
        with graph.as_default():
            with tf.compat.v1.Session() as sess:
                # Get handles to input and output tensors
                ops = tf.compat.v1.get_default_graph().get_operations()
                all_tensor_names = {output.name for op in ops for output in op.outputs}
                tensor_dict = {}
                for key in [
                    self.NUM_DETECTIONS, self.DETECTION_BOXES, self.DETECTION_SCORES,
                    self.DETECTION_CLASSES, self.DETECTION_MASKS
                    ]:
                    tensor_name = key + ':0'
                    if tensor_name in all_tensor_names:
                        tensor_dict[key] = tf.compat.v1.get_default_graph().get_tensor_by_name(
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
                image_tensor = tf.compat.v1.get_default_graph().get_tensor_by_name(self.IMAGE_TENSOR)

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
    
    def run_inference_for_single_image_LITE(self, image, graph):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='run_inference_for_single_image_LITE')
        with graph.as_default():
            with tflite.interpreter.Session() as sess:
                # Get handles to input and output tensors
                ops = tflite.interpreter.get_default_graph().get_operations()
                all_tensor_names = {output.name for op in ops for output in op.outputs}
                tensor_dict = {}
                for key in [
                    self.NUM_DETECTIONS, self.DETECTION_BOXES, self.DETECTION_SCORES,
                    self.DETECTION_CLASSES, self.DETECTION_MASKS
                    ]:
                    tensor_name = key + ':0'
                    if tensor_name in all_tensor_names:
                        tensor_dict[key] = tflite.interpreter.get_default_graph().get_tensor_by_name(
                            tensor_name)
                if self.DETECTION_MASKS in tensor_dict:
                    # The following processing is only for single image
                    detection_boxes = tflite.interpreter.squeeze(tensor_dict[self.DETECTION_BOXES], [0])
                    detection_masks = tflite.interpreter.squeeze(tensor_dict[self.DETECTION_MASKS], [0])
                    # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                    real_num_detection = tflite.interpreter.cast(tensor_dict[self.NUM_DETECTIONS][0], tflite.interpreter.int32)
                    detection_boxes = tflite.interpreter.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                    detection_masks = tflite.interpreter.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                        detection_masks, detection_boxes, image.shape[1], image.shape[2])
                    detection_masks_reframed = tflite.interpreter.cast(
                        tflite.interpreter.greater(detection_masks_reframed, 0.5), tflite.interpreter.uint8)
                    # Follow the convention by adding back the batch dimension
                    tensor_dict[self.DETECTION_MASKS] = tflite.interpreter.expand_dims(
                        detection_masks_reframed, 0)
                image_tensor = tflite.interpreter.get_default_graph().get_tensor_by_name(self.IMAGE_TENSOR)

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
        self.log("Starting robot who " + self.getWho() + " kind " + self.config.getKind() + " instanceType " + str(self.config.getInstanceType()))      

        if TensorFlow_LITE:        
            if not os.path.exists(TensorFlowClassification.LITE_PATH_TO_FROZEN_GRAPH):
                print(logLevel=Robot.LogLevel.Normal, logStr="downloading model " + TensorFlowClassification.LITE_PATH_TO_FROZEN_GRAPH)      
                opener = urllib.request.URLopener()
                opener.retrieve(TensorFlowClassification.LITE_DOWNLOAD_BASE + TensorFlowClassification.LITE_MODEL_ZIP_NAME, TensorFlowClassification.LITE_MODEL_ZIP_NAME)
                with zipfile.ZipFile(TensorFlowClassification.LITE_MODEL_ZIP_NAME, 'r') as zipObj:
                    # Extract all the contents of zip file in current directory
                    zipObj.extractall(TensorFlowClassification.LITE_PATH_TO_GRAPH_DIR)
            self.log(logLevel=Robot.LogLevel.Normal, logStr="LITE model is ready to use")
            
            self.log(logLevel=Robot.LogLevel.Normal, logStr="1 self.detection_graph = tflite.Graph()")
            self.detection_graph = tflite.Graph()
            self.log(logLevel=Robot.LogLevel.Normal, logStr="2 with self.detection_graph.as_default()")
            with self.detection_graph.as_default():
                self.log(logLevel=Robot.LogLevel.Normal, logStr="3 od_graph_def = tflite.GraphDef()")
                od_graph_def = tflite.GraphDef()
                self.log(logLevel=Robot.LogLevel.Normal, logStr="4 with tflite.gfile.GFile(TensorFlowClassification.LITE_PATH_TO_FROZEN_GRAPH, rb) as fid")
                with tflite.gfile.GFile(TensorFlowClassification.LITE_PATH_TO_FROZEN_GRAPH, 'rb') as fid:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr="5 serialized_graph = fid.read()")
                    serialized_graph = fid.read()
                    self.log(logLevel=Robot.LogLevel.Normal, logStr="6 od_graph_def.ParseFromString(serialized_graph)")
                    od_graph_def.ParseFromString(serialized_graph)
                    self.log(logLevel=Robot.LogLevel.Normal, logStr="7 tflite.import_graph_def(od_graph_def, name='')")
                    tflite.import_graph_def(od_graph_def, name='')
                    
            TensorFlowClassification.category_index = label_map_util.create_category_index_from_labelmap(TensorFlowClassification.LITE_PATH_TO_LABELS, use_display_name=True)
            self.log(logLevel=Robot.LogLevel.Normal, logStr="TensorFlowClassification.category_indexmodel DONE")
            
        else:
            if not os.path.exists(TensorFlowClassification.PATH_TO_FROZEN_GRAPH):
                self.log(logLevel=Robot.LogLevel.Normal, logStr="downloading model " + TensorFlowClassification.PATH_TO_FROZEN_GRAPH)      
                opener = urllib.request.URLopener()
                opener.retrieve(TensorFlowClassification.DOWNLOAD_BASE + TensorFlowClassification.MODEL_FILE, TensorFlowClassification.MODEL_FILE)
                tar_file = tarfile.open(TensorFlowClassification.MODEL_FILE)
                self.log(logLevel=Robot.LogLevel.Normal, logStr="setting model classes")      
                for file in tar_file.getmembers():
                    file_name = os.path.basename(file.name)
                    if TensorFlowClassification.FROZEN_GRAPH_PB_NAME in file_name:
                        tar_file.extract(file, Sensation.DATADIR)
            self.log(logLevel=Robot.LogLevel.Normal, logStr="model is ready to use")
                    
            self.detection_graph = tf.Graph()
            self.log(logLevel=Robot.LogLevel.Normal, logStr="1")
            with self.detection_graph.as_default():
                self.log(logLevel=Robot.LogLevel.Normal, logStr="2")
                od_graph_def = tf.compat.v1.GraphDef()
                self.log(logLevel=Robot.LogLevel.Normal, logStr="3")
                with tf.io.gfile.GFile(TensorFlowClassification.PATH_TO_FROZEN_GRAPH, 'rb') as fid:
                    self.log(logLevel=Robot.LogLevel.Normal, logStr="4")
                    serialized_graph = fid.read()
                    self.log(logLevel=Robot.LogLevel.Normal, logStr="5")
                    od_graph_def.ParseFromString(serialized_graph)
                    self.log(logLevel=Robot.LogLevel.Normal, logStr="6")
                    tf.compat.v1.import_graph_def(od_graph_def, name='')
                    self.log(logLevel=Robot.LogLevel.Normal, logStr="7")
            self.log(logLevel=Robot.LogLevel.Normal, logStr="detection_grap OK")
                   
            TensorFlowClassification.category_index = \
                label_map_util.create_category_index_from_labelmap(label_map_path=TensorFlowClassification.PATH_TO_LABELS,
                                                                   gfile = tf.io.gfile,
                                                                   use_display_name=True)
            self.log(logLevel=Robot.LogLevel.Normal, logStr="category_index OK")
#         if TensorFlowClassification.TensorFlow_LITE:
#             try:
#                 self.log(logLevel=Robot.LogLevel.Normal, logStr='run: convert LITE model' )
#                 converter = tf.lite.TFLiteConverter.from_keras_model(self.detection_graph)
#                 self.tflite_model = converter.convert()
#             except Exception as e:
#                 self.log(logLevel=Robot.LogLevel.Normal, logStr='run: convert LITE model error ' + str(e))
#                 TensorFlowClassification.TensorFlow_LITE=False
#         else:
#             self.log(logLevel=Robot.LogLevel.Normal, logStr='run: NO LITE' )

        self.running=True
                
        # live until stopped
        self.mode = Sensation.Mode.Normal

        if TensorFlowClassification.TensorFlow_TEST:
            self.log(logLevel=Robot.LogLevel.Normal, logStr="Testing")
            for image_path in self.TEST_IMAGE_PATHS:
                image = PIL_Image.open(image_path)
                # the array based representation of the image will be used later in order to prepare the
                # result image with boxes and labels on it.
                image_np = self.load_image_into_numpy_array(image)
                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(image_np, axis=0)
                # Actual detection.
                # TODO detection_graph where it is defined
                if (TensorFlowClassification.TensorFlow_LITE) and (self.tflite_model != None):
                    output_dict = self.run_inference_for_single_image_LITE(image_np_expanded, self.tflite_model)
                else:
                    output_dict = self.run_inference_for_single_image(image_np_expanded, self.detection_graph)
                i=0  
                for classInd in output_dict[self.DETECTION_CLASSES]:
                    self.log("image className " + self.category_index[classInd][self.NAME] + ' score ' + str(output_dict[self.DETECTION_SCORES][i]) +\
                             ' box ' + str(output_dict[self.DETECTION_BOXES][i]))
                    i = i+1   

        self.log(logLevel=Robot.LogLevel.Normal, logStr="Running")
        while self.running:
            transferDirection, sensation, association = self.getAxon().get()
            self.log("got sensation from queue " + str(transferDirection) + ' ' + sensation.toDebugStr())      
            self.process(transferDirection=transferDirection, sensation=sensation, association=association)
        self.log("Stopping TensorFlowClassification")
        self.mode = Sensation.Mode.Stopping
#         self.camera.close() 
       
        self.log("run ALL SHUT DOWN")

    def process(self, transferDirection, sensation, association=None):
        self.log(logLevel=Robot.LogLevel.Normal, logStr='process: ' + systemTime.ctime(sensation.getTime()) + ' ' + str(transferDirection) +  ' ' + sensation.toDebugStr())
        if sensation.getSensationType() == Sensation.SensationType.Stop:
            self.log(logLevel=Robot.LogLevel.Normal, logStr='process: SensationSensationType.Stop')      
            self.stop()
        elif sensation.getDirection() == Sensation.Direction.Out and \
               sensation.getSensationType() == Sensation.SensationType.Image and \
               sensation.getMemory() == Sensation.Memory.Sensory: # and\ # todo, no ordercontrl for testing
               #(self.lastImageTime is None or sensation.getTime() > self.lastImageTime):    # sensation should come in order
            self.lastImageTime = sensation.getTime()
             # we can process this   
            current_present = {}
            # the array based representation of the image will be used later in order to prepare the
            # result image with boxes and labels on it.
            image_np = self.load_image_into_numpy_array(sensation.getImage())
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            # Actual detection.
            # TODO detection_graph where it is defined
            if (TensorFlowClassification.TensorFlow_LITE) and (self.tflite_model != None):
                output_dict = self.run_inference_for_single_image_LITE(image_np_expanded, self.tflite_model)
            else:
                 output_dict = self.run_inference_for_single_image(image_np_expanded, self.detection_graph)
            
            i=0
            names=[]
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
                    # Item
                    name = self.category_index[classInd][self.NAME]
                    #if name not in current_present:
                    #    current_present.append(name)
                    change, precence = self.getPresence(name=name,names=names)
                    current_present[name] = precence
                    if change:
                        subimage = sensation.getImage().crop(size)
                        subsensation = Sensation.create(sensationType = Sensation.SensationType.Image, memory = Sensation.Memory.LongTerm, direction = Sensation.Direction.Out,\
                                                        image=subimage)
                        self.log("process created subimage sensation " + subsensation.toDebugStr())
                        # don't associate to original image sensation
                        # we wan't to save memory and subimage is important, not whore image
                        #subsensation.associate(sensation=sensation, score=score)
                        subsensation.save()
                        
                        itemsensation = Sensation.create(sensationType = Sensation.SensationType.Item, memory = Sensation.Memory.LongTerm, direction = Sensation.Direction.Out, name=name,\
                                                         presence = precence)
                        itemsensation.associate(sensation=subsensation, score=score)
                        self.log("process created present itemsensation " + itemsensation.toDebugStr() + ' score ' + str(score))
                        self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=subsensation, association=subsensation.getAssociation(sensation=itemsensation))
                        self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=itemsensation, association=subsensation.getAssociation(sensation=subsensation))
                        self.log("Created LongTerm subImage and item sensation for this")
                    # TODO WE should classify this item also by className to detect separate item inside a class like 'Martha' in 'person'
                i = i+1
            self.logAbsents(present=current_present)  
            # Seems that at least raspberry keep to restart it very often when running this Rpbot,
            # So the to sleep between runs
            # TODO, if this works, make sleep time as Configuration parameter  
            self.log("Sleeping " + str(TensorFlowClassification.SLEEP_TIME_BETWEEN_PROCESSES))
            systemTime.sleep(TensorFlowClassification.SLEEP_TIME_BETWEEN_PROCESSES)
        else:
            self.log(logLevel=Robot.LogLevel.Error, logStr='process: got sensation we this robot can\'t process')
 
    def getPresence(self, name, names):
            change = False
            if name not in names:   # we don't calculate detected names count
                                    # or try to identify name yet
                names.append(name)
                if name not in TensorFlowClassification.present:
                    self.log("Name " + name + " Entering")
                    TensorFlowClassification.present[name] = Sensation.Presence.Entering
                    return True, Sensation.Presence.Entering
                elif TensorFlowClassification.present[name] == Sensation.Presence.Entering:
                    TensorFlowClassification.present[name] = Sensation.Presence.Present
                    self.log("Name " + name + " Entering to Present")
                    return True, Sensation.Presence.Present
                self.log("Name " + name + " Still Present")
                return True, Sensation.Presence.Present
            else:
                self.log("Name " + name + " another instance, ignored")
            return False, None
           
    def logAbsents(self, present):
        absent_names=[]
        for name, presence in TensorFlowClassification.present.items():
            if name not in present:
                if presence == Sensation.Presence.Exiting:
                   presence = Sensation.Presence.Absent
                   absent_names.append(name)
                else:
                   presence = Sensation.Presence.Exiting  
                   TensorFlowClassification.present[name] = presence
                itemsensation = Sensation.create(sensationType = Sensation.SensationType.Item, memory = Sensation.Memory.LongTerm, direction = Sensation.Direction.Out, name=name,\
                                                 presence = presence)
                self.getParent().getAxon().put(transferDirection=Sensation.TransferDirection.Up, sensation=itemsensation, association=None)
                self.log("process created exiting/absent itemsensation " + itemsensation.toDebugStr())
        # can't del in loop, do it here
        for name in absent_names:
            del TensorFlowClassification.present[name]


                
          
if __name__ == "__main__":
    if not os.path.exists(TensorFlowClassification.LITE_PATH_TO_FROZEN_GRAPH):
        print("downloading model " + TensorFlowClassification.LITE_PATH_TO_FROZEN_GRAPH)      
        opener = urllib.request.URLopener()
        opener.retrieve(TensorFlowClassification.LITE_DOWNLOAD_BASE + TensorFlowClassification.LITE_MODEL_FILE, TensorFlowClassification.LITE_MODEL_FILE)
        zip_file = zipfile.open(TensorFlowClassification.LITE_MODEL_FILE)
        print("setting model classes")      
        for file in zip_file.getmembers():
            file_name = os.path.basename(file.name)
            if TensorFlowClassification.FROZEN_GRAPH_PB_NAME in file_name:
                zip_file.extract(file, Sensation.DATADIR)
    print("model is ready to use")
