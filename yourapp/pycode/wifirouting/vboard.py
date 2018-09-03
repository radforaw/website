from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import StringIO

def board(letter):
	image=Image.new('RGB',(7,8),'white')
	ImageDraw.Draw(image).text((1, -2),letter,(0, 0, 0))
	
	pic=image.load()
	im2=Image.new('RGB',(56,64),'black')
	draw=ImageDraw.Draw(im2)
	for x in range(7):
		for y in range(8):
			col='#333300'
			if pic[x,y][0]==0:
				col='yellow'
			draw.ellipse((((x*8)+2,(y*8)+2),((x*8)+6,(y*8)+6)),fill=col)

	return im2

def sentence(words):
	words=words.split('|')
	j=len(words)
	l=max([len(x) for x in words])
	pic=Image.new('RGB',((l*56),j*64),'white')
	v=0
	for word in words:
		w=centrewords(word,l)
		for x in range(l):
			pic.paste(board(w[x]),(x*56,v*64))
		v+=1
	out=StringIO.StringIO()
	pic.save(out,'PNG')
	
	return pic
	
def centrewords(w,l):
	x=len(w)
	j=''
	for n in range((l-x)/2):
		j+=' '
	k=''
	for n in range(l-(len(j)+x)):
		k+=' '
	return j+w.upper()+k

if __name__=='__main__':
	x=sentence('air zone')
	x.show()
