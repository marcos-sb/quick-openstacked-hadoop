#Custon authentication backend to work with openstack

from mapred.compute import get_api_auth, get_flavor_list
from django.contrib.auth.models import User
from mapred.exceptions import ServiceError
import pdb

class OpenStackBackend(object):
        
    def authenticate(self, uname=None, passw=None):
        api_token_url = get_api_auth(uname, passw)
        
        try:
            user = User.objects.get(username=uname)
        except User.DoesNotExist:
            user = User(username=uname, password='fromopenstack')
            user.is_staff = False
            user.is_superuser = False
            user.save()
        finally:
            user.api_token_url = api_token_url
            #pdb.set_trace()
        return user
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

