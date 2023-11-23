from django.shortcuts import redirect, render, HttpResponseRedirect, HttpResponse
from django.http.response import StreamingHttpResponse, JsonResponse
from .models import TempTestImagesCSV
from django.contrib import messages
import os
import glob


from .utils import calculate_f1_score

# from .yolo import open_cv_read_images

# from .rekognition import aws_read_images
from .performance_evaluation import plot_bar_chart

from yolov7.yolo_detect import yolo_detect, move_to_result_yolo_and_delete_folder

# from .utils_yolo import open_cv_read_images, calculate_f1_score_yolo


parent_dir = os.getcwd()
media = os.path.join(parent_dir, 'media')
test_images_dir = os.path.join(media, 'test_images')
test_csv_dir = os.path.join(media, 'test_csv')
yolo_result = os.path.join(media, 'result_yolo')
aws_result = os.path.join(media, 'result_aws')
csv_files = os.path.join(media, 'csv_for_scores')

yolov7 = os.path.join(parent_dir, 'yolov7')
plot_figures = os.path.join(media, 'plot_figures')
bar_plot_fig = os.path.join(plot_figures, 'performance_bar_chart.png')



# Create your views here.


def vision_app(request):
    context = {"name": "Chukwuemeka Duru"}
    return render(request, 'vision/vision_app.html', context)

def poll_upload_action(request, csvfile_list, imgfiles):
    if csvfile_list == 0:
        messages.info(request,  "Ground Truth CSV file Missing ... ")
    if len(imgfiles) == 0:
        messages.error(request, "You can't run the vission app without Test Images. Please upload Test Image(s)")
        return redirect(request.META.get('HTTP_REFERER'))
    csvfile_name = os.path.basename(csvfile_list[0])
    print(csvfile_name)
    os.rename(f'{test_csv_dir}/{csvfile_name}', f'{test_csv_dir}/manual.csv')
    messages.info(request, f"Your Ground Truth File: {csvfile_name} was successfully uploaded and renamed as manual.csv")
    
    for i, img in enumerate(imgfiles):
        TempTestImagesCSV(test_images_file=img).save()
        messages.info(request, f"image - {i} - {img} - Uploaded")
    return redirect('vision_app')
    

def upload_images_csv(request):
    images_list = glob.glob(f"{test_images_dir}/*.jpg") #this returns a list
    csvfile_list = glob.glob(f"{test_csv_dir}/*.csv")
    print(len(csvfile_list))
    if len(images_list) != 0:
        os.chdir(test_images_dir)
        for img in images_list:
            img_name = os.path.basename(img)
            os.remove(img_name)
        os.chdir(parent_dir) 
    
    if len(csvfile_list) != 0:
        os.chdir(test_csv_dir)
        for csv in csvfile_list:
            csv_name = os.path.basename(csv)
            print(csv_name)
            
        os.chdir(parent_dir)

    if request.method == 'POST':
            csvfile = request.FILES.get('uploadcsvfile')
            print(csvfile)
            imgfiles = request.FILES.getlist('uploadimgfiles')
            TempTestImagesCSV(test_csv_file=csvfile).save()
            csvfile_list = glob.glob(f"{test_csv_dir}/*.csv")
            return poll_upload_action(request, csvfile_list, imgfiles)
    
    return redirect('vision_app')


def view_uploaded_images(request):
    context = {'images': []}
    images_list = glob.glob(f"{test_images_dir}/*.jpg")
    if len(images_list) == 0:
        messages.error(request, "There are no images available. Please upload some to continue.")
        return redirect(request.META.get('HTTP_REFERER'))
    for img in images_list:
        image_name = os.path.basename(img)
        print(image_name)
        context['images'].append(image_name)
    # context_json = json.dumps(context, indent=)
    print(context)
    return JsonResponse(context, safe=False)


def view_bar_plot(request):
    context = {}
    bar_plot_img = os.path.basename(bar_plot_fig)
    print(context)
    context['bar_plot'] = bar_plot_img
    return JsonResponse(context, safe=False)


def read_yolo_result(request):
    context = {'images_with_box': []}
    images_with_boxes = glob.glob(f"{yolo_result}/*.jpg")
    if len(images_with_boxes) != 0:
        for img in images_with_boxes:
            image_name = os.path.basename(img)
            context['images_with_box'].append(image_name)
        print(context)
    return JsonResponse(context, safe=False)

def read_aws_result(request):
    context = {'images_with_box': []}
    images_with_boxes = glob.glob(f"{aws_result}/*.jpg")
    if len(images_with_boxes) != 0:
        for img in images_with_boxes:
            image_name = os.path.basename(img)
            context['images_with_box'].append(image_name)
        print(context)
    return JsonResponse(context, safe=False)


# def run_detection(request, caller="workbench", **kwargs):
    
    
#     # if request.GET.get('term') == 'yolo-aws':
#     #     print("Running Detection on all Platforms ===>")
#     #     open_cv_read_images(test_images_dir, term)
#     #     aws_read_images(test_images_dir, term)
#     # elif request.GET.get('term') == 'yolo':
#     #     print("yes - yolo")
#     #     open_cv_read_images(test_images_dir, term)
#     # elif request.GET.get('term') == 'aws':
#     #     print('yes-aws')
#     #     aws_read_images(test_images_dir, term)
#     # elif request.GET.get('term') == 'google':
#     #     print('yes-google')
#     print(caller)
#     if caller == 'workbench':
#         print(caller)
#         term = request.GET.get('term')
#         # print("termType:", type(term))
#         terms = term.split('-')
#         yolo_detect(test_images_dir, terms[0])
#         move_to_result_yolo_and_delete_folder()
#         aws_read_images(test_images_dir, terms[1])
#         return redirect('vision_app')
    
#     elif caller == "yolo-aws":
#         print(caller)
#         # term_api = request.GET.get('term_api')
#         # print("termType:", type(term))
#         term_api = caller.split('-')
#         print("term_ api:", term_api)
#         yolo_detect(test_images_dir, term_api[0])
#         move_to_result_yolo_and_delete_folder()
#         # aws_read_images(test_images_dir, term_api[1])
#         return redirect('/')
    
#     elif caller == 'meta_data_api':
#         current_image = kwargs['current_image']
#         print("current_image =", kwargs['current_image'])
#         # context = aws_read_images(current_image, caller)
#         context = {}
#         return context
        


def evaluate_performance(request):
    term = request.GET.get('term')
    plot_bar_chart(term)
    return redirect('vision_app')
     

def f1_score(request):
    context = {}
    calculate_f1_score(test_images_dir, csv_files)
    # context = score_yolo
    # return JsonResponse(context, safe=False)


    
