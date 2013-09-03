# -*- coding: utf-8 -*-
import httplib, json, pdb, re, string, random
from mapred.environment import keystone_host_port, mapred_tenant_name, mapred_image_name
from mapred.exceptions import ServiceError


def touch_keystone_service():
  
    try:
  
        conn = httplib.HTTPConnection(keystone_host_port)
        conn.request('GET', '/')
        response = conn.getresponse()
  
        if response.status > 300:
            raise ServiceError('Service down')
  
        return True
    
    finally:
        conn.close()


def get_api_auth(user, passw):
  
    try:
  
        params = '{ \
                    "auth": { \
                        "passwordCredentials": { \
                            "username": "' + user + '", \
                            "password": "' + passw + '" \
                        }, \
                        "tenantName": "' + mapred_tenant_name + '" \
                    } \
                }'
            
        headers = {"Content-Type": "application/json"}
        conn = httplib.HTTPConnection(keystone_host_port)
        conn.request('POST', '/v2.0/tokens', params, headers)
        response = conn.getresponse()
      
        if response.status != 200:
            raise ServiceError('{0.status} {0.reason}'.format(response))
      
        #pdb.set_trace()
      
        data = response.read()
        dd = json.loads(data)  
        api_token = dd ['access']['token']['id']
        endpoints = dd ['access']['serviceCatalog']
      
        for endpoint in endpoints:
            if endpoint ['type'] == 'compute':
                compute_url = endpoint ['endpoints'][0]['publicURL']
                break
        #pdb.set_trace()
        return {'api_token' : api_token,
                'compute_url' : compute_url}
        
    finally:
        conn.close()
  

def get_image_id(api_token, compute_url):
  
    try:
      
        headers = {"Content-Type": "application/json",\
                   "X-Auth-Token": api_token}
      
        match = re.search(r'//(?P<host_port>.+?)(?P<api_url>/.*)', compute_url)
        compute_host_port = match.groupdict() ['host_port']
        compute_api_url = match.groupdict() ['api_url']
        conn = httplib.HTTPConnection(compute_host_port)
        conn.request('GET', compute_api_url + '/images', '', headers)
        response = conn.getresponse()
      
        if response.status != 200:
            raise ServiceError('{0.status} {0.reason}'.format(response))
      
        data = response.read()
        dd = json.loads(data)
      
        #pdb.set_trace()
      
        for image in dd ['images']:
            if image ['name'] == mapred_image_name:
                image_id = image ['id']
                break
      
        return image_id
        
    finally:
        conn.close()
      
  
def get_flavor_list(api_token, compute_url):
  
    try:
      
        headers = {"Content-Type": "application/json",\
                   "X-Auth-Token": api_token}
      
        match = re.search(r'//(?P<host_port>.+?)(?P<api_url>/.*)', compute_url)
        compute_host_port = match.groupdict() ['host_port']
        compute_api_url = match.groupdict() ['api_url']
        conn = httplib.HTTPConnection(compute_host_port)
        conn.request('GET', compute_api_url + '/flavors/detail', '', headers)
        response = conn.getresponse()
      
        #pdb.set_trace()
      
        if response.status != 200:
            raise ServiceError('{0.status} {0.reason}'.format(response))
      
        data = response.read()
        dd = json.loads(data)
        
        return dd ['flavors']
      
    finally:
        conn.close()


def gen_keypair(api_token, compute_url):
  
    try:
        
        keypair_name = ''.join(random.choice(string.ascii_lowercase) for c in range(10))
        params = '{ \
                    "keypair": { \
                      "name": "' + keypair_name + '" \
                    } \
                  }'
                
        headers = {"Content-Type": "application/json", \
                   "X-Auth-Token": api_token}
      
        match = re.search(r'//(?P<host_port>.+?)(?P<api_url>/.*)', compute_url)
        compute_host_port = match.groupdict() ['host_port']
        compute_api_url = match.groupdict() ['api_url']
        conn = httplib.HTTPConnection(compute_host_port)
        conn.request('POST', compute_api_url + '/os-keypairs', params, headers)
        response = conn.getresponse()
      
        #pdb.set_trace()
          
        if response.status != 200:
            if response.status == 409: # keypair already exists
                gen_keypair(api_token, compute_url) #try again (new name will be generated)
            raise ServiceError('{0.status} {0.reason}'.format(response))
      
        data = response.read()
        dd = json.loads(data)
      
        #pdb.set_trace()
      
        key_name = dd ['keypair'] ['name']
        private_key = dd ['keypair'] ['private_key']
          
        return {'key_name' : key_name, 'private_key' : private_key}
        
    finally:
        conn.close()
    

