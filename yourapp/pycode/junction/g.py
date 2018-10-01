import requests
import time
import location
#import motion
from math import sqrt, pi, sin, cos, tan, atan2


def WGS84toOSGB36(lat, lon):
	""" Accept latitude and longitude as used in GPS.
	Return OSGB grid coordinates: eastings and northings.
	Usage:
	>>> from latlon_to_bng import WGS84toOSGB36
	>>> WGS84toOSGB36(51.4778, -0.0014)
	(538890.1053365842, 177320.49650700082)
	>>> WGS84toOSGB36(53.50713, -2.71766)
	(352500.19520169357, 401400.01483428996)
	"""
	# First convert to radians
	# These are on the wrong ellipsoid currently: GRS80. (Denoted by _1)
	lat_1 = lat*pi/180
	lon_1 = lon*pi/180
	
	# Want to convert to the Airy 1830 ellipsoid, which has the following:
	# The GSR80 semi-major and semi-minor axes used for WGS84(m)
	a_1, b_1 = 6378137.000, 6356752.3141
	e2_1 = 1 - (b_1*b_1)/(a_1*a_1)  # The eccentricity of the GRS80 ellipsoid
	nu_1 = a_1/sqrt(1-e2_1*sin(lat_1)**2)
	
	# First convert to cartesian from spherical polar coordinates
	H = 0  # Third spherical coord.
	x_1 = (nu_1 + H)*cos(lat_1)*cos(lon_1)
	y_1 = (nu_1 + H)*cos(lat_1)*sin(lon_1)
	z_1 = ((1-e2_1)*nu_1 + H)*sin(lat_1)
	
	# Perform Helmut transform (to go between GRS80 (_1) and Airy 1830 (_2))
	s = 20.4894*10**-6  # The scale factor -1
	# The translations along x,y,z axes respectively
	tx, ty, tz = -446.448, 125.157, -542.060
	# The rotations along x,y,z respectively, in seconds
	rxs, rys, rzs = -0.1502, -0.2470, -0.8421
	# In radians
	rx, ry, rz = rxs*pi/(180*3600.), rys*pi/(180*3600.), rzs*pi/(180*3600.)
	x_2 = tx + (1+s)*x_1 + (-rz)*y_1 + (ry)*z_1
	y_2 = ty + (rz)*x_1 + (1+s)*y_1 + (-rx)*z_1
	z_2 = tz + (-ry)*x_1 + (rx)*y_1 + (1+s)*z_1
	
	# Back to spherical polar coordinates from cartesian
	# Need some of the characteristics of the new ellipsoid
	# The GSR80 semi-major and semi-minor axes used for WGS84(m)
	a, b = 6377563.396, 6356256.909
	e2 = 1 - (b*b)/(a*a)  # The eccentricity of the Airy 1830 ellipsoid
	p = sqrt(x_2**2 + y_2**2)
	
	# Lat is obtained by an iterative proceedure:
	lat = atan2(z_2, (p*(1-e2)))  # Initial value
	latold = 2*pi
	while abs(lat - latold) > 10**-16:
		lat, latold = latold, lat
		nu = a/sqrt(1-e2*sin(latold)**2)
		lat = atan2(z_2+e2*nu*sin(latold), p)
		
	# Lon and height are then pretty easy
	lon = atan2(y_2, x_2)
	H = p/cos(lat) - nu
	
	# E, N are the British national grid coordinates - eastings and northings
	F0 = 0.9996012717  # scale factor on the central meridian
	lat0 = 49*pi/180  # Latitude of true origin (radians)
	lon0 = -2*pi/180  # Longtitude of true origin and central meridian (radians)
	N0, E0 = -100000, 400000  # Northing & easting of true origin (m)
	n = (a-b)/(a+b)
	
	# meridional radius of curvature
	rho = a*F0*(1-e2)*(1-e2*sin(lat)**2)**(-1.5)
	eta2 = nu*F0/rho-1
	
	M1 = (1 + n + (5/4)*n**2 + (5/4)*n**3) * (lat-lat0)
	M2 = (3*n + 3*n**2 + (21/8)*n**3) * sin(lat-lat0) * cos(lat+lat0)
	M3 = ((15/8)*n**2 + (15/8)*n**3) * sin(2*(lat-lat0)) * cos(2*(lat+lat0))
	M4 = (35/24)*n**3 * sin(3*(lat-lat0)) * cos(3*(lat+lat0))
	
	# meridional arc
	M = b * F0 * (M1 - M2 + M3 - M4)
	
	I = M + N0
	II = nu*F0*sin(lat)*cos(lat)/2
	III = nu*F0*sin(lat)*cos(lat)**3*(5 - tan(lat)**2 + 9*eta2)/24
	IIIA = nu*F0*sin(lat)*cos(lat)**5*(61 - 58*tan(lat)**2 + tan(lat)**4)/720
	IV = nu*F0*cos(lat)
	V = nu*F0*cos(lat)**3*(nu/rho - tan(lat)**2)/6
	VI = nu*F0*cos(lat)**5*(5 - 18*tan(lat)**2 + tan(lat)**4 + 14*eta2 - 58*eta2*tan(lat)**2)/120
	
	N = I + II*(lon-lon0)**2 + III*(lon-lon0)**4 + IIIA*(lon-lon0)**6
	E = E0 + IV*(lon-lon0) + V*(lon-lon0)**3 + VI*(lon-lon0)**5
	
	# Job's a good'n.
	return E, N

