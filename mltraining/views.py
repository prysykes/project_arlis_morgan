from django.shortcuts import render, redirect

from django.core.files.base import ContentFile


from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.views import View
from mltraining.models import IAMRole, NotebookInstance, Predictions, Training
import time, datetime, os, json, pathlib, shutil
from .aws import create_iam_role, create_notebook_instance, check_notebook_instance, get_notebook_instance, stop_notebook_instance, delete_notebook_instance, get_notebook_instance_jupyterlab_url, upload_to_s3, create_lifecycle_config, upload_folder_to_s3, delete_s3_directory, download_dataset
from .utils import create_lc_scripts_for_user, extract_metadata, extract_dataset
from django.utils import timezone
from django.contrib import messages
import mltraining.transferlearning as tfl


import pandas as pd
import boto3

# Create your views here.

cred_pad = '/Users/prynet/Documents/aws_cred/emeka_accessKeys.csv'
df = pd.read_csv(cred_pad)
#print(df.columns)
access_key_id = df.loc[df.index[0], 'Access key ID'] #df.index[0] returns first row, second argument is the column name 

secret_key_id = df.loc[df.index[0], 'Secret access key']


class NotebookStatusView(View):
    def get(self, request):
        try:
            notebook = NotebookInstance.objects.get(instance_name=f"notebook-instance-{request.user.username}")
            status = notebook.instance_status

            now = timezone.now()
            if notebook.start_time is not None:
                time_in_service = now - notebook.start_time
            else:
                time_in_service = 0
        except NotebookInstance.DoesNotExist:
            status = "Instance does not exist"
            time_in_service = 0
        except Exception as e:
            status = f"An error occurred: {e}"
            time_in_service = 0

        try:
            training = Training.objects.get(user=request.user)
            training_status = training.training_status
        except Training.DoesNotExist:
            training_status = "Not Started"
        print(training_status)
        
        return JsonResponse({'status': status, 'time_in_service': time_in_service, 'training_status': training_status})



def mltraining(request):
    user = request.user
    print(user)
    iam_role = IAMRole.objects.filter(user=user).first()
    #print(iam_role.role_name)
    
    if not iam_role:
        print("I am role not found.. creating")
        role_name="SagemakerRoleFor"+str(user)
        arn = create_iam_role(user, role_name)       
                
        iam_role = IAMRole.objects.create(user=user, role_arn=arn, role_name=role_name)
    note_note = len(NotebookInstance.objects.filter(user=user))
    print("***Instance Status***", note_note)
    instance = NotebookInstance.objects.filter(user=user).first()    
    if instance:
        instance_status = instance.instance_status
        instance_exists = True
        
    else:
        instance_status = "Notebook instance does not exist"
        instance_exists = False
       
    latest_predictions = Predictions.objects.filter(user=user).order_by('-id')[:10]

    training_obj = Training.objects.filter(user=user).first()

    if training_obj:
        metadata = training_obj.dataset_metadata
        model_summary = training_obj.model_summary
    else:
        metadata = None


    context = {
        'iam_role_exists': True,
        'iam_role': iam_role.role_name,
        'instance_exists': instance_exists,
        'instance_status': instance_status,
        'latest_predictions': latest_predictions,
        'metadata': metadata,
        # 'model_summary': model_summary,
    }
    return render(request, 'mltraining/mltraining.html', context)

