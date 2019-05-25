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
#import zipfile

from distutils.version import StrictVersion
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
        opener.retrieve(TensorFlowClassification.DOWNLOAD_BASE + TensorFlowClassification.MODEL_FILE, TensorFlowClassification.MODEL_FILE)
        tar_file = tarfile.open(TensorFlowClassification.MODEL_FILE)
        for file in tar_file.getmembers():
            file_name = os.path.basename(file.name)
            if 'frozen_inference_graph.pb' in file_name:
                tar_file.extract(file, os.getcwd())
                
        TensorFlowClassification.detection_graph = tf.Graph()
        with TensorFlowClassification.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(TensorFlowClassification.PATH_TO_FROZEN_GRAPH, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
                
        TensorFlowClassification.category_index = label_map_util.create_category_index_from_labelmap(TensorFlowClassification.PATH_TO_LABELS, use_display_name=True)
        #TensorFlowClassification.category_index = TensorFlowClassification.create_category_index_from_labelmap(TensorFlowClassification.PATH_TO_LABELS, use_display_name=True)

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
    
    '''
    utils
    '''
    
#     def create_category_index_from_labelmap(label_map_path, use_display_name=True):
#         """
#         Reads a label map and returns a category index.
#     
#         Args:
#             label_map_path: Path to `StringIntLabelMap` proto text file.
#             use_display_name: (boolean) choose whether to load 'display_name' field
#               as category name.  If False or if the display_name field does not exist,
#               uses 'name' field as category names instead.
#         
#         Returns:
#             A category index, which is a dictionary that maps integer ids to dicts
#             containing categories, e.g.
#             {1: {'id': 1, 'name': 'dog'}, 2: {'id': 2, 'name': 'cat'}, ...}
#         """
#         
#         categories = TensorFlowClassification.create_categories_from_labelmap(label_map_path, use_display_name)
#         return TensorFlowClassification.create_category_index(categories)
# 
#     def create_categories_from_labelmap(label_map_path, use_display_name=True):
#         """Reads a label map and returns categories list compatible with eval.
#     
#           This function converts label map proto and returns a list of dicts, each of
#           which  has the following keys:
#             'id': an integer id uniquely identifying this category.
#             'name': string representing category name e.g., 'cat', 'dog'.
#     
#           Args:
#             label_map_path: Path to `StringIntLabelMap` proto text file.
#             use_display_name: (boolean) choose whether to load 'display_name' field
#               as category name.  If False or if the display_name field does not exist,
#               uses 'name' field as category names instead.
#     
#           Returns:
#             categories: a list of dictionaries representing all possible categories.
#         """
#         label_map = TensorFlowClassification.load_labelmap(label_map_path)
#         max_num_classes = max(item.id for item in label_map.item)
#         return TensorFlowClassification.convert_label_map_to_categories(label_map, max_num_classes,
#                                          use_display_name)
# 
#     def convert_label_map_to_categories(label_map,
#                                     max_num_classes,
#                                     use_display_name=True):
#         """Given label map proto returns categories list compatible with eval.
#         
#           This function converts label map proto and returns a list of dicts, each of
#           which  has the following keys:
#             'id': (required) an integer id uniquely identifying this category.
#             'name': (required) string representing category name
#               e.g., 'cat', 'dog', 'pizza'.
#           We only allow class into the list if its id-label_id_offset is
#           between 0 (inclusive) and max_num_classes (exclusive).
#           If there are several items mapping to the same id in the label map,
#           we will only keep the first one in the categories list.
#         
#           Args:
#             label_map: a StringIntLabelMapProto or None.  If None, a default categories
#               list is created with max_num_classes categories.
#             max_num_classes: maximum number of (consecutive) label indices to include.
#             use_display_name: (boolean) choose whether to load 'display_name' field as
#               category name.  If False or if the display_name field does not exist, uses
#               'name' field as category names instead.
#         
#           Returns:
#             categories: a list of dictionaries representing all possible categories.
#         """
#         categories = []
#         list_of_ids_already_added = []
#         if not label_map:
#           label_id_offset = 1
#           for class_id in range(max_num_classes):
#             categories.append({
#                 'id': class_id + label_id_offset,
#                 'name': 'category_{}'.format(class_id + label_id_offset)
#             })
#           return categories
#         for item in label_map.item:
#           if not 0 < item.id <= max_num_classes:
#             logging.info(
#                 'Ignore item %d since it falls outside of requested '
#                 'label range.', item.id)
#             continue
#           if use_display_name and item.HasField('display_name'):
#             name = item.display_name
#           else:
#             name = item.name
#           if item.id not in list_of_ids_already_added:
#             list_of_ids_already_added.append(item.id)
#             categories.append({'id': item.id, 'name': name})
#         return categories
#     
#     def load_labelmap(path):
#         """Loads label map proto.
# 
#         Args:
#             path: path to StringIntLabelMap proto text file.
#         Returns:
#             a StringIntLabelMapProto
#         """
#         with tf.gfile.GFile(path, 'r') as fid:
#             label_map_string = fid.read()
#             label_map = string_int_label_map_pb2.StringIntLabelMap()
#             try:
#                 text_format.Merge(label_map_string, label_map)
#             except text_format.ParseError:
#                 label_map.ParseFromString(label_map_string)
#         _validate_label_map(label_map)
#         return label_map
#     
# 
#     def _validate_label_map(label_map):
#         """Checks if a label map is valid.
# 
#         Args:
#             label_map: StringIntLabelMap to validate.
# 
#         Raises:
#             ValueError: if label map is invalid.
#         """
#         for item in label_map.item:
#             if item.id < 0:
#                 raise ValueError('Label map ids should be >= 0.')
#             if (item.id == 0 and item.name != 'background' and
#                 item.display_name != 'background'):
#                 raise ValueError('Label map id 0 is reserved for the background label')
#             
#             
#     def create_category_index(categories):
#         """Creates dictionary of COCO compatible categories keyed by category id.
#         
#         Args:
#             categories: a list of dicts, each of which has the following keys:
#               'id': (required) an integer id uniquely identifying this category.
#               'name': (required) string representing category name
#                 e.g., 'cat', 'dog', 'pizza'.
#         
#         Returns:
#             category_index: a dict containing the same entries as categories, but keyed
#               by the 'id' field of each category.
#         """
#         category_index = {}
#         for cat in categories:
#             category_index[cat['id']] = cat
#         return category_index
  
    def run(self):
        self.log(" Starting robot who " + self.getWho() + " kind " + self.config.getKind() + " instanceType " + str(self.config.getInstanceType()))      
        
        # starting other threads/senders/capabilities
        
        self.running=False
                
        # live until stopped
        self.mode = Sensation.Mode.Normal

        for image_path in self.TEST_IMAGE_PATHS:
            image = PIL_Image.open(image_path)
            # the array based representation of the image will be used later in order to prepare the
            # result image with boxes and labels on it.
            image_np = TensorFlowClassification.load_image_into_numpy_array(image)
            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image_np, axis=0)
            # Actual detection.
            # TODO detection_graph where it is defined
            output_dict = TensorFlowClassification.run_inference_for_single_image(image_np_expanded, self.detection_graph)
            # Visualization of the results of a detection.