class what():
	def __init__(self):
		self.prev=self.phoneangle()
		self.junctions=self.getlocs()
		self.loc=(0,0)
		self.test=None
		
	def getlocs(self):
		url='http://bcc.opendata.onl/Flow.json'
		a=requests.get(url)
		z={}
		for n in a.json()['Flows']['Flow'][:9]:
			if n['Northing']<>0:
				z[n['SCN']]=[n['Northing'],n['Easting']]
		a=WGS84toOSGB36(52.4549404,-1.7938292)
		z[2115]=[a[1],a[0]] 
		return z
		
	def getlocation(self):
		if self.test<>None:
			n=self.test
		else:
			n=location.get_location()
		b=WGS84toOSGB36(n['latitude'],n['longitude'])
		s=n['speed']
		c=n['course']
		if s==-1:
			s=0
		if s<8:
			c=self.prev
		self.prev=c
		self.loc=(round(b[1],1),round(b[0],1))
		return (round(b[1],1),round(b[0],1)),s,c
		
	def dist(self,a,b):
		x=a[0]-b[0]
		y=a[1]-b[1]
		return sqrt(x*x+y*y)
	
	def angle(self,a,b):
		x=a[0]-b[0]
		y=a[1]-b[1]
		r=atan2(y,x)*(180/pi)
		#if r<0:
		#	r+=180
		return r%360
	
	def phoneangle(self):
		motion.start_updates()
		x=motion.get_magnetic_field()
		return (atan2(x[1],x[0])*(180/pi))%360
	
	def getarm(self,angle):
		#simple version
		# 0 S 1 W 2 N 3 E
		return int(((angle+45)%360)/90)
	
	def nearestjunction(self):
		a,b,p=self.getlocation()
		res=[]
		y=self.junctions
		for n in y:
			d=(p-self.angle(a,y[n])-90)%360
			j=self.dist(a,y[n])
			if d<180 and j<300:
				res.append([j,self.angle(a,y[n]),n,d,y[n]])
		try:
			return sorted(res)[0],self.getarm(p)
		except:
			return False



def testidea():
	j=what()
	a=time.time()
	print j.nearestjunction()
	print j.prev
	print time.time()-a
	import canvas
	canvas.set_size(256,256)
	x=[]
	for n in j.junctions:
		x.append(j.junctions[n])
	
	mn=[min(x)[0],min(x, key=lambda a:a[1])[1]]
	mx=[max(x)[0],max(x, key=lambda a:a[1])[1]]
	ml=(mx[0]-mn[0])/256.0
	mf=(mx[1]-mn[1])/256.0
	md=max([ml,mf])
	print mn,mx
	print ml,mf
	for n in x:
		canvas.draw_ellipse((n[0]-mn[0])/md,256-(n[1]-mn[1])/md,2,2)
	canvas.set_stroke_color(255,0,0)
	canvas.draw_ellipse((j.loc[0]-mn[0])/md,256-(j.loc[1]-mn[1])/md,2,2)
	
	canvas.set_stroke_color(0,255,255)
	d=j.nearestjunction()[0]
	x=[]
	for n in d:
		x.append(n[4])
	for n in x:
		canvas.draw_ellipse((n[0]-mn[0])/md,256-(n[1]-mn[1])/md,2,2)

