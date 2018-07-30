from __future__ import print_function
from waitress import serve
from flask import Flask
from flask import make_response, request
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import sys
import roadsafety
import numpy as np
import twmph
import twimage
import logging

logger=logging.getLogger('waitress')
logger.setLevel(logging.DEBUG)

app = Flask(__name__,static_url_path="/static")


def draw_graph():
    x = [np.random.randint(10) for _ in range(10)]
    y = [np.random.randint(10) for _ in range(10)]

    plt.plot(x, y)
    buf=io.BytesIO()
    plt.savefig(buf,format='png')
    plt.clf()
    return buf

@app.route("/")
def hello():
    retval="<center><H1>Welcome to my page</H1><BR>"
    retval+="<H3>Menu</H3><P>"
    retval+="<a href='stick?v1=15&v2=62'>Stick Diagrams</a>"
    retval+="<BR><i>syntax = <B>/stick?v1=18&v2=24</B>"
    retval+="<LI><i>where v is <B>vehicle number</b>"
    retval+="<LI><i>1-8 are compass points representing <B>from</B> and <B>to</B></i>"
    retval+="<BR><a href='twenty'>Is my road 20mph?</a>"
    return retval

@app.route("/stick")
def stick():
    print('Received Call', file=sys.stderr)
    print('/', file=sys.stderr)
    print('IP:', request.remote_addr, file=sys.stderr)
    print(request.args, file=sys.stderr)
    args=request.args.to_dict()
    print(args['v1'])
    buf=roadsafety.quickimage(int(args['v1']),int(args['v2']))
    buf.seek(0)
    response = make_response(buf.read())

    response.headers.set('Content-Type', 'image/png')
    response.headers.set('Content-Disposition', 'inline')
    return response

@app.route("/twentyform")
def twentyform():
    print('Received Call', file=sys.stderr)
    print('/', file=sys.stderr)
    print('IP:', request.remote_addr, file=sys.stderr)
    print(request.args, file=sys.stderr)
    args=request.args.to_dict()
    ret="Error - you should have typed a street name"
    if 'road' in args:
        #print(args['road'])
        ret="<H1>Nope,it's not in a twenty (or I can't find the street name)"
        a=twmph.ismyroad(args['road'])
        if a[0]:
            print (str(a[1]))
            ret="<H1>Yep, it's in a twenty <IMG SRC=\'/getpic.png?coords="+str(a[1])+"\'</IMG>"
    return ret

@app.route("/getpic.png")
def helo():

    args = request.args.to_dict()
    #print args
    buf=twimage.countup(args['coords'])
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


if __name__ == '__main__':
    serve(app, listen='0.0.0.0:80')
