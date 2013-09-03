from fabric.api import run, sudo, env, roles, settings, hide, execute, local, put, get, show

import re, pdb
import time

env.connection_attempts = 250
env.timeout = 1
env.abort_on_prompts = True
env.disable_known_hosts = True
env.no_keys = True
env.no_agent = True
##################### move to mapred environment
env.user = 'hduser'
env.password = 'hduser'
#####################

# SET I/O, KEY, RAM, MASTER AND SLAVES BEFORE USING #################################

#env.roledefs = {
#    'master':['192.100.0.1'],
#    'slaves':['192.100.0.1']
#}
#env.roledefs = None
#env.role2priv_ip = {
#    'master':['172.100.0.3'],
#    'slaves':['172.100.0.3']
#}
env.role2priv_ip = dict()
env.key_filename = None
#env.key_filename = '~/Documents/test.pem'
env.input_filename = None
#env.input_filename = '/home/marcos/Documents/words.tar.gz'
env.mapred_job_filename = None
env.mapred_job_impl_class = None
env.output_path = None
#env.output_path = '/home/marcos/Documents'
###################################### move to mapred environment
env.remote_input_path = '~/hadoop/input'
env.remote_mapred_job_path = '~/hadoop/mapred'
env.remote_output_path = '~/hadoop/output'
###############################
env.remote_mapred_job_filename = None
env.mb_ram = None

# AGAIN, SET I/O, KEY, RAM, MASTER AND SLAVES BEFORE USING #################################

def set_input_filename(abs_file_path=None):
    env.input_filename = abs_file_path

def set_mapred_job_filename(abs_file_path=None):
    env.mapred_job_filename = abs_file_path

def set_mapred_job_impl_class(fq_class_name=None):
    env.mapred_job_impl_class = fq_class_name

def set_output_path(output_path=None):
    env.output_path = output_path


def set_key(abs_file_path=None, file_name=None, priv_key=None):
    env.key_filename = abs_file_path + file_name;
    with open(env.key_filename, 'w') as f:
        f.write(priv_key)
        
    local('chmod 0600 ' + env.key_filename)


def set_master_ips(priv_ipv4=None, pub_ipv4=None):
    env.roledefs['master'] = [pub_ipv4]
    env.role2priv_ip['master'] = [priv_ipv4]
    
    
def set_slaves_ips(priv_ipv4_list=None, pub_ipv4_list=None):
    env.roledefs['slaves'] = pub_ipv4_list
    env.role2priv_ip['slaves'] = priv_ipv4_list


def set_hadoop_ram(mb_ram=None):
    env.mb_ram = mb_ram
    
########################################################################

def clean_file(file_name):
    sudo('rm -rf ' + file_name)
    sudo('touch ' + file_name)
    sudo('chmod 664 ' + file_name)
    sudo('chown :hadoop ' + file_name)


def _set_hadoop_ram():
    env_file = '$HADOOP_CONF_DIR/hadoop-env.sh'
    run("sed -ri 's_-Xmx[0-9]+m_-Xmx{0}m_' {1}".format(env.mb_ram, env_file))


def set_hadoop_master():
    masters_file = '$HADOOP_CONF_DIR/masters'
    clean_file(masters_file)
    run('echo {0} > {1}'.format(env.role2priv_ip['master'][0], masters_file))


def set_hadoop_slaves():
    slaves_file = '$HADOOP_CONF_DIR/slaves'
    clean_file(slaves_file)
    command = '"{0}\\n'.format(env.role2priv_ip['master'][0])
    for slave in env.role2priv_ip['slaves']:
        command += slave + '\\n'
    command = command[:-2] + '"' #"-2" as the '\' is escaped 
    run('echo -e {0} > {1}'.format(command, slaves_file))


def set_hadoop_core_site():
    core_site_file = '$HADOOP_CONF_DIR/core-site.xml'
    run("sed -ri 's_//[a-z0-9]+:_//{0}:_' {1}" \
        .format(env.role2priv_ip['master'][0], core_site_file))


def set_hadoop_mapred_site():
    mapred_site_file = '$HADOOP_CONF_DIR/mapred-site.xml'
    run("sed -ri 's_>[a-z0-9]+:_>{0}:_' {1}" \
        .format(env.role2priv_ip['master'][0], mapred_site_file))
        
        
#@roles('master')
#def set_hadoop_hdfs_site():
#    hdfs_site_file = '$HADOOP_CONF_DIR/hdfs-site.xml'
#    run("sed -ir 's_>[a-z0-9]+:_>{0}:_' {1}" \
#        .format(env.role2priv_ip['master'][0], hdfs_site_file))


