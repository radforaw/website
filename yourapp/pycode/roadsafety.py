from PIL import Image,ImageDraw
import math
import io


def compcalc(n):
        ang=(((n-1)*45)+270)%360
        return [int(round(math.cos(math.radians(ang)))), int(round(math.sin(math.radians(ang))))]

def calcalt(a,size=50):
        first=int(a/10)
        second=a%10
        j=[a*size for a in compcalc(second)]
        n=compcalc(second+1)
        m=compcalc(second-1)
        return [[a*size for a in compcalc(first)],[0,0],j,[j[0]-n[0]*5,j[1]-n[1]*5],[j[0]-m[0]*5,j[1]-m[1]*5],j]

def minmax(x,off=[0,0]):
        minx=min([a[0] for a in x])
        miny=min([a[1] for a in x])
        maxx=max([a[0] for a in x])
        maxy=max([a[1] for a in x])
        ox=0-minx
        oy=0-miny
        return {'line':tuple([(a[0]+ox+off[0],a[1]+oy+off[1])for a in x]),'limits':[maxx+ox+1+off[0],maxy+oy+1+off[1]],'centre':[ox+off[0],oy+off[1]]}


def minmaxobj(objs):
        x=[]
        for n in objs:
                for y in n:
                        x.append(y)
        minx=min([a[0] for a in x])
        miny=min([a[1] for a in x])
        maxx=max([a[0] for a in x])
        maxy=max([a[1] for a in x])
        ox=0-minx
        oy=0-miny
        ret=[]
        for b in objs:
                ret.append(tuple([(a[0]+ox,a[1]+oy)for a in b]))
        return {'lines':ret,'limits':[maxx+ox+1,maxy+oy+1]}

def wheredoesitgo(a,limitsa,limitsb):
        loc=((a%10)+4)
        d=compcalc(loc)
        return [((d[0]<0)*-limitsa[0])+((d[0]>0)*limitsb[0]),((d[1]<0)*-limitsa[1])+((d[1]>0)*limitsb[1])]

def quickimage(z,p):
        a=calcalt(z)
        b=minmax(a)
        y=minmax(calcalt(p))
        pos2=wheredoesitgo(p,y['limits'],b['limits'])
        y=minmax(y['line'],pos2)
        res=minmaxobj([b['line'],y['line']])
        col=['blue','red','green']
        c=0
        x=Image.new('RGB',res['limits'],'White')
        draw=ImageDraw.Draw(x)
        for b in res['lines']:
                draw.line(b,fill=col[c%3])
                c+=1
        ret=io.BytesIO()
        x.save(ret,format='PNG')
        return ret

if __name__=='__main__':
        n=(12,23,34,42,57,65,78,84,84)
        m=(41,42,57,65,78,84,23,12,84)
        for d in range(len(n)):
                x=quickimage(n[d],m[d])
                Image.open(x).show()


