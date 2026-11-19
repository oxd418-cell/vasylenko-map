import numpy as np, cv2, math
from PIL import Image
W,H=2100,2850; S=1.5
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

# ================= ДНІПРО =================
cl_r=[(1335,-80),(1300,250),(1318,560),(1268,860),(1288,1200),(1246,1550),(1276,2000)]
cc=cr(cl_r,4)
rad=np.interp(np.arange(len(cc)),[0,len(cc)-1],[150,112])
wm=np.zeros((H,W),np.uint8)
for i,p in enumerate(cc):
    cv2.circle(wm,(int(p[0]*S),int(p[1]*S)),int((rad[i]+8*math.sin(i*0.02))*S),255,-1)
dx=(noise(130,21)-0.5)*16*S; dy=(noise(130,22)-0.5)*16*S
wm=cv2.remap(wm,xx+dx,yy+dy,cv2.INTER_LINEAR)
# Труханів острів
isl_pts=[(1335,30),(1380,110),(1410,240),(1418,380),(1398,500),(1362,600),(1330,620),(1316,520),(1300,400),(1306,260),(1318,140)]
im=np.zeros((H,W),np.uint8); cv2.fillPoly(im,[np.int32(cr(isl_pts+[isl_pts[0]],6)*S)],255)
im=cv2.remap(im,xx+dx*0.6,yy+dy*0.6,cv2.INTER_LINEAR)
wm=cv2.subtract(wm,im)
wmf=cv2.GaussianBlur(wm,(0,0),1.4).astype(np.float32)/255
imf=cv2.GaussianBlur(im,(0,0),1.4).astype(np.float32)/255
# вода
dist=cv2.distanceTransform((wm>127).astype(np.uint8),cv2.DIST_L2,5)/S
deep=np.clip(dist/90,0,1)
water=mix(np.broadcast_to(C(92,170,178),(H,W,3)).copy(),C(46,124,142),deep)
water+=(fbm(60,200,5)[...,None]-0.5)*C(20,28,28)
fl=np.zeros((H,W),np.uint8); fl2=np.zeros((H,W),np.uint8)
for k in range(520):
    t0=int(R.uniform(0,len(cc)-60)); off=R.uniform(-1,1)
    seg=[]; L=int(R.uniform(16,60))
    for j in range(L):
        i=min(len(cc)-2,t0+j); d=cc[i+1]-cc[i]; n=np.array([-d[1],d[0]])/(np.linalg.norm(d)+1e-6)
        seg.append((cc[i]+n*(off*rad[i]*0.9+3*math.sin(j*0.35+k)))*S)
    tgt=fl if k%3 else fl2
    cv2.polylines(tgt,[np.int32(np.array(seg)*4)],False,255,int(R.choice([2,3,4,6])),cv2.LINE_AA,shift=2)
fl=cv2.GaussianBlur(fl,(0,0),1.2).astype(np.float32)/255; fl2=cv2.GaussianBlur(fl2,(0,0),1.0).astype(np.float32)/255
water=mix(water,C(150,208,206),fl*0.35); water=mix(water,C(36,108,126),fl2*0.35)
glint=np.clip((fbm(66,40,3)-0.72)*6,0,1)*fl; water=mix(water,C(230,242,236),glint*0.6)
# пісок/берег
band=lambda m,px: cv2.GaussianBlur(cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(px,px))),(0,0),2.5).astype(np.float32)/255
sand=np.clip(band(wm,int(26*S))-wmf,0,1)*(0.55+0.45*noise(10,23))
tex=mix(tex,C(206,170,104),sand*0.8)
isl_sand=np.clip(imf-cv2.GaussianBlur(cv2.erode(im,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(int(22*S),)*2)),(0,0),3).astype(np.float32)/255,0,1)
tex=mix(tex,water,wmf)
edge=np.clip(band(wm,5)-cv2.GaussianBlur(cv2.erode(wm,np.ones((3,3),np.uint8)),(0,0),1).astype(np.float32)/255,0,1)

