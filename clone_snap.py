import requests
import json
import os
from docopt import docopt
import traceback
import csv
requests.packages.urllib3.disable_warnings()

__version__ = '1.0'
__revision__ = '20190626'
__deprecated__ = False

data = {}
def get_headers():
	# Function that will return the headers and the Auth for the API
	headers = {
		"Content-Type":"application/json",
		"Accept": "application/json",
		"X-Auth-User": 'root',
		"X-Auth-Key": 'password'

	}
	return headers

def get_args():

	usage = """
	Usage:
		try.py -s <STORAGE> -fs <FILESYSTEM> -sp <SNAPSHOT> -cl <CLONE> --clone		
		try.py --version
		try.py -h | --help

	Options:
		-h --help            Show this message and exit
		-s <STORAGE>         ZFS appliance/storage name

	"""
	# version = '{} VER: {} REV: {}'.format(__program__, __version__, __revision__)
	# args = docopt(usage, version=version)
	args = docopt(usage)
	return args	



def get_projects(args, storage, filesys, snap_name, clone_name):

	header = get_headers()
	base_url = 'https://{}:215'.format(storage)
	

	# url = '{}/api/storage/v1/pools/testpool/projects/test4/filesystems?snaps=true'.format(base_url)
	url = '{}/api/storage/v1/filesystems'.format(base_url)

	resp = requests.get(url = url, verify=False, headers = header)

	json1 = resp.json()
	data.update(json1)
	# print(json.dumps(data, indent=2))
	for i in data['filesystems']:
		# print(i['name'])
		if i['name'] == filesys:
			# print(i['pool'])
			# print(i['name'])
			# print(i['project'])
			pool = i['pool']
			filesys = i['name']
			# print(filesys)
			project = i['project']

			newsnap(storage, pool, project, filesys, snap_name, clone_name)

			break
		else:
			print("Filesystem not Found!")
			break


def newsnap(storage, pool, project, filesys, snap_name, clone_name):
	header = get_headers()
	base_url = 'https://{}:215'.format(storage)
	
	data1 = {
		"share" : clone_name,

	}
	json_dump = json.dumps(data1)

	url = '''{}/api/storage/v1/pools/{}/projects/{}/filesystems/{}/snapshots/{}/clone'''.format(
				base_url, 
				pool,
				project,
				filesys,
				snap_name)

	# print(url)
	url_list = '''{}/api/storage/v1/pools/{}/projects/{}/filesystems/{}/snapshots'''.format(
			base_url, 
			pool,
			project,
			filesys)

	resp = requests.put(url = url, data= json_dump, verify=False, headers = header)
	newresp = requests.get(url = url_list,verify=False, headers = header)
	json1 = newresp.json()
	data.update(json1)
	# print(resp.status_code)
	if resp.status_code == 201:
		print("-"*30)
		print("Snapshot "+ snap_name + " Cloned! on pool ("+pool+") and filesystem ("+filesys+")")
	
		data_ = data['snapshots']
		data_file = open('datafile.csv', 'w')
		csv_ = csv.writer(data_file)

		c = 0
		for item in data_:
			if c == 0:
				header = item.keys()
				csv_.writerow(header)
				c +=1

			csv_.writerow(item.values())
		data_file.close()

		# Creating json file
		with open('datafile.json', 'w') as outfile:
			json.dump(data_, outfile, indent = 2)

	else:
		print("-"*30)
		print("Error Cloning Snapshot: \n\t --> "+ snap_name)
		print("ERROR CODE: \n\t --> ",resp.status_code)


def main(args):
	storage = args['<STORAGE>']
	filesys = args['<FILESYSTEM>']
	snap_name = args['<SNAPSHOT>']
	clone_name = args['<CLONE>']


	get_projects(args, storage, filesys, snap_name, clone_name)


if __name__ == '__main__':
	try:
		ARGS = get_args()

		main(ARGS)
	except KeyboardInterrupt:
		print('\nReceived Ctrl^C. Exiting....')
	except Exception:
	    ETRACE = traceback.format_exc()
	    print(ETRACE)