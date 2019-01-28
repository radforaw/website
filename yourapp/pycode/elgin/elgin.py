import requests
import andyconfig
import os
import json
import time

def elginget():
	keys={'app_key':os.environ['ELGINKEY']}
	a=requests.get('http://data-api.roadworks.org/',params=keys)
	return a.content

def newdata():
	data={"time":str(time.time()),"data":elginget()}	
	with open('elgincache.json','w') as cachefile:
		json.dump(data,cachefile)
	return data
	
def cache():
	try:
		with open("elgincache.json","r") as cachefile:
			data=json.load(cachefile)
	except IOError:
		data=newdata()
	if time.time()-float(data["time"])>3600:
		data=newdata()
	return data["data"]
	
if __name__=="__main__":
	print cache()
