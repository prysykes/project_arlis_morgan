import pandas as pd
import cv2
import numpy as np
import os
import glob

from .utils import create_csv

parent_dir = os.getcwd()
media = os.path.join(parent_dir, 'media')
test_images_dir = os.path.join(media, 'test_images')
test_csv_dir = os.path.join(media, 'test_csv')
yolo_result = os.path.join(media, 'result_yolo')
aws_result = os.path.join(media, 'result_aws')
yolo_tp_fp_result = os.path.join(test_csv_dir, 'yolo_tp_fp_result')
csv_for_scores = os.path.join(media, 'csv_for_scores')


yolo_config = os.path.join(parent_dir, 'yolo_config')
yolo_v3_weights = os.path.join(yolo_config, 'yolov3.weights')
yolo_v3_config = os.path.join(yolo_config, 'yolov3.cfg')
coco_name = os.path.join(yolo_config, 'coco.names')


classes = []

font = cv2.FONT_HERSHEY_PLAIN

with open(coco_name, 'r') as f:
    classes = [line.strip() for line in f.readlines()]

def net_set_input(blob, weights, config):
    net = cv2.dnn.readNet(weights, config)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i-1] for i in net.getUnconnectedOutLayers()]
    net.setInput(blob)
    outs = net.forward(output_layers)
    return outs

box_for_csv_aws = []
box_for_csv_yolo = []
    
def draw_box_and_save_image(my_img, boxes, confidences, image_name, height, width, csv_path, term,  class_ids=None):
    terms = term.split('-')
    
    
    if term == 'yolo':
        # print("boxess", boxes)
        # print("termmm", term)
        
        
        """
            prior to the line below, detections made were overlapping. 
            This function improves detection acuracy by reducing overlapping
            NMS NonMassSeperation 
        """
        # print("csv path", csv_path)
        # print("term term", term)
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        number_of_persons_detected = len(boxes)
        personid = 1
        for i in range(number_of_persons_detected):
            
            #gets the bounding box for each detection and draws same on each image
            
            if i in indexes:
                
                x, y, wt, ht = boxes[i]
                
                label = classes[class_ids[i]]
                #
                cv2.rectangle(my_img, (x, y), (x + wt, y + ht), (0, 255, 0), 2)
                # creating left, top width and height for f1 score calculation
                left = x/width
                top = y/height 
                width_box_for_csv = wt/width 
                height_box_for_csv = ht/height
                person_detail = [image_name+'.jpg', personid, round(confidences[i]*100, 5), round(width_box_for_csv, 5), round(height_box_for_csv, 5), round(left, 5), round(top, 5)]
                personid += 1
                
                box_for_csv_yolo.append(person_detail)
                
                
                cv2.putText(my_img, label, (x, y + 20), font, 1, (255, 255, 255), 2)
                cv2.putText(my_img, str(round(confidences[i]*100, 3)), (x, y + 40), font, 1, (255, 255, 255), 2)
        create_csv(box_for_csv_yolo, csv_path)
        os.chdir(yolo_result)
        cv2.imwrite(f"{image_name}.jpg", my_img)
        os.chdir(parent_dir)
    elif term == 'aws':
        # print("boxess", boxes)
        # print("termmm", term)
        """
            prior to the line below, detections made were overlapping. 
            This function improves detection acuracy by reducing overlapping
            NMS NonMassSeperation 
        """
        # print("csv path", csv_path)
        # print("term term", term)
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        number_of_persons_detected = len(boxes)
        personid = 1
        for i in range(number_of_persons_detected):
            
            #gets the bounding box for each detection and draws same on each image
            
            if i in indexes:
                
                x, y, wt, ht = boxes[i]
                
                label = classes[class_ids[i]]
                #
                cv2.rectangle(my_img, (x, y), (x + wt, y + ht), (0, 255, 0), 2)
                # creating left, top width and height for f1 score calculation
                left = x/width
                top = y/height 
                width_box_for_csv = wt/width 
                height_box_for_csv = ht/height
                person_detail = [image_name+'.jpg', personid, round(confidences[i]*100, 5), round(width_box_for_csv, 5), round(height_box_for_csv, 5), round(left, 5), round(top, 5)]
                personid += 1
                
                
                box_for_csv_aws.append(person_detail)
                
                
                cv2.putText(my_img, label, (x, y + 20), font, 1, (255, 255, 255), 2)
                cv2.putText(my_img, str(round(confidences[i]*100, 3)), (x, y + 40), font, 1, (255, 255, 255), 2)
        
        create_csv(box_for_csv_aws, csv_path)
        os.chdir(aws_result)
        cv2.imwrite(f"{image_name}.jpg", my_img)
        os.chdir(parent_dir)
    
    
    
    # print("boxes for csv", box_for_csv)
    
    
def generate_boxes_class_confidence(outs, my_img, height, width, image_name, term):
    """
    personid = 1
         persons = []
    print(f"left: {x/width} \n top: {y/height} \n width: {wt/width} \n height: {ht/height}")
            pers_box = {}
            pers_box['imagefile'] = image_name+'.jpg'
    """
    class_ids = []
    boxes = [] 
    # boxes_tp_count = 0  #len(boxes) = TP
    # boxes_fp_count = 0  #confidence output of 0.1 --> 0.49    
    confidences = []
    
    for out in outs: # outs has three channel detection
        
        for detection in out:
            
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if (confidence > 0.5) and (classes[class_id] == 'person'):
                # boxes_tp_count += 1
                #this makes sure that only persons are detected. 
                # We can modify same for object or anything esle
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                wt = int(detection[2] * width)
                ht = int(detection[3] * height)
                #recatngle cordinates for bounding boxes
                x = int(center_x - wt/2) #xc
                y = int(center_y - ht/2) #yc
                #create bounding boxes for each person detected for a particualr image
                boxes.append([x, y, wt, ht]) 
                
                confidences.append(float(confidence))
                class_ids.append(class_id)
                
    yolo_boxes_csv = os.path.join(csv_for_scores, 'yolo_boxes.csv')              
    draw_box_and_save_image(my_img, boxes, confidences, image_name, height, width, yolo_boxes_csv, term, class_ids)
                
                


def open_cv_read_images(path, term):
    print("Running Yolo Detect ==>")
    weights = yolo_v3_weights
    config = yolo_v3_config
    images_list = glob.glob(f"{path}/*.jpg")
    for i, img in enumerate(images_list):
        
        image_name = os.path.basename(img).split('.')[0]
        # print("imagoloo", image_name)
        my_img = cv2.imread(img)
        height, width, _ = my_img.shape
        blob = cv2.dnn.blobFromImage(my_img, 1/255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
        outs = net_set_input(blob, weights, config)
        generate_boxes_class_confidence(outs, my_img, height, width, image_name, term)
        

cv2.waitKey(0)
cv2.destroyAllWindows()
