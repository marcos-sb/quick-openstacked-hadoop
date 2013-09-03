
class OSFlavor(object):
    @staticmethod
    def from_json_list(json_list):
        #return {flavor.id:flavor for flavor in (OSFlavor(json_flavor) for json_flavor in json_list)}
	flavors = dict()
	for flavor in (OSFlavor(json_flavor) for json_flavor in json_list):
            flavors[flavor.id] = flavor
        return flavors

    def __init__(self, json_flavor):
        self.id = int(json_flavor ['id'])
        self.name = json_flavor ['name']
        self.vcpus = json_flavor ['vcpus']
        self.ram = json_flavor ['ram']
        self.disk = json_flavor ['disk']

    def as_choice(self):
        return (str(self.id), ('{0.name} vcpus:{0.vcpus}'
                ' ram:{0.ram}MB disk:{0.disk}GB').format(self))

    def __str__(self):
        return ('id:{0.id} name:{0.name} vcpus:{0.vcpus}' + \
                ' ram:{0.ram}MB disk:{0.disk}GB').format(self)

    def __unicode__(self):
        return self.__str__


class OSServer(object):
    @staticmethod
    def from_json_list(json_list):
        return [OSServer(json_server) for json_server in json_list]

    def __init__(self, json_server):
        self.id = json_server ['id']
        self.name = json_server ['name']
        #FLAT NETWORK
        #self.private_ipv4 = json_server ['addresses']['novanet'][0]['addr']
        #self.public_ipv4 = json_server ['addresses']['novanet'][1]['addr']

        #VLAN NETWORK
        self.private_ipv4 = json_server ['addresses']['nova_net_0'][0]['addr']
        self.public_ipv4 = json_server ['addresses']['nova_net_0'][1]['addr']