# ================= СХИЛ (рельєф) =================
slope=[(120,760),(330,820),(520,800),(700,880),(860,960),(980,1060),(1060,1200),(1110,1420)]
sm=np.zeros((H,W),np.uint8); stroke(sm,cr(slope,6)*S,70)
sm=cv2.GaussianBlur(sm,(0,0),40).astype(np.float32)/255
tex=mix(tex,C(80,82,70),sm*0.28)
hm=np.zeros((H,W),np.uint8); sc_=cr(slope,6)
for i in range(0,len(sc_)-3,3):
    p=sc_[i]; d=sc_[i+2]-sc_[i]; n=np.array([-d[1],d[0]])/(np.linalg.norm(d)+1e-6)
    for k in range(2):
        o=R.uniform(-45,30); q=p+n*o
        l=R.uniform(10,22); a=q-n*0+np.array([d[0],d[1]])/(np.linalg.norm(d)+1e-6)*0
        e=q-n*l
        cv2.line(hm,(int(q[0]*S*4),int(q[1]*S*4)),(int(e[0]*S*4),int(e[1]*S*4)),200,2,cv2.LINE_AA,shift=2)
hm=cv2.GaussianBlur(hm,(0,0),0.8).astype(np.float32)/255*(1-wmf)
tex=mix(tex,C(70,72,62),hm*0.35)

# ================= ПАРКИ =================
def blob(cx,cy,rx,ry,rot,seed,jit=0.16,n=40):
    r=np.random.default_rng(seed); th=np.linspace(0,6.283,n,endpoint=False)
    k=1+jit*np.sin(th*r.integers(2,5)+r.uniform(0,6))+0.05*r.normal(size=n)
    x=rx*k*np.cos(th); y=ry*k*np.sin(th); c,s=math.cos(rot),math.sin(rot)
    return [(cx+x[i]*c-y[i]*s,cy+x[i]*s+y[i]*c) for i in range(n)]
parks=[(880,1080,120,70,-0.6,2),(690,760,70,120,0.5,3),(470,830,110,40,-0.1,4),
       (1010,1360,70,95,0.3,6),(170,1180,55,40,0.4,5),(560,1760,60,38,-0.3,7),(980,1700,70,55,0.2,9),(420,560,50,70,0.4,8)]
pmask=np.zeros((H,W),np.uint8)
for (cx,cy,rx,ry,rot,sd) in parks:
    cv2.fillPoly(pmask,[np.int32(cr(blob(cx,cy,rx,ry,rot,sd)+[blob(cx,cy,rx,ry,rot,sd)[0]],6)*S)],255)
pmask=cv2.bitwise_or(pmask,cv2.erode(im,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(int(18*S),)*2)))
pmask=cv2.bitwise_and(pmask,cv2.bitwise_not(wm))
pm=cv2.GaussianBlur(pmask,(0,0),1.3).astype(np.float32)/255
g=mix(np.broadcast_to(C(92,122,92),(H,W,3)).copy(),C(128,148,108),fbm(70,120,4))
dab=np.zeros((H,W),np.uint8); dab2=np.zeros((H,W),np.uint8)
ys,xs=np.nonzero(pmask[::6,::6])
for k in R.choice(len(xs),min(len(xs),2600),replace=False):
    x,y=xs[k]*6+R.uniform(-3,3),ys[k]*6+R.uniform(-3,3)
    tgt=dab if R.random()<0.55 else dab2
    cv2.circle(tgt,(int(x*4),int(y*4)),int(R.uniform(4,10)*4),255,-1,cv2.LINE_AA,shift=2)
