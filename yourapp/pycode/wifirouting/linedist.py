from scene import *
import sound
import random
import math
A = Action

def pointlinedistance(line,point):
	x1=line[0][0]
	y1=line[0][1]
	x2=line[1][0]
	y2=line[1][1]
	x3=point[0]
	y3=point[1]
	u=(((x3-x1)*(x2-x1))+((y3-y1)*(y2-y1)))/(((x2-x1)**2)+((y2-y1)**2))
	if u<0.0001 or u>1:
		if ((x3-x1)**2)+((y3-y1)**2)<((x3-x2)**2)+((y3-y2)**2):
			ix=x1
			iy=y1
		else:
			ix=x2
			iy=y2
	else:
		ix = x1 + u * (x2 - x1)
		iy = y1 + u * (y2 - y1)
	d=((ix-x3)**2)+((iy-y3)**2)
	return (ix,iy),d

class MyScene (Scene):
	def setup(self):
		a,b,c,d=67,198,340,500
		self.a,self.b,self.c,self.d=a,b,c,d
		self.mypath=ui.Path()
		self.mypath.move_to(0,0)
		self.mypath.line_to(c-a,b-d)
		self.x=ShapeNode(self.mypath,anchor_point=(0,0),color='white',stroke_color='white',parent=self,position=(a,b))
		self.y=SpriteNode('emj:Basketball',parent=self,position=(100,100),scale=0.5)
	
	def did_change_size(self):
		pass
	
	def update(self):
		pass
	
	def touch_began(self, touch):
		pass
	
	def touch_moved(self, touch):
		for n in self.touches:
			x,y=self.touches[n].location
		r=pointlinedistance(((self.a,self.b),(self.c,self.d)),(x,y))
		print math.sqrt(r[1])
		self.y.position=r[0]
	
	def touch_ended(self, touch):
		pass

if __name__ == '__main__':
	run(MyScene(), show_fps=True)
