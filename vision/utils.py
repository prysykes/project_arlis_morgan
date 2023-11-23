import pandas as pd
import cv2
import numpy as np
import os
import csv
import glob


parent_dir = os.getcwd()
media = os.path.join(parent_dir, 'media')
test_images_dir = os.path.join(media, 'test_images')
test_csv_dir = os.path.join(media, 'test_csv')
yolo_result = os.path.join(media, 'result_yolo')
csv_for_scores = os.path.join(media, 'csv_for_scores')



yolo_config = os.path.join(parent_dir, 'yolo_config')
yolo_v3_weights = os.path.join(yolo_config, 'yolov3.weights')
yolo_v3_config = os.path.join(yolo_config, 'yolov3.cfg')
coco_name = os.path.join(yolo_config, 'coco.names')


def create_csv(box_for_csv, csv_path):
    csv_header = ['imagefile', 'personid', 'confidence', 'width', 'height', 'left', 'top']
    print("csv_path", csv_path)
    #print(f"IMAGENAME: {image_name+'.jpg'} \n left: {x/width} \n top: {y/height} \n width: {wt/width} \n height: {ht/height}")
    with open(csv_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(csv_header)
        writer.writerows(box_for_csv)
        

    #print("manic", image_name)
    
    # if os.path.isfile(yolo_boxes_csv):
    #     x, y, wt, ht = boxes[i]
        
    #         #
        
    #     print(f"left: {x/width} \n top: {y/height} \n width: {wt/width} \n height: {ht/height}")
            
    # else:
    #     pass
    # print("checking", os.path.isfile(yolo_boxes_csv))
    
    # csv = os.path.join(yolo_tp_fp_result, 'tp_fp.csv')
    # TP = boxes_tp_count
    # FP = boxes_fp_count
    
    
    # dict_to_csv = {"imagefile": image_name+".jpg", 'TP': [TP], 'FP': [FP]}
    # df = pd.DataFrame(dict_to_csv)
    
    # df.to_csv(csv, mode='a', index=False, header=False)

def score_processing(img, TP, Aovlp, area_gt, ElimList, row, bb_box_file):
    
    for yindex, yrow in bb_box_file.iterrows():
        if yrow['imagefile'] == img and yindex not in ElimList:
            if yrow['top']>row['top'] and yrow['top']<row['top']+row['height']:
                if yrow['left']>row['left'] and yrow['left']<row['left']+row['width']:
                    Aovlp=min(yrow['width'],(row['width']-(yrow['left']-row['left'])))*min(yrow['height'],(row['height']-(yrow['top']-row['top'])))
                if row['left']>yrow['left'] and row['left']<yrow['left']+yrow['width']:
                    Aovlp=((yrow['width']-(row['left']-yrow['left'])))*((row['height']-(yrow['top']-row['top'])))
            if row['top']>yrow['top'] and row['top']<yrow['top']+yrow['height']:
                if yrow['left']>row['left'] and yrow['left']<row['left']+row['width']:
                    # Aovlp=min(yrow['width'],(row['width']-(yrow['left']-row['left'])))*min(yrow['height'],(row['height']-(yrow['top']-row['top'])))
                    Aovlp=((row['width']-(yrow['left']-row['left'])))*((yrow['height']-(row['top']-yrow['top'])))
                if row['left']>yrow['left'] and row['left']<yrow['left']+yrow['width']:
                    # Aovlp=((yrow['width']-(row['left']-yrow['left'])))*((row['height']-(row['top']-yrow['top'])))
                    Aovlp=min(row['width'],(yrow['width']-(row['left']-yrow['left'])))*min(row['height'],(yrow['height']-(row['top']-yrow['top'])))
        
        if Aovlp > area_gt*0.8:
            TP+=1                                   
            # print(Atruth)
            # print(Aovlp)
            # print(yrow['imagefile']+' check yolo')
            # print(yrow['height'])
            print("inner TP", TP)
            print("inner Aovlp", Aovlp)
            ElimList.append(yindex)
            break


def calculate_f1_score(test_imgdir, csv_files):
    imglist = os.listdir(test_imgdir)
    csv_file_list = glob.glob(f"{csv_files}/*.csv")
    print("F1 score started")
    dfgtruth = pd.read_csv(os.path.join(csv_files, 'manual.csv'))
    dfyolo = pd.read_csv(os.path.join(csv_files, 'manual.csv'))
    dfaws = None
    # print("Before", dfgtruth, dfyolo, dfaws)
    # for csv_file in csv_file_list:
    #     if os.path.isfile(csv_file) and os.path.basename(csv_file) == 'manual.csv':
    #         dfgtruth = pd.read_csv(csv_file)
    #     elif os.path.isfile(csv_file) and os.path.basename(csv_file) == 'yolo_boxes.csv':
    #         dfyolo = pd.read_csv(csv_file)
    #     elif os.path.isfile(csv_file) and os.path.basename(csv_file) == 'aws_boxes.csv':
    #         dfaws = pd.read_csv(csv_file)
    
    
    TParr = []
    TPimg = []
    F1arr = [] # dictionary of f1 scores

    for img in imglist:
        TP = 0
        cv_img = cv2.imread(os.path.join(test_images_dir, img))
        ElimList = []
        for index, row in dfgtruth.iterrows():
            Aovlp = 0
            if row['imagefile'] == img:
                area_gt = row['height'] * row['width']
                # if type(dfyolo) != None:
                for yindex, yrow in  dfyolo.iterrows():
                    if yrow['imagefile'] == img and yindex not in ElimList:
                        if yrow['top']>row['top'] and yrow['top']<row['top']+row['height']:
                            if yrow['left']>row['left'] and yrow['left']<row['left']+row['width']:
                                Aovlp=min(yrow['width'],(row['width']-(yrow['left']-row['left'])))*min(yrow['height'],(row['height']-(yrow['top']-row['top'])))
                            if row['left']>yrow['left'] and row['left']<yrow['left']+yrow['width']:
                                Aovlp=((yrow['width']-(row['left']-yrow['left'])))*((row['height']-(yrow['top']-row['top'])))
                        if row['top']>yrow['top'] and row['top']<yrow['top']+yrow['height']:
                            if yrow['left']>row['left'] and yrow['left']<row['left']+row['width']:
                                # Aovlp=min(yrow['width'],(row['width']-(yrow['left']-row['left'])))*min(yrow['height'],(row['height']-(yrow['top']-row['top'])))
                                Aovlp=((row['width']-(yrow['left']-row['left'])))*((yrow['height']-(row['top']-yrow['top'])))
                            if row['left']>yrow['left'] and row['left']<yrow['left']+yrow['width']:
                                # Aovlp=((yrow['width']-(row['left']-yrow['left'])))*((row['height']-(row['top']-yrow['top'])))
                                Aovlp=min(row['width'],(yrow['width']-(row['left']-yrow['left'])))*min(row['height'],(yrow['height']-(row['top']-yrow['top'])))
                    
                    if Aovlp > area_gt*0.8:
                        TP+=1                                   
                        # print(Atruth)
                        # print(Aovlp)
                        # print(yrow['imagefile']+' check yolo')
                        # print(yrow['height'])
                        print("inner TP", TP)
                        print("inner Aovlp", Aovlp)
                        ElimList.append(yindex)
                        break
    

            
        print(TP)
        TParr.append(TP)
        TPimg.append(img)
        FN = len(dfgtruth[(dfgtruth['imagefile']==img)])-TP
        FP = len(dfyolo[(dfyolo['imagefile']==img)])-TP
        #print(FN)
        #print(FP)
        F1 = TP / (TP + (FP + FN)/2)
        #print(F1)
        F1arr.append(F1)
    print("TParr", TParr)
    print("TPomg", TPimg)
    print("F1 arr", F1arr) 
    


    # grndth_csv = os.path.join(test_csv_dir, 'manual.csv' )
    # df_grndth_csv = pd.read_csv(grndth_csv)
    # scores_csv_list = glob.glob(f"{csv_for_scores}/*.csv")
    # for i, truthrow in df_grndth_csv.iterrows():
    #     #print("gtruth", truthrow['imagefile'])
    #     #print(i, row)
    
    #     for csv in scores_csv_list:
    #         if os.path.basename(csv).split('.')[0] == "yolo_boxes":
    #             yolo_boxes_csv = os.path.join(csv_for_scores, 'yolo_boxes.csv')
    #             df_yolo_boxes_csv = pd.read_csv(yolo_boxes_csv)
    #             #print(truthrow['imagefile'])
    #             for i, yolorow in df_yolo_boxes_csv.iterrows():
                    
    #                 if yolorow['imagefile'] == truthrow['imagefile']:
                        
    #                     print("yolo", yolorow['imagefile'])
        
    