dab=cv2.GaussianBlur(dab,(0,0),1.5).astype(np.float32)/255; dab2=cv2.GaussianBlur(dab2,(0,0),1.2).astype(np.float32)/255
g=mix(g,C(70,102,78),dab*0.35); g=mix(g,C(150,166,122),dab2*0.25)
g=mix(g,C(184,128,64),rm*0.35)
tex=mix(tex,g,pm*0.82)
pedge=np.clip(cv2.GaussianBlur(pmask,(0,0),1.2).astype(np.float32)/255-cv2.GaussianBlur(cv2.erode(pmask,np.ones((5,5),np.uint8)),(0,0),1.2).astype(np.float32)/255,0,1)
tex=mix(tex,C(58,82,62),pedge*0.6)

# ================= ДОРОГИ =================
road=np.zeros((H,W),np.uint8)   # основні лінії
gap=np.zeros((H,W),np.uint8)    # світлий просвіт у проспектах
thin=np.zeros((H,W),np.uint8)   # тонкі контури будівель
sd=[0]
def L(pts,w,amp=1.2,avenue=False):
    sd[0]+=1; c=path(pts,amp,sd[0]); stroke(road,c,w)
    if avenue: stroke(gap,c,w*0.38)
ZV=(320,1500); SOF=(440,1250); MYK=(600,1120); DES=(560,960); AND=(592,880)
KON=(800,420); POSH=(1060,840); EUR=(820,1260); MAI=(700,1460); LV=(150,1050)
L([ZV,(380,1370),SOF,(500,1100),DES,AND],13)                       # Володимирська
L([AND,(612,850),(575,790),(628,745),(612,680),(680,640),(690,560),(752,500),KON],8,amp=2.2)  # Андріївський узвіз
L([SOF,(520,1180),MYK,(700,1150),EUR],11)                            # Трьохсвятительська
L([MYK,(700,1040),(820,965),(960,885),POSH],13)                      # Володимирський узвіз
L([EUR,MAI,(600,1650),(520,1960)],20,avenue=True)                    # Хрещатик
L([(-40,1330),(60,1360),(200,1425),ZV],11)                           # Ярославів Вал
L([ZV,(300,1700),(290,1960)],12)                                      # Володимирська пд
L([(355,1520),(520,1515),(660,1545)],9)                              # Прорізна
L([(300,1650),(450,1655),(620,1665)],10)                             # Хмельницького
L([(380,1370),(210,1300),(40,1245),(-40,1225)],9)                    # Рейтарська
L([(500,1100),(320,1080),LV,(-40,1020)],11)                          # В.Житомирська
L([LV,(205,860),(300,660),(450,500),(600,410),KON],10)               # Глибочицька → Поділ
L([POSH,(980,700),(880,560),KON],13,avenue=True)                     # Сагайдачного
L([KON,(770,220),(745,-40)],11)                                       # Межигірська
L([KON,(600,375),(400,325),(150,275),(-40,250)],10)                  # Костянтинівська
L([EUR,(950,1300),(1060,1420),(1120,1560),(1130,1960)],9)            # Петрівська алея
L([MAI,(780,1560),(880,1700),(960,1960)],10)                          # Інститутська
L([MYK,(640,1240),(700,1360),MAI],8)                                 # Михайлівська
# набережна вздовж берега
bk=[]
for i in range(0,len(cc),25):
    p=cc[min(i,len(cc)-1)]; j=min(i+5,len(cc)-1); d=cc[j]-cc[max(0,j-10)]; n=np.array([-d[1],d[0]])/(np.linalg.norm(d)+1e-6)
    if n[0]>0: n=-n
    bk.append(p+n*(rad[min(i,len(rad)-1)]+38))
bk=np.array(bk); stroke(road,wob(cr(bk,5),1.0,77)*S,14); stroke(gap,wob(cr(bk,5),1.0,77)*S,14*0.38)
# пішохідний міст на острів
L([(890,1080),(1060,1000),(1200,880),(1315,560)],6,amp=0.5)