@roles('master','slaves')
def ping_all():
    while True:
        try:
            run('echo "$(hostname) is up"')
            return
        except:
            time.sleep(1)

@roles('master')
def configure_master():
    _set_hadoop_ram()
    set_hadoop_master()
    set_hadoop_slaves()
    set_hadoop_core_site()
    set_hadoop_mapred_site()


@roles('slaves')
def configure_slaves():
    _set_hadoop_ram()
    set_hadoop_core_site()
    set_hadoop_mapred_site()


@roles('master')
def format_hdfs():
    hdfs_site_file_name = '$HADOOP_CONF_DIR/hdfs-site.xml'
    hdfs_site_file = run('cat ' + hdfs_site_file_name)
    match = re.search(r'>(?P<dfs_name_dir>.+name)<', hdfs_site_file)
    dfs_name_dir = match.groupdict() ['dfs_name_dir']
    sudo('rm -rf ' + dfs_name_dir + '/../*') #remove all folders from a previous hdfs formatting
    run('hadoop namenode -format')

        
@roles('master')
def start_hdfs():
    put(local_path=env.key_filename,
        remote_path='~/.ssh/id_rsa',
        mode=0600)
    run('start-dfs.sh')


@roles('master')
def stop_hdfs():
    run('stop-dfs.sh')
    

@roles('master')
def start_mapred():
    run('start-mapred.sh')
    

@roles('master')
def stop_mapred():
    run('stop-mapred.sh')


@roles('master')
def put_input():
    run('rm -rf ' + env.remote_input_path)
    run('mkdir -p ' + env.remote_input_path)
    put(local_path=env.input_filename, remote_path=env.remote_input_path)
    ##################################################################################
    match = re.search(r'.*/(?P<file_name>.+)(?P<file_ext>\..+$)', env.input_filename)
    file_ext = match.groupdict() ['file_ext']
    file_name = match.groupdict() ['file_name'] + file_ext
    ##################################################################################
    cmd = {}
    cmd['.tbz'] = cmd['.bz2'] = \
        cmd['.tgz'] = cmd['.gz'] = 'tar -C {0} -xvf'.format(env.remote_input_path)
    #cmd['.zip'] = 'unzip' ...
    
    #pdb.set_trace()
    run('{0} {1}/{2}'.format(
        cmd[file_ext], env.remote_input_path, file_name))
    run('rm -f {0}/{1}'.format(env.remote_input_path, file_name))
    
    #with settings(warn_only=True):
    #    run('hadoop dfs -rmr input output')
    run('hadoop dfs -mkdir input')
    run('hadoop dfs -put {0}/* input'.format(
        env.remote_input_path))
          

@roles('master')
def put_mapred_job():
    run('rm -rf ' + env.remote_mapred_job_path)
    run('mkdir -p ' + env.remote_mapred_job_path)
    put(local_path=env.mapred_job_filename, remote_path=env.remote_mapred_job_path)
    ##################################################################################
    match = re.search(r'.*/(?P<file_name>.+)(?P<file_ext>\..+$)', env.mapred_job_filename)
    file_ext = match.groupdict() ['file_ext']
    file_name = match.groupdict() ['file_name'] + file_ext
    ##################################################################################
    env.remote_mapred_job_filename = '{0}/{1}'.format(env.remote_mapred_job_path, file_name)


@roles('master')
def run_comp():
    run('hadoop jar {0} {1} input output'.format(
        env.remote_mapred_job_filename, env.mapred_job_impl_class))
    
    
@roles('master') 
def get_output():
    run('rm -rf ' + env.remote_output_path)
    run('mkdir -p ' + env.remote_output_path)
    run('hadoop dfs -get output ' + env.remote_output_path)
    run('tar -C {0} -czvf {0}/hadoop.out.tar.gz output'.format(env.remote_output_path))
    local('mkdir -p ' + env.output_path)
    get(remote_path='{0}/hadoop.out.tar.gz'.format(env.remote_output_path),
        local_path=env.output_path)
    

def stop():
    execute(stop_hdfs)
    execute(stop_mapred)


def delete_keypair():
    local('rm -rf ' + env.key_filename)


def get_output_file_name():
    return 'hadoop.out.tar.gz'

def start(timer):
    with show('debug'):
        execute(ping_all)
        timer.hadoopwfconfstart = time.time()
        execute(configure_master)
        execute(configure_slaves)
        execute(format_hdfs)
        execute(start_hdfs)
        execute(start_mapred)
        execute(put_input)
        execute(put_mapred_job)
        timer.hadoopmapredstart = time.time()
        execute(run_comp)
        timer.hadoopmapredend = time.time()
        execute(get_output)
        #execute(stop)
        #execute()






    