def launch_instance(request):
    iam_role = IAMRole.objects.filter(user=request.user).first()
    role_arn = iam_role.role_arn
    if not iam_role:
        return render(request, 'mltraining.html', {'error_message': "IAM role does not exist"})
    
    create_lc_scripts_for_user(request.user.username)
    folder_path = os.path.join(os.getcwd()+"/mltraining/", request.user.username)
    # print("folder000", folder_path)
    upload_folder_to_s3('mlwb-scripts', folder_path)
    print("***uploaded s3***")
    script_path = os.path.join(folder_path, "generic_lifecycle_config.sh")
    print("***script Path***")
    create_lifecycle_config(script_path, request.user.username+"-lc-config")
    print("***create_lifecycle_config***")

    
    instance_name = f"notebook-instance-{request.user.username}"
    
    # on_create_key, on_start_key = create_lifecycle_configs(request.user.username)
    role_arn = role_arn 
    print(f"role arn inside launch \t {role_arn}")
    # role_arn = "arn:aws:iam::687069121510:role/service-role/AmazonSageMaker-ExecutionRole-20230221T113819"
    instance_arn = create_notebook_instance(instance_name, 'ml.t2.medium', request.user.username+"-lc-config", role_arn)
    print(instance_arn)
    instance, created = NotebookInstance.objects.update_or_create(
        user=request.user,
        defaults={'instance_name': instance_name, 'instance_arn': instance_arn, 'instance_status': 'Pending'}
    )

    # start_time = time.time()
    # 

    cnt = 0
    while True:
        status = check_notebook_instance(instance_name) 
        if status == 'InService':
            instance.start_time = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f')
            
            break
        print(status)
        instance.instance_status = status+ "..."+str(cnt)
        
        
        instance.save()
        time.sleep(2)
        cnt+=1

        
    instance_response = get_notebook_instance(instance_name)
    instance.instance_status = 'In Service'
    instance.instance_url = instance_response['Url']
    instance.save()
    
    return redirect('mltraining')

def delete_instance(request):
    notebook = NotebookInstance.objects.filter(user=request.user).first()
    if notebook:
        stop_notebook_instance(notebook.instance_name)
        notebook.instance_status = "Stopping"
        messages.success(request, "Notebook instance is stopping.")
    else:
        messages.error(request, "Notebook instance not found.")

    cnt = 0
    while True:
        status = check_notebook_instance(notebook.instance_name) 
        if status == 'Stopped':
            delete_notebook_instance(notebook.instance_name)            
            break
        print(status)
        notebook.instance_status = status+ "..."+str(cnt)
        
        
        notebook.save()
        time.sleep(2)
        cnt+=1

    notebook.delete()
    
    return redirect('mltraining')


def open_jupyterlab(request):
    notebook_instance = NotebookInstance.objects.filter(user=request.user).first()
    if notebook_instance:
        jupyterlab_url = get_notebook_instance_jupyterlab_url(notebook_instance.instance_name)
        print(jupyterlab_url)
        if jupyterlab_url:
            return HttpResponseRedirect(jupyterlab_url)
        else:
            # JupyterLab URL not found
            return JsonResponse({'error': 'JupyterLab URL not found.'})
    else:
        # Notebook instance not found
        return JsonResponse({'error': 'Notebook instance not found.'})


def upload_file(request):
    if request.method == 'POST':
        user = request.user.username
        uploaded_file = request.FILES['file']
        filename = uploaded_file.name
        success, msg = upload_to_s3(uploaded_file, user, filename, 'mlwb-nbks')
        print("file upload...")
        print(success)
        print(msg)

        if success:
            return redirect('mltraining')
        else:
            # handle file upload failure
            print("file upload failed...")

    return redirect('mltraining')


def classify_images(request):
    user = request.user.username
    if request.method == 'POST' and request.FILES.getlist('images'):
        images = request.FILES.getlist('images')

        # Determine which classifier to use based on the selected form field
        classifier = request.POST.get('classifier')
        if classifier == 'classifier1':
            print("pretrained model call")
            # Load first trained model and image labels
            IMAGE_SHAPE = (224, 224)
            model = tfl.create_classifier(IMAGE_SHAPE)
            input_file = os.path.join(os.getcwd()+"/mltraining/", "imagenet_classes.txt")
            image_labels = tfl.load_image_labels(input_file)
        elif classifier == 'classifier2':
            print("transfer learning model call")
            training = Training.objects.filter(user=request.user).first()
            model_path = training.model_dir
            # Load second trained model and image labels
            IMAGE_SHAPE = (224, 224)
            model = tfl.create_classifier2(IMAGE_SHAPE, model_path)
            print(model.summary())
            input_file = os.path.join(os.getcwd()+"/mltraining/", user + "-model/tfl_classes.txt")
            print(input_file)
            image_labels = tfl.load_image_labels(input_file)
        else:
            # Handle invalid classifier selection
            return HttpResponseBadRequest("Invalid classifier selected")

        # Delete existing predictions
        Predictions.objects.filter(user=request.user).delete()


        for image in images:
            # Preprocess image
            image_arr = tfl.preprocess_image(image, IMAGE_SHAPE)

            # Get predicted label
            predicted_label_index = tfl.predict_label(model, image_arr)
            print(predicted_label_index)
            predicted_label = image_labels[predicted_label_index]

            # Create the Predictions object with the user field set to the current user
            prediction = Predictions(user=request.user, image=image, predicted_label=predicted_label)
            prediction.save()

        # Redirect to the mltraining view
        return redirect('mltraining')

    # Render the form for selecting the classifier
    return redirect('mltraining')


