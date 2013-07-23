Quick OpenStacked Hadoop
========================
An easy way to tap your hardware to compute MapReduce applications.

FOREWORD
--------
This piece of software is intented to sample a real world application. It is by no means suitable for production deployments.


SYSTEM REQUERIMENTS
-------------------
* x86_64 architecture and fresh Fedora 17 installation.
* 10GB free HDD space and lots of RAM (4GB+)
* 1h+ of your time...


QUICK INSTALL
-------------
Install Fedora 17.

`sudo yum install -y git`  
`sudo yum update -y`

`sudo reboot`

`cd <destination_folder_parent>`  

`git clone https://github.com/marcos-sb/quick-openstacked-hadoop.git`  
(quick-openstacked-hadoop folder will be created for you)

`cd quick-openstacked-hadoop`

`sudo ./install.py`  
(It will install OpenStack Folsom, a Hadoop virtual machine, Fabric and Django)

`./configure.py`  
(To set up Django settings)


QUICK RUN
---------
`cd quick-openstacked-hadoop/Alba/albaproject`

`python manage.py runserver`

navigate to <http://localhost:8000/albaproject/mapred>

user: "udc"  
password: "udc"


HORIZON
-------
OpenStack native administration web interface is accessible at <http://localhost/dashboard>
