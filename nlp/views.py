from django.shortcuts import redirect, render, HttpResponseRedirect, HttpResponse
from django.http.response import StreamingHttpResponse, JsonResponse
from .models import NLPCSV
from django.core.paginator import Paginator
from django.contrib import messages
import os
import glob
import pandas as pd

#api requirements
from rest_framework.views import APIView
from rest_framework.response import Response

from .utils import read_uploaded_csv, aws_get_sentiment, google_Analyze_Sentiment, run_jobs


parent_dir = os.getcwd()
media = os.path.join(parent_dir, 'media')
csv_dir = os.path.join(media, 'nlp_csv')




def nlp_app(request):
    context = {}
    return render(request, 'nlp/nlp_app.html', context)


def upload_nlp_csv(request):
    if request.method == 'POST':
        nlp_csv = request.FILES.get('uploadcsvfile')
        NLPCSV(uploaded_nlp_csv=nlp_csv).save()
        print(nlp_csv, 'saved')
    return redirect('nlp_app')

def view_uploaded_csv(request):
    """
    Function returns the uploaded CSV 
    """
    context = {}
    df = read_uploaded_csv(csv_dir)
    df = df[1:]
    paginator = Paginator(df, 20)
    page_number = request.GET.get('page')
    csv_rows = paginator.get_page(page_number)
    # print(df)
    context['csv_rows'] = csv_rows
    # print(context['df'])

    return render(request, 'nlp/nlp_app.html', context)


def run_analysis(request, job=None):
   
    context = run_jobs()
    # text = str(new_df['text'])
    #response = google_Analyze_Sentiment(text)
    #response = aws_get_sentiment(text)
    return render(request, 'nlp/nlp_app.html', context)



