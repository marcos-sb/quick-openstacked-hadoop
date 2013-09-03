from django.db import models
from django.contrib.auth.models import User
from albaproject.settings import MEDIA_ROOT

import pdb


def _upload_to_generic(prefix_path=None, instance=None, field=None, filename=None):
        #pdb.set_trace()
        if not instance.pk: # generate DB PK if not present
            instance.save()
        if not prefix_path:
            if not filename:
                return '{0}/job_{1}/{2}'.format(instance.user.username, instance.pk,
                    field)
            return '{0}/job_{1}/{2}/{3}'.format(instance.user.username, instance.pk,
                field, filename)
        return '{0}/{1}/job_{2}/{3}'.format(prefix_path, instance.user.username,
            instance.pk, field)


class Job(models.Model):

    def __unicode__(self):
        return str(self.id)
        
    def save(self, *args, **kwargs):
        #pdb.set_trace()
        _input = self.file_input
        _job = self.mapred_job
        _output = self.file_output
        self.file_input = None
        self.mapred_job = None
        self.file_output = None
        super(Job, self).save(*args,**kwargs)
        self.save = super(Job, self).save
        self.file_input = _input
        self.mapred_job = _job
        self.file_output = _output
        self.save() #super.save
        

    def input_dest(self, filename):
        return _upload_to_generic(None, self, 'input', filename)
        
    def mapred_dest(self, filename):
        return _upload_to_generic(None, self, 'mapred', filename)
        
    def output_dest(self, filename):
        return _upload_to_generic(None, self, 'output', filename)
    
    def output_path(self):
        return _upload_to_generic(MEDIA_ROOT, self, 'output', None)
        
    user = models.ForeignKey(User)
    file_input = models.FileField(upload_to=input_dest, null=True)
    mapred_job = models.FileField(upload_to=mapred_dest, null=True)
    fully_qualified_job_impl_class = models.CharField(max_length=200, null=True)
    file_output = models.FileField(upload_to=output_dest, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)


class Server(models.Model):
    job = models.ForeignKey(Job)
    openstack_id = models.CharField(max_length=200)
    server_name = models.CharField(max_length=200)
    vcpus = models.PositiveSmallIntegerField()
    ram = models.PositiveIntegerField()
    disk = models.PositiveIntegerField()


