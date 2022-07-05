#!/usr/bin/python3

# Marwan NOUR

import os
import json
import optparse
import requests
from requests.auth import HTTPBasicAuth
import urllib3

# Disable SSL warnings 
urllib3.disable_warnings()

apiversion = "v2"
final_list_of_blobs = []

parser = optparse.OptionParser()
parser.add_option('-u', '--url', action="store", dest="url", help="URL Endpoint for Docker Registry API v2. Eg https://IP:Port", default="spam")
parser.add_option('--username', action="store", dest="username", help="username for Docker Registry API v2", default="")
parser.add_option('--password', action="store", dest="password", help="username for Docker Registry API v2", default="")
options, args = parser.parse_args()
url = options.url

# Auth data
username = options.username
password = options.password


def list_repos(username, password):
	req = requests.get(url+ "/" + apiversion + "/_catalog", verify=False, auth=HTTPBasicAuth(username, password))
	if req.status_code == 401:
		print("\n[-] Please specify a username and a password for the registry with --username and --password")
		exit(1)
	elif req.status_code == 200:
		return json.loads(req.text)["repositories"]
	else:
		print("Error: " + req.status_code)
		exit(1)


def find_tags(reponame, username, password):
	req = requests.get(url+ "/" + apiversion + "/" + reponame+"/tags/list", verify=False, auth=HTTPBasicAuth(username, password))
	if req.status_code == 401:
		print("\n[-] Please specify a username and a password for the registry with --username and --password")
		exit(1)	
	elif req.status_code == 200:
		print("\n")
		data =  json.loads(req.content)
		if "tags" in data:
			return data["tags"]
	else:	
		print("Error: " + req.status_code)
		exit(1)


def list_blobs(reponame,tag, username, password):
	req = requests.get(url+ "/" + apiversion + "/" + reponame+"/manifests/" + tag, verify=False, auth=HTTPBasicAuth(username, password))
	if req.status_code == 401:
		print("\n[-] Please specify a username and a password for the registry with --username and --password")
		exit(1)
	elif req.status_code == 200:
		data = json.loads(req.content)
		if "fsLayers" in data:
			for x in data["fsLayers"]:
				curr_blob = x['blobSum'].split(":")[1]
				if curr_blob not in final_list_of_blobs:
					final_list_of_blobs.append(curr_blob)
	else:
		print("Error: " + req.status_code)
		exit(1)


def download_blobs(reponame, blobdigest,dirname, username, password):
	req = requests.get(url+ "/" + apiversion + "/" + reponame +"/blobs/sha256:" + blobdigest, verify=False, auth=HTTPBasicAuth(username, password))
	if req.status_code == 401:
		print("\n[-] Please specify a username and a password for the registry with --username and --password")
		exit(1)
	elif req.status_code == 200:
		filename = "%s.tar.gz" % blobdigest
		with open(dirname + "/" + filename, 'wb') as test:
			test.write(req.content)
	else:
		print("Error: " + req.status_code)
		exit(1)	

def main(): 
	if url != "spam":
		list_of_repos = list_repos(username, password)
		print("\nPress <Ctrl-C> to Exit\n")
		print("\n[+] List of Repositories:\n")
		for x in list_of_repos:
			print(x)
		
		try:
			target_repo = input("\nWhich repo would you like to download?:  ")
			if target_repo in list_of_repos:
				tags = find_tags(target_repo, username, password)
				if tags != None:
					print("\n[+] Available Tags:\n")
					for x in tags:
						print(x)

					target_tag = input("\nWhich tag would you like to download?:  ")
					if target_tag in tags:
						list_blobs(target_repo,target_tag, username, password)

						dirname = input("\nGive a directory name:  ")
						os.makedirs(dirname)
						print("Now sit back and relax. I will download all the blobs for you in %s directory. \nOpen the directory, unzip all the files and explore like a Boss. " % dirname)
						for x in final_list_of_blobs:
							print("\n[+] Downloading Blob: %s" % x)
							download_blobs(target_repo,x,dirname, username, password)
					else:
						print("No such Tag Available. Qutting....")
				else:
					print("[+] No Tags Available. Quitting....")
			else:
				print("No such repo found. Quitting....")
		except KeyboardInterrupt:
			print("\nExiting...")
			exit(1)
	else:
		print("\n[-] Please use -u option to define API Endpoint, e.g. https://IP:Port\n")


if __name__ == "__main__":
	main()
