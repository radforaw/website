import csv
import requests
import json


url='https://taginfo.openstreetmap.org.uk/api/4/key/values?key=highway&page=1&rp=50&sortname=count_ways&sortorder=desc&filter=ways'
msurl='https://taginfo.openstreetmap.org.uk/api/4/key/values?key=maxspeed&page=1&rp=50&sortname=count_ways&sortorder=desc&filter=ways'


n=requests.get(url)
x=json.loads(n.content)
for n in x['data']:
	print n[u'value'],n[u'count'],n[u'description']
highwaytypes='motorway','trunk','primary','secondary','tertiary','unclassified','residential','motorway_link','trunk_link','primary_link','secondary_link','tertiary_link','service','living_street'

with open('zweights.csv','w') as csvfile:
	wr=csv.writer(csvfile)
	wr.writerow(['key','value','description','car','cycle','walk','lorry'])
	for n in x['data']:
		if int(n[u'count'])>1000:
			wr.writerow(['highway',str(n[u'value']),str(n[u'description']),1,1,1,1])