def delete_keypair(api_token, compute_url, keypair_name):
  
    try:
                
        headers = {"Content-Type": "application/json", \
                   "X-Auth-Token": api_token}
      
        match = re.search(r'//(?P<host_port>.+?)(?P<api_url>/.*)', compute_url)
        compute_host_port = match.groupdict() ['host_port']
        compute_api_url = match.groupdict() ['api_url']
        conn = httplib.HTTPConnection(compute_host_port)
        conn.request('DELETE', compute_api_url + '/os-keypairs/' + keypair_name, '', headers)
        response = conn.getresponse()
      
        #pdb.set_trace()
          
        if response.status != 202:
            raise ServiceError('{0.status} {0.reason}'.format(response))
      
    finally:
        conn.close()

    
def create_servers(api_token, compute_url, keypair_name, count, server_name, image_id, flavor_id):
  
    try:
  
        headers = {"Content-Type": "application/json", \
                   "X-Auth-Token": api_token}
        
        match = re.search(r'//(?P<host_port>.+?)(?P<api_url>/.*)', compute_url)
        compute_host_port = match.groupdict() ['host_port']
        compute_api_url = match.groupdict() ['api_url']
        conn = httplib.HTTPConnection(compute_host_port)
        server_id_list = []

        for i in range(count):
        
            params = '{ \
                        "server": { \
                            "flavorRef": "' + str(flavor_id) + '", \
                            "imageRef": "' + image_id + '", \
                            "name": "' + server_name + str(i) + '", \
                            "key_name": "' + keypair_name + '" \
                        } \
                     }'
                
            conn.request('POST', compute_api_url + '/servers', params, headers)
            response = conn.getresponse()
        
            if response.status != 202:
                raise ServiceError('{0.status} {0.reason}'.format(response))
        
            data = response.read()
            dd = json.loads(data)
        
            server_id_list.append(dd ['server']['id'])
            
        return server_id_list
      
    finally:
        conn.close()


def get_server_info(api_token, compute_url, server_id_list):
  
    try:
    
        headers = {"Content-Type": "application/json",\
                       "X-Auth-Token": api_token}
      
        match = re.search(r'//(?P<host_port>.+?)(?P<api_url>/.*)', compute_url)
        compute_host_port = match.groupdict() ['host_port']
        compute_api_url = match.groupdict() ['api_url']
        conn = httplib.HTTPConnection(compute_host_port)
            
        server_list = []
        for server_id in server_id_list:
            
            conn.request('GET', compute_api_url + '/servers/' + server_id, '', headers)
            response = conn.getresponse()
          
            if response.status != 200:
                raise ServiceError('{0.status} {0.reason}'.format(response))
          
            data = response.read()
            dd = json.loads(data)
            #pdb.set_trace()
            server_list.append(dd ['server'])
            
        return server_list
      
    finally:
        conn.close()


def delete_servers(api_token, compute_url, server_id_list):
    try:
                
        headers = {"Content-Type": "application/json", \
                   "X-Auth-Token": api_token}
      
        match = re.search(r'//(?P<host_port>.+?)(?P<api_url>/.*)', compute_url)
        compute_host_port = match.groupdict() ['host_port']
        compute_api_url = match.groupdict() ['api_url']
        conn = httplib.HTTPConnection(compute_host_port)
        
        for server_id in server_id_list:
            conn.request('DELETE', compute_api_url + '/servers/' + server_id, '', headers)
            response = conn.getresponse()
            data = response.read()
            #pdb.set_trace()
          
            if response.status != 204:
                raise ServiceError('{0.status} {0.reason}'.format(response))
        
    finally:
        conn.close()









