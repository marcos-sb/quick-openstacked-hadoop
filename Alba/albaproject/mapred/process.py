from django.core.files import File

from mapred.fabric import fabfile
from mapred import compute
from mapred.models import Server
from mapred.objects import OSServer
from multiprocessing import Process

import time
import os
#import pdb


class DTimer(object):  # dynamic timer ...
    pass


def _execute(request, job, form, media_root):
    ######### virtual machine creation #########
    api_token_url = request.session['api_token_url']
    api_token = api_token_url['api_token']
    compute_url = api_token_url['compute_url']
    image_id = compute.get_image_id(api_token, compute_url)
    keypair = compute.gen_keypair(api_token, compute_url)
    server_count = form.cleaned_data['server_count']
    server_name = form.cleaned_data['server_name']
    flavor_id = form.cleaned_data['flavor']

    timer = DTimer()
    timer.deploystart = time.time()

    try:
        server_id_list = compute.create_servers(api_token, compute_url,
                                                keypair['key_name'], server_count, server_name,
                                                image_id, flavor_id)

        while True:
            #sleep and retry until an ipv4 had been set
            try:
                #time.sleep(server_count * 4)
                time.sleep(0.1)
                os_server_list = OSServer.from_json_list(
                    compute.get_server_info(api_token, compute_url, server_id_list))
                break
            except KeyError:
                pass

        flavor = request.session['flavors_dict'][flavor_id]
        for os_server in os_server_list:
            server = Server(job=job, openstack_id=os_server.id,
                            server_name=os_server.name, vcpus=flavor.vcpus,
                            ram=flavor.ram, disk=flavor.disk)
            server.save()


    #FABRIC

        fabfile.set_key(
            abs_file_path='{0}/{1}/job_{2}/'.format(
                media_root, request.user.username, job.pk),
            file_name=keypair['key_name'] + '.pem',
            priv_key=keypair['private_key'])

        fabfile.set_hadoop_ram(flavor.ram)

        fabfile.set_master_ips(priv_ipv4=os_server_list[0].private_ipv4,
                               pub_ipv4=os_server_list[0].public_ipv4)

        fabfile.set_slaves_ips(
            priv_ipv4_list=[os_server.private_ipv4 for os_server in os_server_list],
            pub_ipv4_list=[os_server.public_ipv4 for os_server in os_server_list])

        fabfile.set_input_filename(abs_file_path=job.file_input.path)
        fabfile.set_mapred_job_filename(abs_file_path=job.mapred_job.path)
        fabfile.set_mapred_job_impl_class(fq_class_name=job.fully_qualified_job_impl_class)
        fabfile.set_output_path(output_path=job.output_path())

    #configure, process job and download results from guest
        fabfile.start(timer)

    #attach output_file to job model

        full_output_file_name = '{0}/{1}'.format(job.output_path(),
                                                 fabfile.get_output_file_name())
        full_output_cloned_file_name = full_output_file_name + '-clone'
        os.rename(full_output_file_name, full_output_cloned_file_name)
        with open(full_output_cloned_file_name) as f:
            output_file = File(f)
            job.file_output.save(name=fabfile.get_output_file_name(),
                                 content=output_file)
            os.remove(full_output_cloned_file_name)

    finally:
        #stop and clean
        #delete keypair and servers from openstack
        timer.cleanupstart = time.time()
        fabfile.stop()
        fabfile.delete_keypair()
        compute.delete_keypair(api_token, compute_url, keypair['key_name'])
        compute.delete_servers(api_token, compute_url, server_id_list)
        #erase files from controller node
       timer.processingend = time.time()

        #print processing times
        print '\n###################################'
        print '## user: {0} ## job: {1:5d}'.format(request.user.username, job.id)
        print '###################################'
        print '## deploying time   # {0:>4.1f} s'.format(timer.hadoopwfconfstart - timer.deploystart)
        print '## configuring time # {0:>4.1f} s'.format(timer.hadoopmapredstart - timer.hadoopwfconfstart)
        print '## mapreducing time # {0:>4.1f} s'.format(timer.hadoopmapredend - timer.hadoopmapredstart)
        print '## cleaning up time # {0:>4.1f} s'.format(timer.processingend - timer.cleanupstart)
        print '###################################'
        print '## total running time # {0:>.1f} s'.format(timer.processingend - timer.deploystart)
        print '###################################\n'
        #################################################################################


def run_mapred_job(request, job, job_form, media_root):
    Process(target=_execute, args=[request,job,job_form, media_root]).start()
    #_execute(request,job,job_form,media_root)

