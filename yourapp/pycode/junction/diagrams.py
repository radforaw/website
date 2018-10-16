import math
from PIL import Image,ImageDraw

class juncdiag():
	def __init__(self):
		self.image=Image.new('RGB',(400,400),'Black')
		self.draw=ImageDraw.Draw(self.image)
		self.draw.line((0,0,399,0),(255,255,255))
		self.draw.line((399,0,399,399),(255,255,255))
		self.draw.line((399,399,0,399),(255,255,255))
		self.draw.line((0,399,0,0),(255,255,255))
	def dirind(self,x,size=40):
		return [int(math.sin(math.radians((360-x)%360))*size),int(math.cos(math.radians((360-x)%360))*size)]

	def getthis(self,a,m):
		direction={'N':180,'NE':225,'E':270,'SE':315,'S':0,'SW':45,'W':90,'NW':135}
		turn={'SA':0,'L':-90,'R':90,'U':90}
		tmp=self.dirind(direction[a])
		tmp2=self.dirind(direction[a]+turn[m])
		tmp3=[tmp[0]+(tmp2[0]/2),tmp[1]+(tmp2[1]/2)]
		return [[0,0],tmp,tmp3]
		
	def startpoint(self,a,m):
		t=self.getthis(a,m)
		l=[-t[1][0]*5,-t[1][1]*5]
		m=[l[0]+t[2][0],l[1]+t[2][1]]
		return [[m],[[m[0]+t[1][0],m[1]+t[1][1]]],[[m[0]+t[2][0],m[1]+t[2][1]]]]

	def onscreen(self,direction,turn,colour=(128,128,128),width=3,centre=(200,200)):
		k=[]
		for n in self.startpoint(direction,turn):
			for y in n:
				tmp=[]
				tmp.append([centre[0]+y[0],centre[1]+y[1]])
			k.append(tmp[0])
		self.draw.line(k[0]+k[1],colour,width)
		self.draw.line(k[1]+k[2],colour,width)

if __name__=="__main__":
	direction={'N':180,'NE':225,'E':270,'SE':315,'S':0,'SW':45,'W':90,'NW':135}
	turn={'SA':0,'L':-90,'R':90}

	n=juncdiag()
	for a in direction:
		for m in turn:
			n.onscreen(a,m)

	n.image.show()

	n.__init__()

	for a in direction:
		for m in turn:
			n.onscreen(a,m,colour=(255,0,0))

	n.image.show()


