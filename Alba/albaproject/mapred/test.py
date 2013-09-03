from mapred.fabric import fabfile
from multiprocessing import Process

class DTimer(object):
    pass

def _execute():
	timer = DTimer()

	fabfile.set_key(
			abs_file_path='/home/marcos.salgueiro/Public/',
			file_name='test.pem',
			priv_key='''-----BEGIN RSA PRIVATE KEY-----
			MIICXQIBAAKBgQCm+zmzhnEVQY8iW8zlZt5VRnsPWY5xmQqOnTESelcmv/9Mx6uz
			2WKjmVA3QRubXs/SsisAMkvzsQva19XafAGxJ8utWnokWtkHUcJvgW5BQiXepA+j
			Hgh7wAtSFqdAP7QzU9H9+pHYt3nOBn9KZ1SywN3Mmp4sL0YfHq9C18hKSQIDAQAB
			AoGAXHH72QtWcfkwwEnonxybfMSffrkLJpMfCCO4tk0rENX9BsoIonJ4rLBFe8G9
			AgC0uCZRrjMqX4kmUgtqZyJ+YGvPtxKjY7Ex5dATGAbUiKpVEtPn3Q/LZvjGyK5A
			QqCEuZdMK0DiGtc0zFXTT6iWiEkYIs6JwJNhhvkf6x6Omh0CQQDXr6SYDdxcYaO8
			wQyKSNx24LKCK8XmjiVUe8mr0NWTauhWYdmJ1pU9d58kLe22aiNqnJakUysO2lwv
			LsC11J0/AkEAxjEcOTczA3GIYm5jd4bSV0b4b5FgdhCzvKOKGneVJkhyCvcl8yx6
			/Pwq/CTb09VSxFASF+4sJqoaR6RSMXZOdwJBAKJRfBQ2sjUQAjKmMjLLvKb2WUEf
			gjMNnMhk1JQqeOEVnr6LqzRRukTlBm4q5m/WlsrAB5qpQIlQCfo0PDFbTe8CQFKw
			RLU+aYNDSALBSbChyHpvetGZluRLfaHznXgDcnABg8s9aFD3uux4DTsb6beM5jZP
			rezcCwGqsMI5Na27TWsCQQDMPVJrSe9nKKqpL+nOmMutxYnBOnGyg/wKXlYIVAR3
			fMUs1mfEnHvclPnVOgtQ+ATTVgrXXX3GSO1gCWcvOGQv
			-----END RSA PRIVATE KEY-----''')

	fabfile.set_hadoop_ram(1024)
	fabfile.set_master_ips(priv_ipv4='17.16.0.2',
			pub_ipv4='19.16.0.1')

	fabfile.set_slaves_ips(priv_ipv4_list=[], pub_ipv4_list=[])

	fabfile.set_input_filename('/home')
	fabfile.set_mapred_job_filename('/home')
	fabfile.set_mapred_job_impl_class('/home')
	fabfile.set_output_path('/home')

	fabfile.start2(timer)

def run_mapred():
        Process(target=_execute, args=[]).start()
