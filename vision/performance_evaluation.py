import pandas as pd
import matplotlib.pyplot as plt
from django.shortcuts import HttpResponse

import os
import glob

parent_dir = os.getcwd()
media = os.path.join(parent_dir, 'media')
test_csv_dir = os.path.join(media, 'test_csv')
csv_for_scores = os.path.join(media, 'csv_for_scores')
test_csv = os.path.join(media, 'test_csv')
test_images = os.path.join(media, 'test_images')
plot_figures = os.path.join(media, 'plot_figures')


def count_detection_per_image(image_list, csv_file, container, image_file_name, image_num):
    for image in image_list:
        image_name = os.path.basename(image)
        if image_name not in image_file_name:
            image_file_name.append(image_name)
        image = csv_file['imagefile'].value_counts()[image_name]

        container.append(image)
        image_num += 1


def plot_bar_chart(term):
    # term function is a string of - seperate values representing available platforms
    #gt = groundtruth
    glob.glob(f"{csv_for_scores}/*.csv")
    uploaded_image_list = glob.glob(f"{test_images}/*.jpg")
    platforms = term.split('-')
    image_file_name = []
    gt_values = []
    yolo_values = []
    aws_values = []
    for platform in platforms:
        if platform == 'gt':
            gt = os.path.join(test_csv, 'manual.csv')
            if os.path.isfile(gt):
                gt_detections = pd.read_csv(gt)
                image_num = 1
                count_detection_per_image(
                    uploaded_image_list, gt_detections, gt_values, image_file_name, image_num)

        elif platform == 'yolo':
            yolo = os.path.join(csv_for_scores, 'yolo_boxes.csv')
            if os.path.isfile(yolo):
                yolo_detections = pd.read_csv(yolo)
                image_num = 1
                count_detection_per_image(
                    uploaded_image_list, yolo_detections, yolo_values, image_file_name, image_num)

        elif platform == 'aws':
            aws = os.path.join(csv_for_scores, 'aws_boxes.csv')
            if os.path.isfile(aws):
                aws_detections = pd.read_csv(aws)
                count_detection_per_image(
                    uploaded_image_list, aws_detections, aws_values, image_file_name, image_num)

    working_df = pd.DataFrame({
        "image file": image_file_name,
        "Ground Truth": gt_values,
        "Yolo": yolo_values,
        "aws": aws_values
    }, index=image_file_name)
    working_df.plot(kind='bar', figsize=(15, 8))
    plt.xticks(rotation=0, horizontalalignment="center")
    plt.xlabel('image file')
    plt.ylabel('Number of Persons Detected')
    plt.title('Object Detection Summary')
    plt.savefig(os.path.join(plot_figures, 'performance_bar_chart.png'))

    print(f'Ploting bar chart for platform {platforms[0]}, {platforms[1]}===>')
    return HttpResponse("hehehe")
