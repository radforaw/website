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
'''
data_to_work_with={'route number':{'coordinates':((coordinate1x,coordinate1y),(coordinate1x,coordinate1y),(coordinate1x,coordinate1y),(coordinate1x,coordinate1y)),'next route':((c2x,c2y),(c2x,c2y))}

{'WiFiL43': {'matched': '6', 'Description': 'Coventry Rd WB E2112 to E1994', 'coordinates': [(52.45326978440362, -1.788729813339725), (52.462406043963846, -1.8237288169225503)], 'Time': '0'}, 'WiFiL41': {'matched': '8', 'Description': 'Coventry Rd WB E2112 to E2130', 'coordinates': [(52.45326978440362, -1.788729813339725), (52.45893844389956, -1.8003969207202497)], 'Time': '101'}}
'''


routes={'Holloway-Circus-inbound':(43000305101,43000203501)}

a=requests.get('https://realjourneytime.azurewebsites.net/index.php?method=AllStops').json()
stoplookup={n['stop_id']:(n['stop_lat'],n['stop_lon']) for n in a}



dy=datetime.datetime.now()
tm=dy.strftime('%Y-%m-%d')	
url='https://realjourneytime.azurewebsites.net/index.php?method=Journeys&fromCode='+str(route[0])+'&toCode='+str(route[1])+'&dateString='+tm


res=[stoplookup[route[0]]]

rt=requests.get('https://realjourneytime.azurewebsites.net/index.php?method=StopsFromStop&fromCode='+str(route[0])).json()

for n in rt:
    if n['stop_id']==str(route[1]):
        break
    res.append((n['stop_lat'],n['stop_lon']))
    
print res
