#!/usr/bin/python3

from subprocess import Popen, PIPE
import os, sys, uuid

def list_packages():
	res = Popen("ls packages",stdout=PIPE,shell=True).communicate()[0].decode()
	pkgs = res.split("\n")
	while '' in pkgs: pkgs.remove("")
	return pkgs

start = '''
from flask import Flask, jsonify, request
from subprocess import Popen, PIPE
import os, uuid, base64

def list_packages():
	res = Popen("ls packages",stdout=PIPE,shell=True).communicate()[0].decode()
	pkgs = res.split("\\n")
	while '' in pkgs: pkgs.remove("")
	return pkgs

app = Flask("mPkg-server")
@app.route("/packages",methods=['GET'])
def app_packages():
	return jsonify({'packages':list_packages()})
'''
end = '''
app.run(host="{}",port={})
'''
comp_pkg = '''
def compress_pkg(name):
	os.system("zip %s.zip packages/%s -r" % (name,name))
	return "%s.zip" % name
'''

script = start + comp_pkg


for pkg in list_packages():
	script += '''
@app.route("/package/<name>",methods=['GET'])
def route_{}(name):
	if not name in list_packages():
		return ""
	else:
		res = base64.b64encode(open(compress_pkg(name),"rb").read()).decode()
		os.system("rm %s.zip" % name)
		return res
	'''.format(''.join(str(uuid.uuid4()).split("-")))
try:
	script += end.format(sys.argv[1],sys.argv[2])
except:
	script += end.format(input("IP to listen on: "),int(input("Port: ")))
exec(script)
