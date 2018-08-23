import math
import requests
try:
	from lxml import etree as ET
except ImportError:
	import xml.etree.cElementTree as ET
import pickle


def osmcreate(tl=(52.4607,-1.8174),br=(52.4681,-1.8031)):
	highwaytypes='motorway','trunk','primary','secondary','tertiary','unclassified','residential','motorway_link','trunk_link','primary_link','secondary_link','tertiary_link','service','living_street'

	url='https://overpass-api.de/api/interpreter?data=[out:xml][timeout:25];('
	for n in highwaytypes:
		url=url+'way["highway"=\"'+n+'\"]('+str(tl[0])+','+str(tl[1])+','+str(br[0])+','+str(br[1])+');'
	url=url+');out;>;out skel qt;'
	getdata = requests.get(url)
	with open('sampledata.pickle', 'wb') as handle:
		pickle.dump(getdata.content, handle)


if __name__=='__main__':
	osmcreate(tl=(52.4577,-1.9309),br=(52.4982,-1.8645))