# rko commented out, this is very hard to get working with Ubuntu 14.04, because of denpendecies
# Study vis_util.visualize_boxes_and_labels_on_image_array
#             vis_util.visualize_boxes_and_labels_on_image_array(
#                 mage_np,
#                 output_dict['detection_boxes'],
#                 output_dict['detection_classes'],
#                 output_dict['detection_scores'],
#                 self.category_index,
#                 instance_masks=output_dict.get('detection_masks'),
#                 use_normalized_coordinates=True,
#                 line_thickness=8)
#             plt.figure(figsize=self.IMAGE_SIZE)
#             plt.imshow(image_np)
            
            classNames = self.getClassNames(
                output_dict['detection_classes'],
                self.category_index)
            self.log("image classnames " + str(classNames))     

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
                image = PIL_Image.open(stream)
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

    #def visualize_boxes_and_labels_on_image_array(self,
#         image,
#         boxes,
    def getClassNames(self,
         classes,
#         scores,
         category_index):
        
        class_names=[]
        
        for c in classes:
            class_name = category_index[c]['name']
            class_names.append(class_name)
        return class_names


#         instance_masks=None,
#         instance_boundaries=None,
#         keypoints=None,
#         track_ids=None,
#         use_normalized_coordinates=False,
#         max_boxes_to_draw=20,
#         min_score_thresh=.5,
#         agnostic_mode=False,
#         line_thickness=4,
#         groundtruth_box_visualization_color='black',
#         skip_scores=False,
#         skip_labels=False,
#         skip_track_ids=False):
    """Overlay labeled boxes on an image with formatted scores and label names.
    
      This function groups boxes that correspond to the same location
      and creates a display string for each detection and overlays these
      on the image. Note that this function modifies the image in place, and returns
      that same image.
    
      Args:
        image: uint8 numpy array with shape (img_height, img_width, 3)
        boxes: a numpy array of shape [N, 4]
        classes: a numpy array of shape [N]. Note that class indices are 1-based,
          and match the keys in the label map.
        scores: a numpy array of shape [N] or None.  If scores=None, then
          this function assumes that the boxes to be plotted are groundtruth
          boxes and plot all boxes as black with no classes or scores.
        category_index: a dict containing category dictionaries (each holding
          category index `id` and category name `name`) keyed by category indices.
        instance_masks: a numpy array of shape [N, image_height, image_width] with
          values ranging between 0 and 1, can be None.
        instance_boundaries: a numpy array of shape [N, image_height, image_width]
          with values ranging between 0 and 1, can be None.
        keypoints: a numpy array of shape [N, num_keypoints, 2], can
          be None
        track_ids: a numpy array of shape [N] with unique track ids. If provided,
          color-coding of boxes will be determined by these ids, and not the class
          indices.
        use_normalized_coordinates: whether boxes is to be interpreted as
          normalized coordinates or not.
        max_boxes_to_draw: maximum number of boxes to visualize.  If None, draw
          all boxes.
        min_score_thresh: minimum score threshold for a box to be visualized
        agnostic_mode: boolean (default: False) controlling whether to evaluate in
          class-agnostic mode or not.  This mode will display scores but ignore
          classes.
        line_thickness: integer (default: 4) controlling line width of the boxes.
        groundtruth_box_visualization_color: box color for visualizing groundtruth
          boxes
        skip_scores: whether to skip score when drawing a single detection
        skip_labels: whether to skip label when drawing a single detection
        skip_track_ids: whether to skip track id when drawing a single detection
    
      Returns:
        uint8 numpy array with shape (img_height, img_width, 3) with overlaid boxes.
      """
      # Create a display string (and color) for every box location, group any boxes
      # that correspond to the same location.