def upload_dataset(request):
    if request.method == 'POST':
        user = request.user.username
        uploaded_file = request.FILES['file']
        filename = uploaded_file.name

        # Delete existing instance
        Training.objects.filter(user=request.user).delete()

        # Extract metadata
        metadata = extract_metadata(uploaded_file)
        print(metadata)

        # Reset the file pointer to the beginning of the file
        uploaded_file.seek(0)

        delete_s3_directory('mlwb-datasets', user)
        # Upload dataset file
        print(uploaded_file.size)
        success, dataset_msg = upload_to_s3(uploaded_file, user, 'data.tar.gz', 'mlwb-datasets')
        print("file upload...")
        print(success)
        print(dataset_msg)
        print(filename)

        obj, created = Training.objects.update_or_create(user=request.user, dataset_metadata=metadata)       

        obj.save()

        if success:
            return redirect('mltraining')
        else:
            # handle file upload failure
            print("file upload failed...")

    return redirect('mltraining')


def start_transfer_learning(request):
    user = request.user.username
    dataset_dir = os.path.join(os.getcwd() + "/mltraining/", user + "-dataset")
    model_path = os.path.join(os.getcwd() + "/mltraining/", user + "-model")

    training = Training.objects.filter(user=request.user).first()
    training.training_status = "Starting Transfer Learning ..."
    training.save()

    # Delete the dataset_dir and model_path if they exist
    if os.path.exists(dataset_dir):
        shutil.rmtree(dataset_dir)
    if os.path.exists(model_path):
        shutil.rmtree(model_path)

    os.makedirs(dataset_dir)
    

    
    metadata = {item[0]: item[1] for item in training.dataset_metadata}
    print(metadata)

    training.training_status = "Getting dataset from cloud storage ..."
    training.save()

    # Download the dataset from S3 once
    s3_object_key = f"{user}/data.tar.gz"
    local_dataset_file = f"{dataset_dir}/data.tar.gz"
    download_dataset("mlwb-datasets", s3_object_key, local_dataset_file)

    # Extract the dataset for each label
    for label in metadata:
        label_dir = os.path.join(dataset_dir, label)
        if not os.path.exists(label_dir):
            os.makedirs(label_dir)

        extract_dataset(dataset_dir, label_dir, label)

    # Delete the data.tar.gz file
    os.remove(local_dataset_file)

    # Load the data and start training
    data_dir = pathlib.Path(dataset_dir)
    X_train_scaled, X_test_scaled, y_train, y_test, num_classes, labels_dict, labels_dict_inv = tfl.load_data(data_dir)
    print(labels_dict)
    print(labels_dict_inv)

    # Save the classes to a text file
    classes_file = os.path.join(model_path, "tfl_classes.txt")
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    with open(classes_file, "w") as f:
        for i in range(num_classes):
            class_name = labels_dict_inv[i]
            f.write(class_name + "\n")


    training.training_status = "Build model and start training ..."
    training.save()

    model, model_summary, summary_path = tfl.build_model(num_classes, save_path=model_path)
    
    print(model_summary)

    epochs, validation_split = 10, 0.2
    test_loss, test_acc, elapsed_time = tfl.train_model(model, X_train_scaled, X_test_scaled, y_train, y_test, epochs, validation_split, save_path=model_path)

    # Save the model directory path and model_summary to the Training object in the database
    training.model_dir = model_path
    with open(summary_path, 'r') as f:
        summary_txt = f.read()
    training.model_summary = summary_txt

    training.training_status = "Training completed, TL model saved.\nTest Loss: "+str(test_loss)+". Test Accuracy: "+str(test_acc)+".\nTime elapsed for training: "+str(elapsed_time)+"secs" 
    training.save()

    
    return redirect('mltraining')