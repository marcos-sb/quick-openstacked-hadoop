#!/usr/bin/env python

import os, subprocess, re, sys

def set_env():
    if 'OS_AUTH_URL' not in os.environ:
        print '\nAbout to set up the execution environment...\n'
        home = os.environ['HOME']
        new_env = subprocess.check_output(['bash', '-c', 'source {0}/.keystonerc && env'.format(home)]).split('\n')
        for line in new_env:
            (key, _, value) = line.partition('=')
            os.environ[key] = value
        print '\nCredentials correctly sourced...\n'



def install_os():
    print '\nRelaxing SELinux...\n'
    os.system('setenforce 0')

    print '\nAdding repos...\n'
    os.system('curl http://repos.fedorapeople.org/repos/openstack/openstack-folsom/fedora-openstack-folsom.repo -o /etc/yum.repos.d/fedora-openstack-folsom.repo')

    print '\nNova (compute), Glance (images), Keystone (identity), Swift (object store), Horizon (dashboard)\n'
    os.system('yum install -y openstack-utils openstack-nova openstack-glance openstack-keystone openstack-swift openstack-dashboard openstack-swift-proxy openstack-swift-account openstack-swift-container openstack-swift-object')

    print '\nQPID (AMQP message bus), memcached, NBD (Network Block Device) module\n'
    os.system('yum install -y qpid-cpp-server-daemon qpid-cpp-server memcached nbd')

    print '\nPython bindings...\n'
    os.system('yum install -y python-django-openstack-auth python-django-horizon python-keystone python-keystone-auth-token python-keystoneclient python-nova-adminclient python-quantumclient')

    print '\nSome documentation...\n'
    os.system('yum install -y openstack-keystone-doc openstack-swift-doc openstack-cinder-doc python-keystoneclient-doc')

    print '\nNew Folsom components: Quantum (network), Tempo, Cinder (replacement for Nova volumes)\n'
    os.system('yum install -y openstack-quantum openstack-tempo openstack-cinder openstack-quantum-linuxbridge openstack-quantum-openvswitch python-cinder python-cinderclient')

    print('\nRuby bindings...\n')
    os.system('yum install -y rubygem-openstack rubygem-openstack-compute')

    print('\nImage creation tools...\n')
    os.system('yum install -y appliance-tools appliance-tools-minimizer febootstrap rubygem-boxgrinder-build')

    print '\nOpenStack install phase over...\n'
    print '\nOn to configuring services...\n'
    os.system('openstack-db --service nova --init --yes --rootpw root')
    os.system('openstack-db --service glance --init --yes --rootpw root')
    os.system('openstack-db --service cinder --init --yes --rootpw root')

    print '\nStarting/enabling support services...\n'
    print '\nMessage queue...\n'
    os.system('systemctl restart qpidd.service && systemctl enable qpidd.service')
    print '\nVirtualization daemon...\n'
    os.system('systemctl restart libvirtd.service && systemctl enable libvirtd.service')

    print '\nStarting/enabling glance-related services...\n'
    os.system('for svc in api registry; do systemctl restart openstack-glance-$svc.service; done')
    os.system('for svc in api registry; do systemctl enable openstack-glance-$svc.service; done')

    print '\nSkipping volume creation (Cinder configuration)...\n'
    print '\nStarting/enabling compute-related (Nova) services...\n'
    os.system('for svc in api objectstore compute network scheduler cert; do systemctl restart openstack-nova-$svc.service; done')
    os.system('for svc in api objectstore compute network scheduler cert; do systemctl enable openstack-nova-$svc.service; done')

    print '\nInitial Keystone setup...\n'
    os.system('openstack-db --service keystone --init --yes --rootpw root')
    admin_token = subprocess.check_output('openssl rand -hex 10'.split())[:-1]
    home = os.environ['HOME']
    with(open('{0}/.keystonerc'.format(home),'w')) as fout:
        fout.write('export ADMIN_TOKEN={0}\n'.format(admin_token))
        fout.write('export OS_USERNAME=admin\n')
        fout.write('export OS_PASSWORD=verybadpass\n')
        fout.write('export OS_TENANT_NAME=admin\n')
        fout.write('export OS_AUTH_URL=http://127.0.0.1:5000/v2.0/\n')
        fout.write('export SERVICE_ENDPOINT=http://127.0.0.1:35357/v2.0/\n')
        fout.write('export SERVICE_TOKEN={0}\n'.format(admin_token))
    set_env()
    print '\nAdmin credentials stored in {0}/.keystonerc\n'.format(home)
    os.system('openstack-config --set /etc/keystone/keystone.conf DEFAULT admin_token {0}'.format(admin_token))
    os.system('systemctl restart openstack-keystone.service && systemctl enable openstack-keystone.service')

    print '\nAbout to create sample data...\n'
    os.system('ADMIN_PASSWORD=verybadpass SERVICE_PASSWORD=servicepass openstack-keystone-sample-data')

    out = os.system('keystone user-list')
    users_ok = out == 0
    if not users_ok:
        raise Exception('*** There has been an error with Keystone')
    print '\nKeystone correctly installed...\n'

    print '\nConfiguring Nova to use Keystone...\n'
    os.system('openstack-config --set /etc/nova/api-paste.ini filter:authtoken admin_tenant_name service')
    os.system('openstack-config --set /etc/nova/api-paste.ini filter:authtoken admin_user nova')
    os.system('openstack-config --set /etc/nova/api-paste.ini filter:authtoken admin_password servicepass')
    os.system('openstack-config --set /etc/nova/nova.conf DEFAULT auth_strategy keystone')
    os.system('for svc in api compute; do systemctl restart openstack-nova-$svc.service; done')

    print '\nNova correctly installed...\n'

    print '\nUpdating Glance...\n'
    os.system('yum install -y openssl-devel gcc python-pip python-devel')
    os.system('python-pip uninstall python-glanceclient')
    os.system('python-pip install python-glanceclient --upgrade')

    print '\nConfiguring Glance to use Keystone...\n'
    os.system('openstack-config --set /etc/glance/glance-api.conf paste_deploy flavor keystone')
    os.system('openstack-config --set /etc/glance/glance-registry.conf paste_deploy flavor keystone')
    os.system('openstack-config --set /etc/glance/glance-api-paste.ini filter:authtoken admin_tenant_name service')
    os.system('openstack-config --set /etc/glance/glance-api-paste.ini filter:authtoken admin_user glance')
    os.system('openstack-config --set /etc/glance/glance-api-paste.ini filter:authtoken admin_password servicepass')
    os.system('openstack-config --set /etc/glance/glance-registry-paste.ini filter:authtoken admin_tenant_name service')
    os.system('openstack-config --set /etc/glance/glance-registry-paste.ini filter:authtoken admin_user glance')
    os.system('openstack-config --set /etc/glance/glance-registry-paste.ini filter:authtoken admin_password servicepass')
    os.system('for svc in api registry; do systemctl restart openstack-glance-$svc.service; done')

    print '\nGlance correctly installed...\n'

    print '\nAbout to start Horizon...\n'
    os.system('systemctl restart httpd.service && systemctl enable httpd.service')
    print '\nAbout to configure memcached...\n'
    os.system('systemctl restart memcached.service && systemctl enable memcached.service')
    print '\nInitial configuration finished!\n'



