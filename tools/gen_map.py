import numpy as np, cv2, math
from PIL import Image
W,H=1900,2516; S=1.0
R=np.random.default_rng(5)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)

def noise(cell,seed):
    r=np.random.default_rng(seed).random((H//cell+3,W//cell+3)).astype(np.float32)
    return cv2.resize(r,(W,H),interpolation=cv2.INTER_CUBIC)[:H,:W]
def fbm(seed,base=400,octs=5):
    v=np.zeros((H,W),np.float32);a=1;t=0
    for o in range(octs):
        v+=a*noise(max(2,int(base/(2**o))),seed+o*7);t+=a;a*=0.55
    v/=t; return (v-v.min())/(v.max()-v.min())
def C(*c): return np.array(c,np.float32)
def mix(img,col,a):
    a=np.clip(a,0,1)[...,None]; return img*(1-a)+col*a

def cr(pts,step=5):
    pts=np.array(pts,float)
    if len(pts)<3:
        n=max(2,int(np.linalg.norm(pts[1]-pts[0])/step)); return np.linspace(pts[0],pts[1],n)
    P=np.vstack([pts[0]*2-pts[1],pts,pts[-1]*2-pts[-2]]); out=[]
    for i in range(1,len(P)-2):
        p0,p1,p2,p3=P[i-1],P[i],P[i+1],P[i+2]
        n=max(2,int(np.linalg.norm(p2-p1)/step))
        for t in np.linspace(0,1,n,endpoint=False):
            out.append(0.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3))
    out.append(P[-2]); return np.array(out)
def wob(c,amp,seed):
    r=np.random.default_rng(abs(int(seed))); s=np.cumsum(np.r_[0,np.linalg.norm(np.diff(c,axis=0),axis=1)])
    d=np.zeros_like(c)
    for k in range(2):
        f=r.uniform(0.008,0.025)*(k+1); ph=r.uniform(0,6.28,2)
        d[:,0]+=amp/(k+1)*np.sin(s*f+ph[0]); d[:,1]+=amp/(k+1)*np.sin(s*f*1.2+ph[1])
    return c+d
def path(pts,amp=1.2,seed=0): return wob(cr(pts),amp,seed)*S
def stroke(mask,c,w,val=255):
    pts=np.int32(np.round(c*4)).reshape(-1,1,2)
    cv2.polylines(mask,[pts],False,val,max(1,int(round(w*S))),cv2.LINE_AA,shift=2)
def line(mask,pts,w,amp=1.2,seed=0,val=255):
    stroke(mask,path(pts,amp,seed),w,val)
def ring(mask,c,r,w):
    cv2.circle(mask,(int(c[0]*S*4),int(c[1]*S*4)),int(r*S*4),255,max(1,int(w*S)),cv2.LINE_AA,shift=2)
def pinside(poly,p): return cv2.pointPolygonTest(np.float32(poly),(float(p[0]),float(p[1])),False)>=0

# ================= ТЕКСТУРА (потертий метал/фарба) =================
base=fbm(1,520,6)
tex=mix(np.broadcast_to(C(112,111,94),(H,W,3)).copy(),C(158,153,126),base)
hue=fbm(20,800,3)
tex+=(hue[...,None]-0.5)*C(-14,4,10)*1.6
dk=np.clip((fbm(25,350,5)-0.55)*3,0,1); tex=mix(tex,C(92,92,80),dk*0.45)
cl=np.clip((fbm(30,650,6)-0.56)*2.6,0,1)**1.4
tex=mix(tex,C(212,212,198),cl*0.78)
# іржа
rm=np.clip((fbm(40,420,6)-0.6)*4.0,0,1)*(0.3+0.7*fbm(45,90,4))
tex=mix(tex,C(178,124,64),rm*0.55)
rm2=np.clip((fbm(48,90,4)-0.8)*7,0,1)*np.clip(rm*3,0,1); tex=mix(tex,C(170,110,52),rm2*0.4)
# протерті смуги
st=R.random((H//2,W//2)).astype(np.float32)
st=cv2.GaussianBlur(st,(0,0),sigmaX=36,sigmaY=0.7)
M=cv2.getRotationMatrix2D((W//4,H//4),-14,1.25); st=cv2.warpAffine(st,M,(W//2,H//2),borderMode=cv2.BORDER_REFLECT)
st=cv2.resize(st,(W,H)); st=(st-st.mean())/st.std()
tex+=st[...,None]*2.0
tex+=(R.random((H,W)).astype(np.float32)[...,None]-0.5)*11
tex+=(noise(4,77)[...,None]-0.5)*10

def scratches(n,seed,lmin,lmax,curv,widths):
    r=np.random.default_rng(seed); m=np.zeros((H,W),np.uint8)
    for i in range(n):
        x,y=r.uniform(0,W),r.uniform(0,H); a=r.uniform(0,6.28) if r.random()<0.5 else r.normal(-0.5,0.5)
        L=r.uniform(lmin,lmax); k=6; p=[(x,y)]
        for j in range(k): a+=r.normal(0,curv); x+=math.cos(a)*L/k; y+=math.sin(a)*L/k; p.append((x,y))
        cv2.polylines(m,[np.int32(np.array(p)*4)],False,int(r.uniform(90,255)),int(r.choice(widths)),cv2.LINE_AA,shift=2)
    return cv2.GaussianBlur(m,(0,0),0.6).astype(np.float32)/255
sc_w=scratches(520,101,20,200,0.25,[1,1,2])
sc_w=np.maximum(sc_w,scratches(70,102,200,700,0.08,[1,2]))
sc_d=scratches(160,103,15,120,0.3,[1,2])
tex=mix(tex,C(108,104,90),sc_d*0.35)


import json
GJ=json.load(open('osm_export.geojson'))['features']
LON0,LON1,LAT1,LAT0=30.5055,30.5350,50.4710,50.4461
def P(lon,lat): return ((lon-LON0)/(LON1-LON0)*W,(LAT1-lat)/(LAT1-LAT0)*H)
def coords(g):
    t=g['type']
    if t=='LineString': return [[P(*c) for c in g['coordinates']]]
    if t=='Polygon': return [[P(*c) for c in r] for r in g['coordinates']]
    return []
def centroid(f):
    r=coords(f['geometry'])[0]; a=np.array(r); return a.mean(axis=0)
def pnt(a): return np.int32(np.round(np.array(a)*4)).reshape(-1,1,2)

# ---------- ДНІПРО ----------
SHLL=[(50.4800,30.5392),(50.4755,30.5366),(50.4730,30.5344),(50.4705,30.5311),(50.4690,30.5280),(50.4680,30.5256),(50.4655,30.5262),(50.4630,30.5266),(50.4605,30.5272),(50.4580,30.5306),(50.4555,30.5361),(50.4530,30.5425),(50.4505,30.5478),(50.4480,30.5530),(50.4455,30.5563),(50.4400,30.5580),(50.4350,30.5590)]
SHLL=[(50.4800,30.5392),(50.4755,30.5366),(50.4730,30.5344),(50.4705,30.5311),(50.4690,30.5280),(50.4680,30.5256),(50.4655,30.5262),(50.4630,30.5266),(50.4605,30.5272),(50.4580,30.5306),(50.4555,30.5361),(50.4530,30.5425),(50.4505,30.5478),(50.4480,30.5530),(50.4455,30.5563),(50.4400,30.5580),(50.4350,30.5590)]
sp=np.array([P(lo,la) for la,lo in SHLL])
sc_=cr(sp,6); sc_=wob(sc_,22,7)
edgex_pts=sc_
wm=np.zeros((H,W),np.uint8)
poly=np.vstack([sc_,[(W+50,sc_[-1][1]),(W+50,-50),(sc_[0][0],-50)]])
cv2.fillPoly(wm,[pnt(poly)],255,shift=2)
dxx=(noise(120,24)-0.5)*26; dyy=(noise(120,25)-0.5)*26
wm=cv2.remap(wm,(xx+dxx).astype(np.float32),(yy+dyy).astype(np.float32),cv2.INTER_LINEAR)
def edgex_f(y): 
    o=np.argsort(edgex_pts[:,1]); return np.interp(y,edgex_pts[o,1],edgex_pts[o,0])
edgex=np.array([edgex_f(y) for y in range(H)])
wmf=cv2.GaussianBlur(wm,(0,0),1.4).astype(np.float32)/255
dist=cv2.distanceTransform((wm>127).astype(np.uint8),cv2.DIST_L2,5)
deep=np.clip(dist/230,0,1)
water=mix(np.broadcast_to(C(92,170,178),(H,W,3)).copy(),C(46,124,142),deep)
water+=(fbm(60,200,5)[...,None]-0.5)*C(20,28,28)
fl=np.zeros((H,W),np.uint8); fl2=np.zeros((H,W),np.uint8)
for k in range(520):
    y0=R.uniform(0,0.78*H); off=R.uniform(10,300); L_=int(R.uniform(30,90)); seg=[]
    for j in range(L_):
        y=y0+j*R.uniform(8,14); 
        if y>=0.80*H: break
        ex=edgex[int(y)]; seg.append((ex+off+8*math.sin(j*0.35+k),y))
    if len(seg)<3: continue
    tgt=fl if k%3 else fl2
    cv2.polylines(tgt,[pnt(seg)],False,255,int(R.choice([2,3,4,6])),cv2.LINE_AA,shift=2)
fl=cv2.GaussianBlur(fl,(0,0),1.2).astype(np.float32)/255; fl2=cv2.GaussianBlur(fl2,(0,0),1.0).astype(np.float32)/255
water=mix(water,C(150,208,206),fl*0.35); water=mix(water,C(36,108,126),fl2*0.35)
glint=np.clip((fbm(66,40,3)-0.72)*6,0,1)*fl; water=mix(water,C(230,242,236),glint*0.6)
band=lambda m,px: cv2.GaussianBlur(cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(px,px))),(0,0),2.5).astype(np.float32)/255
sand=np.clip(band(wm,39)-wmf,0,1)*(0.55+0.45*noise(10,23))
tex=mix(tex,C(206,170,104),sand*0.8)
tex=mix(tex,water,wmf)
edge=np.clip(band(wm,5)-cv2.GaussianBlur(cv2.erode(wm,np.ones((3,3),np.uint8)),(0,0),1).astype(np.float32)/255,0,1)

# ---------- ПАРКИ ----------
pmask=np.zeros((H,W),np.uint8)
for f in GJ:
    p=f['properties']
    if p.get('leisure')=='park' and f['geometry']['type']=='Polygon':
        cv2.fillPoly(pmask,[np.int32(np.array(coords(f['geometry'])[0]))],255)
pmask=cv2.bitwise_and(pmask,cv2.bitwise_not(wm))
pm=cv2.GaussianBlur(pmask,(0,0),1.3).astype(np.float32)/255
g=mix(np.broadcast_to(C(92,122,92),(H,W,3)).copy(),C(128,148,108),fbm(70,120,4))
dab=np.zeros((H,W),np.uint8); dab2=np.zeros((H,W),np.uint8)
ys,xs=np.nonzero(pmask[::6,::6])
for k in R.choice(len(xs),min(len(xs),3500),replace=False):
    x,y=xs[k]*6+R.uniform(-3,3),ys[k]*6+R.uniform(-3,3)
    tgt=dab if R.random()<0.55 else dab2
    cv2.circle(tgt,(int(x*4),int(y*4)),int(R.uniform(3,8)*4),255,-1,cv2.LINE_AA,shift=2)
dab=cv2.GaussianBlur(dab,(0,0),1.5).astype(np.float32)/255; dab2=cv2.GaussianBlur(dab2,(0,0),1.2).astype(np.float32)/255
g=mix(g,C(70,102,78),dab*0.35); g=mix(g,C(150,166,122),dab2*0.25)
tex=mix(tex,g,pm*0.82)
pedge=np.clip(cv2.GaussianBlur(pmask,(0,0),1.2).astype(np.float32)/255-cv2.GaussianBlur(cv2.erode(pmask,np.ones((5,5),np.uint8)),(0,0),1.2).astype(np.float32)/255,0,1)
tex=mix(tex,C(58,82,62),pedge*0.6)

# ---------- ДОРОГИ ----------
brd=np.zeros((H,W),np.uint8); road=np.zeros((H,W),np.uint8); gap=np.zeros((H,W),np.uint8); thin=np.zeros((H,W),np.uint8)
WD={'primary':17,'primary_link':12,'secondary':14,'secondary_link':10,'tertiary':11,'unclassified':9,'residential':8,'living_street':8,'pedestrian':7,'track':3}
order=['track','pedestrian','living_street','residential','unclassified','tertiary','secondary_link','secondary','primary_link','primary']
sdn=0
def draw(f,w,avenue=False):
    global sdn
    for ring in coords(f['geometry']):
        if len(ring)<2: continue
        sdn+=1; c=wob(np.array(ring,float),0.8,sdn)
        pts=pnt(c)
        if f['properties'].get('bridge') and f['properties'].get('highway') in ('primary','secondary','secondary_link','primary_link','tertiary'): cv2.polylines(brd,[pts],False,255,max(1,int(w)),cv2.LINE_AA,shift=2)
        cv2.polylines(road,[pts],False,255,max(1,int(round(w*(1+0.06*math.sin(sdn))))),cv2.LINE_AA,shift=2)
        if avenue: cv2.polylines(gap,[pts],False,255,max(1,int(w*0.38)),cv2.LINE_AA,shift=2)
for hw in order:
    for f in GJ:
        p=f['properties']
        if p.get('highway')==hw and f['geometry']['type']=='LineString' and not p.get('tunnel') and p.get('highway')!='proposed' and p.get('highway')!='construction':
            av=(hw=='primary' and p.get('lanes') is not None and int(str(p.get('lanes')).split(';')[0] or 0)>=4) or (p.get('name') in ('Хрещатик','Набережне шосе'))
            draw(f,WD[hw],av)
for f in GJ:
    p=f['properties']
    if p.get('highway')=='service' and f['geometry']['type']=='LineString':
        for ring in coords(f['geometry']):
            if len(ring)>=2: cv2.polylines(thin,[pnt(ring)],False,255,3,cv2.LINE_AA,shift=2)
    if p.get('highway')=='steps' and f['geometry']['type']=='LineString':
        for ring in coords(f['geometry']):
            if len(ring)>=2: cv2.polylines(thin,[pnt(ring)],False,255,2,cv2.LINE_AA,shift=2)
nb=0
for f in GJ:
    p=f['properties']
    if 'building' in p and f['geometry']['type']=='Polygon':
        r=np.array(coords(f['geometry'])[0])
        if len(r)<4: continue
        a=cv2.contourArea(np.float32(r))
        if a<35: continue
        cv2.polylines(thin,[pnt(r)],True,255,3,cv2.LINE_AA,shift=2); nb+=1
print('будинків',nb)
bfill=np.zeros((H,W),np.uint8)
for f in GJ:
    if 'building' in f['properties'] and f['geometry']['type']=='Polygon':
        r=np.array(coords(f['geometry'])[0])
        if len(r)>=4: cv2.fillPoly(bfill,[np.int32(r)],255)
bff=cv2.GaussianBlur(bfill,(0,0),0.8).astype(np.float32)/255

# ================= ЗБІРКА =================
rd=cv2.GaussianBlur(road,(0,0),0.7).astype(np.float32)/255
gp=cv2.GaussianBlur(gap,(0,0),0.7).astype(np.float32)/255
th=cv2.GaussianBlur(thin,(0,0),0.6).astype(np.float32)/255
roadd=cv2.GaussianBlur(cv2.dilate(road,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))),(0,0),1).astype(np.float32)/255
th=th*(1-roadd)
ink=C(50,50,46); inkcol=tex*0.22+ink*0.78
out=tex.copy()
out=mix(out,out*0.9+C(60,58,50)*0.1,bff*(1-wmf)*(1-pm)*0.5)
brf=cv2.GaussianBlur(brd,(0,0),0.7).astype(np.float32)/255
rd=np.maximum(rd,brf)
rd=rd*(1-wmf*0.98*(1-brf))
out=mix(out,inkcol,rd*0.92)
out=mix(out,tex*0.85+C(196,192,172)*0.15,gp*rd*0.9)
out=mix(out,inkcol,th*0.62*(1-wmf))
out=mix(out,ink*0.9+tex*0.1,edge*0.35)
out=mix(out,C(228,226,214),sc_w*0.3)
# ---- світлі плями на місці церков і інших храмів
cp=np.zeros((H,W),np.float32)
churches=[]
for f in GJ:
    p=f['properties']
    if p.get('building') in('church','cathedral','chapel','synagogue') or p.get('amenity')=='place_of_worship' or p.get('religion'):
        if p.get('religion')=='pagan': continue
        g_=f['geometry']; c_=g_['coordinates'][0] if g_['type']=='Polygon' else g_['coordinates']
        try: pts=np.array([P(*q) for q in c_]); churches.append(pts.mean(axis=0))
        except Exception: pass
# об'єднуємо дуже близькі
merged=[]
for c in churches:
    for m in merged:
        if np.hypot(*(m[0]-c))<45: m[0]=(m[0]*m[1]+c)/(m[1]+1); m[1]+=1; break
    else: merged.append([c,1])
print('плям',len(merged))
dots=np.zeros((H,W),np.float32); glow=np.zeros((H,W),np.float32)
rr=np.random.default_rng(55)
for (c,k) in merged:
    r=12+3*min(k,3)+rr.uniform(-1.5,1.5)
    th=np.linspace(0,6.283,24,endpoint=False)
    rad=r*(1+0.10*np.sin(th*3+rr.uniform(0,6))+0.04*rr.normal(size=24))
    pts=np.array([(c[0]+rad[i]*math.cos(th[i]),c[1]+rad[i]*math.sin(th[i])) for i in range(24)])
    cv2.fillPoly(dots,[np.int32(np.round(pts*4))],1.0,cv2.LINE_AA,shift=2)
    cv2.circle(glow,(int(c[0]*4),int(c[1]*4)),int(r*1.9*4),1.0,-1,cv2.LINE_AA,shift=2)
glow=cv2.GaussianBlur(glow,(0,0),9)
dots=cv2.GaussianBlur(dots,(0,0),1.6)
out=out+(C(238,234,214)-out)*np.clip(glow*0.22,0,0.22)[...,None]
out=out+(C(236,228,200)-out)*np.clip(dots*0.8,0,0.8)[...,None]

out+=(R.random((H,W)).astype(np.float32)[...,None]-0.5)*7
vig=np.clip(((xx/W-0.5)**2+(yy/H-0.5)**2)*1.6,0,1)
out=out*(1-0.22*vig[...,None])
out=np.clip(out,0,255).astype(np.uint8)
Image.fromarray(out).save('map.jpg',quality=82,optimize=True)
Image.fromarray(out).resize((640,847),Image.LANCZOS).save('preview.png')
import os; print(os.path.getsize('map.jpg'))

# орієнтири
names={'Золоті ворота':None,'Софійський собор':None,'Андріївська церква':None,'Михайлівський Золотоверхий монастир':None,'Контрактова площа':None,'Поштова площа':None,'Майдан Незалежності':None,'Європейська площа':None,'Львівська площа':None,'Хрещатик':None}
for f in GJ:
    n=f['properties'].get('name')
    if n in names and names[n] is None and f['geometry']['type'] in('Polygon','LineString'):
        c=centroid(f); names[n]=(round(c[0]/W*100,1),round(c[1]/H*100,1))
print(names)
for nm,(lo,la) in {'ZV':(30.5138,50.4488),'KON':(30.5157,50.4657)}.items(): print(nm,[round(v,1) for v in (P(lo,la)[0]/W*100,P(lo,la)[1]/H*100)])

