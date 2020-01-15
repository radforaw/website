#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  shortest_path_producer.py
#  
#  Copyright 2019  <pi@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

#import main
import requests
import datetime
import sampleget
import shortest
import geometry
import pickle
'''
data_to_work_with={'route number':{'coordinates':((coordinate1x,coordinate1y),(coordinate1x,coordinate1y),(coordinate1x,coordinate1y),(coordinate1x,coordinate1y)),'next route':((c2x,c2y),(c2x,c2y))}

{'WiFiL43': {'matched': '6', 'Description': 'Coventry Rd WB E2112 to E1994', 'coordinates': [(52.45326978440362, -1.788729813339725), (52.462406043963846, -1.8237288169225503)], 'Time': '0'}, 'WiFiL41': {'matched': '8', 'Description': 'Coventry Rd WB E2112 to E2130', 'coordinates': [(52.45326978440362, -1.788729813339725), (52.45893844389956, -1.8003969207202497)], 'Time': '101'}}
'''


routes={'Ashted-Circus-inbound':(43000242503,43002104401),'Ashted-Circus-outbound':(43002104402,43000242601),
	'Bristol-Road-outbound':(42000204701,43000342304),'Bristol-Road-inbound':(43000342303,43000201702),
	'Selly-Oak-Inbound':(43000352101,43000345201),'Holloway-Circus-inbound':(43000305101,43000203501),
	'Five-Ways-inbound':(43000301102,43000207102),'Spring-Hill-inbound':(43000286602,43000207202),
	'St-Chads-inbound':(43000276503,43000208501),'Dartmouth-Circus-inbound':(43000253404,43000207601),
	'Curzon-Circus-inbound':(43000241402,43002104401),'Garrison-Circus-inbound':(43000236202,43000211304),
	'Bordesley-Circus-inbound':(43000230203,43000202203),'Camp-Hill-Circus-inbound':(43000220102,43000211304),
	'Bradford-Street----Markets-inbound':(43000218202,43000202301),'Belgrave-Interchange-inbound':(43000343202,43000203902),
	'harborne-outbound':(43000205601,43000305201),'Five-Ways-outbound':(43000205601,43003003501),
	'Spring-Hill-outbound':(43000205601,43002870101),'St-Chads-outbound':(43000207205,43000276301),
	'Dartmouth-outbound':(43000252102,43000253601),'Curzon-outbound':(43002104402,43000241502),
	'Garrison-outbound':(43000212601,43000236402),'Camp-Hill-outbound':(43000211501,43000220201),
	'Bordesley-outbound':(43000211502,43000230302),'Moseley-outbound':(43002103506,43000218101),'Pershore-outbound':(43000213202,43000343201)}
for r in routes:
    route=routes[r]

a=requests.get('https://realjourneytime.azurewebsites.net/index.php?method=AllStops').json()
stoplookup={n['stop_id']:(n['stop_lat'],n['stop_lon']) for n in a}


dy=datetime.datetime.now()
tm=dy.strftime('%Y-%m-%d')	
url='https://realjourneytime.azurewebsites.net/index.php?method=Journeys&fromCode='+str(route[0])+'&toCode='+str(route[1])+'&dateString='+tm


res=[geometry.WGS84toOSGB36(*stoplookup[str(route[0])])]
print route
rt=requests.get('https://realjourneytime.azurewebsites.net/index.php?method=StopsFromStop&fromCode='+str(route[0])).json()
#import json
#print json.dumps(rt,indent=2)

for n in rt:
    if n['stop_id']==str(route[1]):
        break
    res.append(geometry.WGS84toOSGB36(n['stop_lat'],n['stop_lon']))
    print n['stop_id'], n['stop_name']

import sys
sys.exit(0)
    
    
print res

l1=[geometry.OSGB36toWGS84(k[0],k[1]) for k in res]
tl=(min([k[0] for k in l1]),min([k[1] for k in l1]))
br=(max([k[0] for k in l1]),max([k[1] for k in l1]))

#print tl,br
sampleget.osmcreate(tl=tl,br=br)
with open('sampledata.pickle', 'r') as handle:
    dat=pickle.load(handle)
    
a,b=shortest.OsmRouteImport(dat)

res1=[]
for d in range(len(res)-1):
    #start point
    t=shortest.getlocsa(res[d],b,a,None)
    ln=min([[shortest.distance(res[d],n[0]),n] for n in t])[1][1]
    print ln
    plt=res[0]
    #end point
    t=shortest.getlocsa(res[d+1],b,a,None)
    ln1=min([[shortest.distance(res[d+1],n[0]),n] for n in t])[1][1]
    plt1=res[1]


    v=shortest.setupshortest(plt, ln, plt1, ln1, None, b, a, None)
    #n=[shortest.offset(a[0],a[1]) for a in n[1]
    try:
        res1+=[geometry.OSGB36toWGS84(z[0],z[1]) for z in v[1]]
    except:
        break

print res1
import folium
m=folium.Map( location=[52.4,-1.9],zoom_start=12)


folium.PolyLine(res1,color="green",weight=2.5).add_to(m)
    
m.save("testofnewmap.html")