def configure_env():
    set_env()

    print '\nCreating tenant "mapreduce"...\n'
    os.system('keystone tenant-create --name mapreduce')
    tenant_list = subprocess.check_output(['keystone', 'tenant-list'])
    new_tenant_id = re.search(r'\| (?P<tenant_id>.*) \|.*mapreduce.*', tenant_list).groupdict()['tenant_id']

    print '\nCreating user "udc"...\n'
    os.system('keystone user-create --name udc --pass udc --tenant-id {0}'.format(new_tenant_id))
    user_list = subprocess.check_output(['keystone', 'user-list'])
    role_list = subprocess.check_output(['keystone', 'role-list'])
    new_user_id = re.search(r'\| (?P<user_id>.*) \|.*udc.*', user_list).groupdict()['user_id']
    member_role_id = re.search(r'\| (?P<role_id>.*) \|.*Member.*', role_list).groupdict()['role_id']
    os.system('keystone user-role-add --user-id {0} --role-id {1} --tenant-id {2}'.format(new_user_id, member_role_id, new_tenant_id))

    print '\nCreating network "novanet"...\n'
    #os.system('openstack-config --set /etc/nova/nova.conf DEFAULT network_manager nova.network.manager.FlatDHCPManager')
    #os.system('openstack-config --set /etc/nova/nova.conf DEFAULT flat_interface em2')
    #os.system('openstack-config --set /etc/nova/nova.conf DEFAULT public_interface em1')
    #os.system('openstack-config --set /etc/nova/nova.conf DEFAULT vlan_interface em2')
    #os.system('openstack-config --set /etc/nova/nova.conf DEFAULT flat_network_bridge br100')
    #os.system('openstack-config --set /etc/nova/nova.conf DEFAULT my_ip 193.144.50.102')
    os.system('openstack-config --set /etc/nova/nova.conf DEFAULT network_manager nova.network.manager.VlanManager')
    os.system('openstack-config --set /etc/nova/nova.conf DEFAULT vlan_interface eth0')
    os.system('openstack-config --set /etc/nova/nova.conf DEFAULT public_interface eth0')
    os.system('openstack-config --set /etc/nova/nova.conf DEFAULT my_ip 192.168.122.1')
    os.system('openstack-config --set /etc/nova/nova.conf DEFAULT auto_assign_floating_ip True')
    os.system('for svc in api compute network; do systemctl restart openstack-nova-$svc.service; done')
    #os.system('nova-manage network create novanet 17.16.0.0/24')
    os.system('nova-manage network create --fixed_range_v4=17.16.0.0/16 --num_networks=2 --vlan=100 --network_size=256 --label=novanet')
    os.system('nova-manage floating create --ip_range=19.16.0.0/24')
    os.system('nova --os-username udc --os-password udc --os-tenant-name mapreduce --os-auth-url http://127.0.0.1:5000/v2.0/ secgroup-add-rule default tcp 22 22 0.0.0.0/0')
    os.system('nova --os-username udc --os-password udc --os-tenant-name mapreduce --os-auth-url http://127.0.0.1:5000/v2.0/ secgroup-add-rule default icmp -1 -1 0.0.0.0/0')

    print '\nCreating flavor "little"...\n'
    os.system('nova-manage flavor create --name=little --memory=1024 --cpu=1 --is_public=True --root_gb=4 --flavor=6 --ephemeral_gb=0')
    print '\nWorking environment configuration finished!\n'