# ================= КВАРТАЛИ =================
gr=np.random.default_rng(31)
def landpx(p):
    x,y=int(p[0]*S),int(p[1]*S)
    if not(0<=x<W and 0<=y<H): return True
    return wm[y,x]<10 and pmask[y,x]<10
def runs(seq_pts,seq_in,w):
    n=len(seq_pts); i=0
    while i<n:
        if not seq_in[i]: i+=1; continue
        j=i
        while j+1<n and seq_in[j+1]: j+=1
        run=[np.array(p) for p in seq_pts[i:j+1]]
        if i>0 and gr.random()<0.55:
            q=run[0]+(seq_pts[i-1]-run[0])*gr.uniform(0.3,0.75)
            if landpx(q): run.insert(0,q)
        if j<n-1 and gr.random()<0.55:
            q=run[-1]+(seq_pts[j+1]-run[-1])*gr.uniform(0.3,0.75)
            if landpx(q): run.append(q)
        if len(run)>=2: L(run,w,amp=0.8)
        i=j+1
def shrink(q,m):
    c=np.mean(q,axis=0); return [c+(p-c)*max(0.05,1-m/(np.linalg.norm(p-c)+1e-6)) for p in q]
NB=[0]
def bpoly(poly,w=2.4):
    NB[0]+=1; P_=np.array(list(poly)+[poly[0]]); stroke(thin,wob(P_,0.25,5000+NB[0])*S,w)
def bline(p,q,w=2.2): stroke(thin,np.array([p,q])*S,w)
def block(q,w,g):
    outer=shrink(q,w/2+6)
    e=[np.linalg.norm(outer[(k+1)%4]-outer[k]) for k in range(4)]
    if min(e)<18: return
    r=g.random()
    if r<0.10: return
    if r<0.70 and min(e)>36:
        dep=g.uniform(9,14); inner=shrink(outer,dep*1.35)
        bpoly(outer); bpoly(inner)
        for k in range(4):
            o0,o1=outer[k],outer[(k+1)%4]; i0,i1=inner[k],inner[(k+1)%4]
            for t in np.sort(g.uniform(0.15,0.85,int(g.integers(1,4)))):
                bline(o0+(o1-o0)*t,i0+(i1-i0)*t)
        if g.random()<0.3:   # флігель у дворі
            c=np.mean(inner,axis=0); d=(inner[1]-inner[0]); d/=np.linalg.norm(d)+1e-6; n=np.array([-d[1],d[0]])
            hl,hd=g.uniform(5,9),g.uniform(4,7)
            bpoly([c+d*a_*hl+n*b_*hd for a_,b_ in [(-1,-1),(1,-1),(1,1),(-1,1)]],2.0)
    else:
        c=np.mean(outer,axis=0)
        for k in range(4):
            if g.random()<0.35: continue
            o0,o1=outer[k],outer[(k+1)%4]; d=o1-o0; Ld=np.linalg.norm(d); d/=Ld+1e-6
            n=c-(o0+o1)/2; n/=np.linalg.norm(n)+1e-6
            t=g.uniform(0.08,0.45); ln=g.uniform(0.25,0.45)*Ld; dp=g.uniform(9,15)
            p0=o0+d*t*Ld
            bpoly([p0,p0+d*ln,p0+d*ln+n*dp,p0+n*dp])
def roughen(poly,seed,amp=35):
    g=np.random.default_rng(seed); out=[]
    for k in range(len(poly)):
        a_=np.array(poly[k],float); b_=np.array(poly[(k+1)%len(poly)],float)
        for t in np.linspace(0,1,4,endpoint=False):
            out.append(tuple(a_+(b_-a_)*t+g.normal(0,amp,2)))
    return out
