import getmap
import diagrams
from PIL import Image,ImageDraw,ImageFont
import StringIO


def main(junc):
	dirs=getmap.thismap(junc).directions()
	image=diagrams.juncdiag()
	n=sorted(j for j in dirs)
	print len(n)
	w=450
	til = Image.new("RGB",(w*3,w*int((len(n)+1)/3)),"White")
	for m in range(len(n)):
		image.__init__()
		for a in dirs:
			for b in dirs[a]:
				image.onscreen(b[0],b[1])
		for b in dirs[n[m]]:
			image.onscreen(b[0],b[1],colour=(255,0,0),width=2)
		til.paste(image.image,(w*(m%3),w*int(m/3)))
		ImageDraw.Draw(til).text(((w*(m%3))+20, (w*int(m/3))+20),chr(64+int(n[m])),(0, 0, 0))
	buf=StringIO.StringIO()
	til.save(buf,format='PNG')
	return buf

if __name__=='__main__':
	main(2111)