#       box_to_display_str_map = collections.defaultdict(list)
#       box_to_color_map = collections.defaultdict(str)
#       box_to_instance_masks_map = {}
#       box_to_instance_boundaries_map = {}
#       box_to_keypoints_map = collections.defaultdict(list)
#       box_to_track_ids_map = {}
#       if not max_boxes_to_draw:
#         max_boxes_to_draw = boxes.shape[0]
#       for i in range(min(max_boxes_to_draw, boxes.shape[0])):
#         if scores is None or scores[i] > min_score_thresh:
#           box = tuple(boxes[i].tolist())
#           if instance_masks is not None:
#             box_to_instance_masks_map[box] = instance_masks[i]
#           if instance_boundaries is not None:
#             box_to_instance_boundaries_map[box] = instance_boundaries[i]
#           if keypoints is not None:
#             box_to_keypoints_map[box].extend(keypoints[i])
#           if track_ids is not None:
#             box_to_track_ids_map[box] = track_ids[i]
#           if scores is None:
#             box_to_color_map[box] = groundtruth_box_visualization_color
#           else:
#             display_str = ''
#             if not skip_labels:
#               if not agnostic_mode:
#                 if classes[i] in category_index.keys():
#                   class_name = category_index[classes[i]]['name']
#                 else:
#                   class_name = 'N/A'
#                 display_str = str(class_name)
#             if not skip_scores:
#               if not display_str:
#                 display_str = '{}%'.format(int(100*scores[i]))
#               else:
#                 display_str = '{}: {}%'.format(display_str, int(100*scores[i]))
#             if not skip_track_ids and track_ids is not None:
#               if not display_str:
#                 display_str = 'ID {}'.format(track_ids[i])
#               else:
#                 display_str = '{}: ID {}'.format(display_str, track_ids[i])
#             box_to_display_str_map[box].append(display_str)
#             if agnostic_mode:
#               box_to_color_map[box] = 'DarkOrange'
#             elif track_ids is not None:
#               prime_multipler = _get_multiplier_for_color_randomness()
#               box_to_color_map[box] = STANDARD_COLORS[
#                   (prime_multipler * track_ids[i]) % len(STANDARD_COLORS)]
#             else:
#               box_to_color_map[box] = STANDARD_COLORS[
#                   classes[i] % len(STANDARD_COLORS)]
#     
#       # Draw all boxes onto image.
#       for box, color in box_to_color_map.items():
#         ymin, xmin, ymax, xmax = box
#         if instance_masks is not None:
#           draw_mask_on_image_array(
#               image,
#               box_to_instance_masks_map[box],
#               color=color
#           )
#         if instance_boundaries is not None:
#           draw_mask_on_image_array(
#               image,
#               box_to_instance_boundaries_map[box],
#               color='red',
#               alpha=1.0
#           )
#         draw_bounding_box_on_image_array(
#             image,
#             ymin,
#             xmin,
#             ymax,
#             xmax,
#             color=color,
#             thickness=line_thickness,
#             display_str_list=box_to_display_str_map[box],
#             use_normalized_coordinates=use_normalized_coordinates)
#         if keypoints is not None:
#           draw_keypoints_on_image_array(
#               image,
#               box_to_keypoints_map[box],
#               color=color,
#               radius=line_thickness / 2,
#               use_normalized_coordinates=use_normalized_coordinates)
#     
#       return image
           
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