def district(poly,org,ang,su,sv,warp,w,seed,drop=0.06):
    g=np.random.default_rng(seed); poly=roughen(poly,seed)
    ua=np.array([math.cos(ang),math.sin(ang)]); va=np.array([-ua[1],ua[0]]); org=np.array(org,float)
    ext=max(np.linalg.norm(np.array(p)-org) for p in poly)+80
    def axis(rng):
        h=[0.0]
        while h[-1]<ext: h.append(h[-1]+g.uniform(*rng))
        neg=[0.0]
        while neg[-1]>-ext: neg.append(neg[-1]-g.uniform(*rng))
        return np.array(sorted(set(neg+h)))
    us,vs=axis(su),axis(sv)
    ph=g.uniform(0,6.28,4)
    P=np.zeros((len(us),len(vs),2)); ins=np.zeros((len(us),len(vs)),bool)
    for i,u in enumerate(us):
        for j,v in enumerate(vs):
            p=org+ua*u+va*v
            p=p+warp*np.array([math.sin(p[1]*0.0045+ph[0])+0.6*math.sin(p[0]*0.009+ph[1]),
                               math.sin(p[0]*0.0045+ph[2])+0.6*math.sin(p[1]*0.01+ph[3])])+g.normal(0,2.5,2)
            P[i,j]=p; ins[i,j]=pinside(poly,p) and landpx(p)
    ki=[i for i in range(len(us)) if g.random()>drop]; kj=[j for j in range(len(vs)) if g.random()>drop]
    for i in ki: runs(P[i,:],ins[i,:],w)
    for j in kj: runs(P[:,j],ins[:,j],w)
    for a_ in range(len(ki)-1):
        for b_ in range(len(kj)-1):
            i0,i1,j0,j1=ki[a_],ki[a_+1],kj[b_],kj[b_+1]
            if ins[i0:i1+1,j0:j1+1].all():
                block([P[i0,j0],P[i1,j0],P[i1,j1],P[i0,j1]],w,g)
ang=math.atan2(420-840,800-1060)
pod=[(590,20),(1145,15),(1150,420),(1100,790),(1010,820),(900,700),(720,560),(560,470),(545,200)]
district(pod,KON,ang,(52,86),(70,110),16,7,31)
district([(-20,20),(540,20),(545,200),(555,460),(420,540),(300,690),(200,900),(-20,900)],(250,450),0.22,(55,100),(62,110),30,6.5,41)
district([(-20,970),(180,990),(470,1085),(525,1180),(600,1380),(640,1560),(560,1950),(-20,1950)],ZV,0.36,(50,92),(56,100),26,6.5,42)
district([(670,1300),(1000,1420),(1110,1520),(1120,1950),(600,1950),(650,1600)],MAI,-0.55,(58,100),(66,112),28,6.5,43)
district([(470,1060),(520,960),(610,1000),(700,1120),(660,1250),(560,1170)],MYK,0.9,(48,70),(52,76),10,6,44)
for pts in [[(300,660),(380,730),(470,790),(540,800)],[(205,860),(330,905),(450,960),(520,965)],[(560,470),(505,590),(430,690),(380,730)],
            [(120,950),(160,1000),(170,1050)],[(470,1080),(420,1010),(330,990)],[(700,1150),(760,1100),(830,1080)],[(640,1240),(690,1290),(760,1300)],
            [(620,1665),(700,1700),(760,1640)],[(990,880),(1010,1000),(1030,1150)]]:
    L(pts,6.5,amp=1.6)

# ================= ПЛОЩІ — зелена плитка з орнаментом =================
tile=np.zeros((H,W),np.uint8); orn=np.zeros((H,W),np.uint8)
def square(poly,center,rad_,spokes,seed):
    return
    cv2.fillPoly(tile,[np.int32(cr(poly+[poly[0]],4)*S)],255)
    c=np.array(center)
    for k in range(spokes):
        a=k*2*math.pi/spokes+0.2; e=c+np.array([math.cos(a),math.sin(a)])*rad_
        cv2.line(orn,tuple(np.int32(c*S*4)),tuple(np.int32(e*S*4)),255,2,cv2.LINE_AA,shift=2)
        m=c+np.array([math.cos(a),math.sin(a)])*rad_*0.6
        cv2.circle(orn,tuple(np.int32(m*S*4)),int(rad_*0.14*S*4),255,2,cv2.LINE_AA,shift=2)
    cv2.circle(orn,tuple(np.int32(c*S*4)),int(rad_*0.32*S*4),255,2,cv2.LINE_AA,shift=2)
    cv2.circle(orn,tuple(np.int32(c*S*4)),int(rad_*0.12*S*4),255,-1,cv2.LINE_AA,shift=2)