def install_vm():
    print '\nDownloading Hadoop virtual machine, please be patient...\n'
    os.system('curl https://quick-openstacked-hadoop.googlecode.com/files/hadoop_104_[0-2].tar -o hadoop_104_#1.tar')

    print '\nUnpacking downloaded files...\n'
    os.system('tar -x --multi-volume --file=hadoop_104_0.tar --file=hadoop_104_1.tar --file=hadoop_104_2.tar')

    print '\nUploading images to Glance "udc"@"mapreduce"...\n'
    kernel_info = subprocess.check_output('glance --os-username udc --os-password udc --os-tenant-name mapreduce --os-auth-url http://127.0.0.1:5000/v2.0/ image-create --name hadoop104_kernel --disk-format aki --container-format aki --file vmlinuz-2.6.32-279.14.1.el6.x86_64'.split())
    kernel_id = re.search(r'\| id.* \| (?P<kernel_id>.*) \|.*', kernel_info).groupdict()['kernel_id']
    initrd_info = subprocess.check_output('glance --os-username udc --os-password udc --os-tenant-name mapreduce --os-auth-url http://127.0.0.1:5000/v2.0/ image-create --name hadoop104_initrd --disk-format ari --container-format ari --file initramfs-2.6.32-279.14.1.el6.x86_64.img'.split())
    initrd_id = re.search(r'\| id.* \| (?P<initrd_id>.*) \|.*', initrd_info).groupdict()['initrd_id']
    os.system('glance --os-username udc --os-password udc --os-tenant-name mapreduce --os-auth-url http://127.0.0.1:5000/v2.0/ image-create --name hadoop104 --disk-format ami --container-format ami --property kernel_id={0} --property ramdisk_id={1} --file centos-final-rip.img'.format(kernel_id, initrd_id))

    print '\nCleaning up...\n'
    os.system('rm -f hadoop_104_*.tar vmlinuz-2.6.32-279.14.1.el6.x86_64 initramfs-2.6.32-279.14.1.el6.x86_64.img centos-final-rip.img')



def set_django_up():
    print '\nInstalling Fabric...\n'
    os.system('yum install -y fabric')
    print '\nSetting Django up...\n'
    os.system('mysql -uroot -proot -e "create database alba; grant all on alba.* to \'alba\'@\'localhost\' identified by \'alba\'"')
    os.chdir('Alba/albaproject')
    os.system('echo "no" | python manage.py syncdb')



if __name__ == '__main__':
    try:
        if os.environ['USER'] != 'root':
            print '*** Please run as root...'
            sys.exit(-1)

        install_os()
        configure_env()
        install_vm()
        set_django_up()

    except Exception as ex:
        print 'Exception: {0}'.format(ex.message)








