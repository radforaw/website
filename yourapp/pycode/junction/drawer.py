from PIL import Image, ImageDraw


class drawing():
	
	def __init__(self,original,screen):
		self.minx=original[0]
		self.miny=original[2]
		self.sx,self.sy=screen[0],screen[1]
		self.width=original[1]-original[0]
		self.height=original[3]-original[2]
		self.scalex=screen[0]/float(self.width)
		self.scaley=screen[1]/float(self.height)
		self.image=Image.new('RGB',screen,'White')
		self.pixels=self.image.load()
		self.draw=ImageDraw.Draw(self.image)
		
	def convert(self,x,y):
		rx=(x-self.minx)*self.scalex
		ry=(y-self.miny)*self.scaley
		return rx,self.sy-ry
		
	def plot(self,x,y,color=(0,0,0)):
		self.pixels[self.convert(x,y)]=color
		
	def line(self,a,b,color=(0,0,0)):
		
		self.draw.line((self.convert(*a),self.convert(*b)),color)
		
		
if __name__=='__main__':
	x=drawing((100,10000,500,30000),(640,480))
	for t in range(100,400):
		x.plot(t,800)
	print x.scalex,x.scaley
	x.line((300,300),(800,2000),(255,0,0))
	x.image.show()