square([(282,1462),(360,1458),(372,1530),(300,1548),(270,1505)],(322,1502),34,8,1)          # Золоті Ворота
square([(745,385),(850,360),(870,450),(770,480)],(808,420),44,10,2)                        # Контрактова
square([(565,1090),(640,1080),(648,1150),(572,1158)],(606,1120),32,8,3)                    # Михайлівська
square([(405,1225),(470,1215),(482,1278),(415,1290)],(443,1252),28,6,4)                    # Софійська
square([(785,1235),(850,1225),(860,1290),(800,1300)],(824,1262),28,8,5)                    # Європейська
square([(660,1430),(745,1425),(750,1495),(668,1500)],(705,1462),36,12,6)                   # Майдан
tl=cv2.GaussianBlur(tile,(0,0),1.0).astype(np.float32)/255
tg=mix(np.broadcast_to(C(66,128,104),(H,W,3)).copy(),C(112,170,140),fbm(90,30,4))
crk=np.abs(noise(9,91)-0.5)<0.03; tg=mix(tg,C(40,90,72),crk.astype(np.float32)*0.5)
om=cv2.GaussianBlur(orn,(0,0),0.8).astype(np.float32)/255
tg=mix(tg,C(36,82,66),om*0.75)
tex=mix(tex,tg,tl)
tedge=np.clip(tl-cv2.GaussianBlur(cv2.erode(tile,np.ones((5,5),np.uint8)),(0,0),1).astype(np.float32)/255,0,1)

# ================= ЗБІРКА =================
rd=cv2.GaussianBlur(road,(0,0),0.7).astype(np.float32)/255
gp=cv2.GaussianBlur(gap,(0,0),0.7).astype(np.float32)/255
th=cv2.GaussianBlur(thin,(0,0),0.6).astype(np.float32)/255
rd=rd*(1-wmf*0.98)
roadd=cv2.GaussianBlur(cv2.dilate(road,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(int(5*S),)*2)),(0,0),1).astype(np.float32)/255
th=th*(1-roadd)
gp=gp*(1-wmf)
ink=C(50,50,46)
inkcol=tex*0.22+ink*0.78
out=mix(tex,inkcol,rd*0.92)
out=mix(out,tex*0.85+C(196,192,172)*0.15,gp*rd*0.9)
out=mix(out,inkcol,th*0.62*(1-wmf))
out=mix(out,ink*0.9+tex*0.1,np.maximum(tedge*0.85,edge*0.35))
br=np.zeros((H,W),np.uint8); cb=wob(cr([(890,1080),(1060,1000),(1200,880),(1318,600)],4),0.4,5)*S
stroke(br,cb,5); brf=cv2.GaussianBlur(br,(0,0),0.7).astype(np.float32)/255
out=mix(out,C(62,60,54),brf*0.85)
# подряпини поверх усього
out=mix(out,C(228,226,214),sc_w*0.3)
out+=(R.random((H,W)).astype(np.float32)[...,None]-0.5)*7
vig=np.clip(((xx/W-0.5)**2+(yy/H-0.5)**2)*1.6,0,1)
out=out*(1-0.22*vig[...,None])
out=np.clip(out,0,255).astype(np.uint8)
Image.fromarray(out).save('map.jpg',quality=82,optimize=True)



import os; print(os.path.getsize('map.jpg'))
