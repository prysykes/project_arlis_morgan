import os
import cv2
import numpy as np

from shapely import geometry

from ultralytics import YOLO
from collections import Counter

parent_dir = os.getcwd()
yolo_config = os.path.join(parent_dir, 'yolo_config')
coco_name = os.path.join(yolo_config, 'coco.names')

# print(os.path.isfile(coco_name))

classes = {}

# font = cv2.FONT_HERSHEY_PLAIN

with open(coco_name, 'r') as f:
    # classes = [line.strip() for line in f.readlines()]
    for idx, line in enumerate(f.readlines()):
        # print(idx, line)
        classes[idx] = line.strip()


images_dir = '/Users/prynet/Documents/workspace/project_arlis/media/met_data_try'


class YOLOSegmentation:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
    
    
    def run_yolo(self, img):
        height, width, channels = img.shape
        # print(f"img-height: {height}  \n img_width {width}")

        results = self.model(img, save=True, save_txt=False)
        results = results[0]
        segmentation_countour_idx = []
        for seg in results.masks.xy:
            
            segment = np.array(seg, dtype=np.int32).tolist()
            segmentation_countour_idx.append(segment)

        bbboxes = np.array(results.boxes.xyxy.cpu(), dtype='int').tolist()
        # print("bbboxes", bbboxes)
        #get class ids
        class_ids = np.array(results.boxes.cls.cpu(), dtype='int').tolist()

        #get scores
        scores = np.array(results.boxes.conf.cpu(), dtype="float").round(2).tolist()
        # scores = round(scores, 2)
        print(bbboxes, file=open('outerloop_bbox.txt', 'a'))
        return bbboxes, class_ids, segmentation_countour_idx, scores


def handle_meta_data_api_obj_det(current_image, img_area):
    # print("", os.path.isfile(current_image))
    img = cv2.imread(current_image)
    # img = cv2.resize(img, None, fx=0.2, fy=0.2)
    yolo_segmentation = YOLOSegmentation('yolov8l-seg.pt')
    bbboxes, class_ids, segmentation_countour_idx, scores = yolo_segmentation.run_yolo(img)
    #selects class name based on ID
    class_names = map(lambda num: classes[num], class_ids)
   
    class_names_count = {}
    # print(F"class_names_count {class_names_count}")
    img_insights = {}
    img_insights.setdefault('num_objects', len(bbboxes))
    img_insights.setdefault('class_conf_bb_seg', {})
    count = 1
    for bbox, class_id, segmentation_countour_idx, score in zip(bbboxes, class_ids, segmentation_countour_idx, scores):
        poly = geometry.Polygon(segmentation_countour_idx)
        area = poly.area
        area /= img_area #normalizing the area
        print(bbox, file=open('innerloop_bbox.txt', 'a'))
        # print("classes keys", classes.keys())
        # reducing confidence will make aws throw this error
        #Exception Value:RequestError(400, 'illegal_argument_exception', 'Limit of total fields [1000] has been exceeded')
        if class_id in classes.keys():
            class_name = classes[class_id]
            if class_names_count.get(class_name) == None:
                class_names_count.setdefault(class_name, 1)
            else:
                class_names_count[class_name] +=1
            
            #if the class already exist, append count to it
            if img_insights['class_conf_bb_seg'].get(class_name) != None:
            # print("found", classes[class_id])
                img_insights['class_conf_bb_seg'].setdefault(f"{class_name}_{count}", [{'confidence': score, 'area': area, 'bb': bbox, 'seg': segmentation_countour_idx}])
                count+=1
            else:
                img_insights['class_conf_bb_seg'].setdefault(f"{class_name}", [{'confidence': score, 'area': area, 'bb': bbox, 'seg': segmentation_countour_idx}])

    return (img_insights, class_names_count)