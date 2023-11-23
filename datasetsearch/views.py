import os
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils_kaggle import search_kaggle, download_dataset_kagle, retrieve_datasets_kaggle
from .utils_uci import scrap_uci, uci_download_dataset, load_json, retrieve_dataset_uci
from .utils_s3 import retrieve_files_from_userS3



parent_dir = os.getcwd()
uci_dataset = "uci_dataset"
path_to_static = os.path.join(parent_dir, 'static') 
download_full_path = os.path.join(path_to_static, 'uci_datasett')

def search_dataset(request):
    os.chdir(parent_dir)
    context = {}

    if request.method == "POST":
        searchkey = request.POST["searchkey"].lower()
        # if " " in searchkey:
        #     messages.error(request, "Keyword should be single words eg: fraud, cat, anomaly")
        #     return redirect('/')
        dtsite = request.POST["dtsite"] 
        #this captures the name of the select button
        # the current value of the select button is the repo to be queried
        if searchkey != "":
            #checks the select button to know the exact repo chosen by the user
            if dtsite == "kaggle":

                results = search_kaggle(searchkey)

                context['results'] = results
                # use this to know the tabe to render
                context['owner'] = dtsite.upper() + " "
                context['lenresults'] = len(results)
                return render(request, 'datasetsearch/dataset_results_kaggle.html', context)

            if dtsite == "datagov":
                context['owner'] = dtsite

            if dtsite == "uci":
                results = {}
                result_key = 0
                try:
                    initial_results = load_json()
                    for dataset in initial_results.values():
                        for item in dataset:
                            if searchkey in item.lower():
                                if dataset in results.values():
                                    continue  # making sure the returned result is unique
                                else:

                                    results[str(result_key)] = dataset
                                    result_key += 1

                    # results = scrap_uci(searchkey)
                    # print("my type", type(results))
                    context['results'] = results
                    context['len_results'] = len(results)
                    context['owner'] = dtsite.upper() + " "
                except FileNotFoundError:
                    context['owner'] = dtsite.upper() + " "
                return render(request, 'datasetsearch/dataset_results_uci.html', context)

            if dtsite == "googlepd":
                context['owner'] = dtsite.upper() + " "

            if dtsite == "federated":
                result_uci_key = 0
                result_key = 0
                initial_results_uci = load_json()  # this returns a JSON dictionary
                # this retunrs a list of strings
                results_kaggle = search_kaggle(searchkey)

                federated_results = {}  # stores result of federated search
                context['owner'] = dtsite.upper() + " "

                # this retuned a list
                print("kaggle type", type(results_kaggle))
                if len(results_kaggle) != 0:

                    for item in results_kaggle[1:]:
                        federated_results[str(result_key)+"#Kaggle"] = item
                        result_key += 1

                if len(initial_results_uci.keys()) != 0:
                    for dataset in initial_results_uci.values():
                        for item in dataset:
                            if searchkey in item.lower():
                                federated_results[str(
                                    result_key)+"#UCI"] = dataset
                                result_key += 1

                print("my_federted results: ", federated_results.items())
                # results = scrap_uci(searchkey) # we will use this in the second phase
                context['federated_results'] = federated_results.items()
                # print(f"UCI: {results_uci['0']} ==== \n Kaggle {results_kaggle[1]} ==== \n {federated_results[0]} ")
                context['len_federated_results'] = len(federated_results)
                context['owner'] = dtsite.upper() + " "
                return render(request, 'datasetsearch/dataset_results_federated.html', context)

        else:
            messages.error(request, " You must select a dataset name!")

    return render(request, 'datasetsearch/dataset_results_kaggle.html', context)

def view_dataset_kaggle(request):
    bucket= 'mlwb-datasets'
    user = str(request.user)
    context = retrieve_files_from_userS3(user, bucket)# retrieves the dataset belonging to a user
   # context['owner'] = 'kaggle'
    # print("printing_S3 content", context)
    return render(request, 'datasetsearch/view_dataset.html', context)

def view_dataset_uci(request):
    user = request.user
    context = retrieve_dataset_uci(user) 
    context['owner'] = 'UCI'
    return render(request, 'datasetsearch/view_dataset.html', context)
    

def download_dataset(request):
    user = request.user
    if request.method == "GET":
        term = request.GET.get('term')
    datasets = download_dataset_kagle(term, user)
    context = datasets
    
    return render(request, 'datasetsearch/view_dataset.html', context)


def dataset_list(request):
    user = request.user
    context = retrieve_datasets(user, dir=None)
    #do we need to save dataset for the
    

    return render(request, 'datasetsearch/dataset_list.html', context)


def downlaod_dataset_uci(request):
    
    user = request.user
    if request.method == "GET":
        term = request.GET.get('term')
    
    uci_download_dataset(term, user, request)
    
    context = {'term': term}
    
    return render(request, 'datasetsearch/view_dataset.html', context)
