from __future__ import print_function
from flask import Flask
from flask import make_response, request, render_template
import time
import os
import csv
import datetime

import pycode
import pycode.wifirouting.graphs as gph
import pycode.wifirouting.sortapp as fol
import pycode.wifirouting.VMS as vmslist
import pycode.wifirouting.vboard as brd
import pycode.junction.together as jnc
import pycode.junction.getmap as gmp
import pycode.junction.elgintest as stwk
import pycode.buses.tomsgraph as tgph


app = Flask(__name__,static_url_path="/static")

@app.route("/")
def hello():
	return render_template("base.html")

@app.route("/stick")
def stick():
	print('Received Call')
	print('/')
	print('IP:', request.remote_addr)
	print(request.args)
	args=request.args.to_dict()
	print(args['v1'])
	buf=pycode.quickimage(int(args['v1']),int(args['v2']))
	buf.seek(0)
	response = make_response(buf.read())

	response.headers.set('Content-Type', 'image/png')
	response.headers.set('Content-Disposition', 'inline')
	return response

@app.route("/twentyform")
def twentyform():
	print('Received Call')
	print('/')
	print('IP:', request.remote_addr)
	print(request.args)
	args=request.args.to_dict()
	ret="Error - you should have typed a street name"
	if 'road' in args:
		#print(args['road'])
		ret="<H1>Nope,it's not in a twenty (or I can't find the street name)"
		a=pycode.ismyroad(args['road'])
		if a[0]:
			print (str(a[1]))
			ret="<H1>Yep, it's in a twenty <IMG SRC=\'/getpic.png?coords="+str(a[1])+"\'</IMG>"
	return ret

@app.route("/getpic.png")
def helo():

	args = request.args.to_dict()
	#print args
	buf=pycode.countup(args['coords'])
	buf.seek(0)
	response = make_response(buf.read())
	response.headers.set('Content-Type', 'image/png')
	response.headers.set('Content-Disposition', 'attachment')
	return response

@app.route("/twenty")
def twenty():
	retval="<!DOCTYPE html><html><body>"
	retval+='<form action="twentyform" method="get" target="_self">'
	retval+='Type your road name: <input type="text" name="road">'
	retval+='<input type="submit" value="Submit">'
	retval+='</form></body></html>'
	return retval


@app.route("/map")
def mapper():
	return fol.main()

@app.route("/graph.png")
def graph():
	args=request.args.to_dict()
	if 'scn' in args:
		response = make_response(gph.drawagraph(args['scn']).img.read())
		response.headers.set('Content-Type', 'image/png')
		response.headers.set('Content-Disposition', 'inline')
		return response

@app.route("/vms")
def vms():
	return vmslist.main()
	
@app.route("/board.png")
def board():
	args=request.args.to_dict()
	if 'text' in args:
		print (args)
		buf=(brd.sentence(args['text']))
		buf.seek(0)
		response = make_response(buf.read())
		response.headers.set('Content-Type', 'image/png')
		response.headers.set('Content-Disposition', 'inline')
		return response

@app.route("/junction.png")
def junction():
	args=request.args.to_dict()
	if 'junc' in args:
		buf=(jnc.main(int(args['junc'])))
		buf.seek(0)
		response = make_response(buf.read())
		response.headers.set('Content-Type', 'image/png')
		response.headers.set('Content-Disposition', 'inline')
		return response

@app.route("/mapdraw.png")
def mapdraw():
	args=request.args.to_dict()
	if 'junc' in args:
		buf=(gmp.thismap(int(args['junc'])).drawit())
		buf.seek(0)
		response = make_response(buf.read())
		response.headers.set('Content-Type', 'image/png')
		response.headers.set('Content-Disposition', 'inline')
		return response

@app.route("/streetworks.png")
def streetworks():
	args=request.args.to_dict()
	if 'days' in args:
		buf=stwk.showgraph(days=int(args['days']))
	else:
		buf=stwk.showgraph()
	response = make_response(buf)
	response.headers.set('Content-Type', 'image/png')
	response.headers.set('Content-Disposition', 'inline')
	return response
	
@app.route("/temp")
def temperature():
	print (os.getcwd())
	args=request.args.to_dict()
	if 'current' in args:
		with open("tmplist.txt","a+") as openfile:
			openfile.write(str(time.time())+","+str(args['current']+"\n"))
	if 'humid' in args:
		with open("humlist.txt","a+") as openfile:
			openfile.write(str(time.time())+","+str(args['humid']+"\n"))
	return "Thanks"


@app.route("/humget")
def humget():
	with open("humlist.txt","r") as fl:
		ret=fl.read()
	return ret

@app.route("/tempget")
def tempget():
	with open("tmplist.txt","r") as fl:
		ret=fl.read()
	return ret
	
@app.route("/worst")
def worst():
	fileloc='/home/ubuntu/website/website/yourapp/static/'
	with open(fileloc+"tesfile.csv","r") as csvfile:
		reader=csv.reader(csvfile)
		reader.next()
		passer=[]
		for row in reader:
			n=datetime.datetime.strptime(row[1]+" 2018","%a, %d %b %Y")
			print (n)
			j=int((datetime.datetime.now()-n).total_seconds()/84600)
			print (j)
			passer.append(row + [str(j)])
	return render_template('tables.html', posts=passer)

@app.route("/tom.png")
def tom():
	args=request.args.to_dict()
	buf=tgph.dailygraph(args['route'],int(args['day']))
	buf.seek(0)
	response = make_response(buf.read())
	response.headers.set('Content-Type', 'image/png')
	response.headers.set('Content-Disposition', 'inline')
	return response
	
	
