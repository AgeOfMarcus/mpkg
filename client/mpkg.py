#!/usr/bin/python3

import requests, base64, json, os, fire
from termcolor import colored as c

def alert(msg): return "%s : %s" % (c("[!]","red"),msg)
def plus(msg): return "%s : %s" % (c("[+]","green"),msg)
def info(msg): return "%s : %s" % (c("[*]","cyan"),msg)

def sources():
	with open("sources.txt","r") as f:
		res = f.read().split("\n")
	for i in res:
		if (i.startswith("#")) or (i == ""):
			res.remove(i)
	while "" in res: res.remove("")
	return res

def packages():
	with open("packages.json","r") as f:
		pkgs = json.loads(f.read())
	return pkgs

def update_packages(new_packages):
	with open("packages.json","w") as f:
		f.write(json.dumps(new_packages))

def get_packages():
	pkgs = []
	for i in sources():
		url = "http://" + i + "packages"
		res = requests.get(url).json()['packages']
		for pkg in res:
			found = False
			for c in pkgs:
				if pkg in c:
					found = True
			if not found:
				pkgs.append([i,pkg])
	return pkgs

def install_package(name):
	pkgs = packages()
	found = False
	for i in pkgs:
		if not found:
			if name in i:
				found = i
	if found == False:
		print(alert("Package not in list"))
		return None
	print(plus("Found package"))
	url = "http://" + found[0] + "package/" + found[1]
	pkg = base64.b64decode(requests.get(url).content)
	with open("/tmp/%s.zip" % name,"wb") as f:
		f.write(pkg)
	print(info("Package downloaded successfully"))
	os.system("unzip /tmp/%s.zip" % name)
	print(info("Package unzipped"))
	olddir = os.getcwd()
	os.chdir("packages/%s" % name)
	os.system("bash install.sh")
	print(plus("Package installed"))
	os.chdir(olddir)
	os.system("rm -r packages")
	return None

class CLI(object):
	def update(self):
		update_packages(get_packages())
	def install(self, package):
		install_package(package)
if __name__ == "__main__":
	fire.Fire(CLI)
