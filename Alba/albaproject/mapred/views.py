
from mapred.forms import LoginForm, JobForm
from mapred.models import Job, Server
from mapred.objects import OSFlavor
from mapred import compute
from mapred.process import run_mapred_job

from albaproject.settings import MEDIA_ROOT

from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.shortcuts import Http404
from django.http import HttpResponse
from django.core.files import File

import pdb, time, os, re


def login_view(request):
    if request.user.is_authenticated():
        return redirect(reverse('home'))
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        #pdb.set_trace()
        if form.is_valid():
        ################# action ###############################
            user = authenticate(
                uname=form.cleaned_data['username'],
                passw=form.cleaned_data['password'])
            if user is not None and user.is_active:
                login(request, user)
                ###################### session manager #######################
                request.session['api_token_url'] = user.api_token_url
                #pdb.set_trace()
                try:
                    return redirect(request.GET['next'])
                except KeyError:
                    return redirect(reverse('home'))
                    
    else:
        form = LoginForm()
  
    return render(request, 'login.html',
        {'form': form})


def logout_view(request):
    logout(request)
    return redirect(reverse('login'))


@login_required()
def home_view(request):
    return render(request, 'home.html')


@login_required()
def define_job_view(request):
    ###################### session manager #######################  
    try:
        flavor_choices = \
            [flavor.as_choice() for flavor in request.session['flavors_dict'].values()]
      
    except (KeyError, TypeError):
        api_token_url = request.session['api_token_url']
        api_token = api_token_url['api_token']
        compute_url = api_token_url['compute_url']
            
        flavors_dict = OSFlavor.from_json_list(
            compute.get_flavor_list(api_token, compute_url))
        request.session['flavors_dict'] = flavors_dict
        flavor_choices = \
            [flavor.as_choice() for flavor in flavors_dict.values()]
    ###############################################################
    
    if request.method == 'POST':
        #pdb.set_trace()
        ################# action ###############################
        form = JobForm(request.POST, request.FILES)
        if form.is_valid():
            job = Job(user=request.user,
                file_input=request.FILES['file_input'],
                mapred_job=request.FILES['mapred_job'],
                fully_qualified_job_impl_class=form.cleaned_data['fully_qualified_job_impl_class'])
            job.save()
            #pdb.set_trace()
            run_mapred_job(
                request=request, job=job, job_form=form, media_root=MEDIA_ROOT)
            
            return redirect(reverse('home'))
        
    else:
        #pdb.set_trace()
        form = JobForm(
            initial={'server_count':'1', 'server_name':'hadoop'})
            
    form.fields['flavor'].widget.choices = flavor_choices
    
    return render(request, 'define_job.html', {'form': form})


@login_required()
def job_details_view(request, job_id=None):
    #pdb.set_trace()
    job = get_object_or_404(Job, pk=job_id, user=request.user)
    return render(request, 'job_details.html', {'job': job})

@login_required()
def job_download_view(request, job_id=None, kind='output'):
    job = get_object_or_404(Job, pk=job_id, user=request.user)
    kind2file = {'input':job.file_input, 'output':job.file_output, 'mapred':job.mapred_job}
    file2download = kind2file[kind]
    default_filename = re.match(r'.*/(?P<filename>.*\..*)', file2download.file.name).groupdict()['filename']
    response = HttpResponse(file2download.chunks(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(default_filename)
    return response

@login_required()
def job_history_view(request):
    #pdb.set_trace()
    try:
        job_list = get_list_or_404(Job, user=request.user)
    except Http404:
	job_list = list()
    return render(request, 'job_history.html', {'job_list': job_list})
