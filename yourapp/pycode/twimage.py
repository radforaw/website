from __future__ import division
import requests
import json
import io
import math
from PIL import Image

def deg2num(lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = (lon_deg + 180.0) / 360.0 * n
        ytile = (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n
        return (int(xtile),int(ytile))


def matchit(coords):
        sm=True
        x=coords[0]
        for n in coords:
                if n<>x:
                        sm=False
        return sm

def createlist(coords,zoom):
        ret=[]
        for n in coords:
                ret.append(deg2num(n[1],n[0],zoom))
        print ret
        return ret

def countup(coords):
        coords=json.loads(coords)
        n=18
        while not matchit(createlist(coords,n)):
                n-=1
        j= deg2num(coords[0][1],coords[0][0],n)
        m=requests.get("https://tile.openstreetmap.org/"+str(n)+"/"+str(j[0])+"/"+str(j[1])+".png")     
        print m.status_code
        if m.status_code==200:
                print "I got here"
                i = Image.open(io.BytesIO(m.content))
                but2=io.BytesIO()
                i.save(but2,format="png")
                return but2
        return [False]
