Quick OpenStacked Hadoop - qosh
=
An easy way to use your hardware to compute MapReduce applications. _qosh_ is the result of my CS degree thesis.
* Full [thesis](https://docs.google.com/file/d/0B2lmVzXW-C5UTjllNm5wM04zd0k/edit?usp=sharing) in Spanish, [paper](http://www.oalib.com/paper/3064389) and [book](http://www.amazon.com/Private-Cloud-Implementation-MapReduce-Applications/dp/3659643963) in English featuring qosh.  
* Keynote presentation [slides](https://docs.google.com/file/d/0B2lmVzXW-C5USHVhQnRtVTBqSWM/edit?usp=sharing) in English.  
* Click the image just below to watch it in action on Youtube.

[![Click to watch on Youtube](http://img.youtube.com/vi/WKaQ_f0PmSY/0.jpg)](http://youtu.be/WKaQ_f0PmSY).

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
