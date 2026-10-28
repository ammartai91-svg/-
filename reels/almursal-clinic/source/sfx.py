import numpy as np, wave, sys
SR=48000; D=40.0; N=int(SR*D)
L=np.zeros(N); rng=np.random.default_rng(7)
def add(sig,t,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig)); L[i:j]+=sig[:j-i]*g
def env(n,a,r): 
    e=np.ones(n); na=int(a*SR); nr=int(r*SR)
    if na: e[:na]=np.linspace(0,1,na)
    if nr: e[-nr:]*=np.linspace(1,0,nr)**2
    return e
def lp(x,k):  # simple one-pole lowpass with varying coef array/scalar
    y=np.zeros_like(x); a=np.broadcast_to(k,x.shape); s=0
    for i in range(len(x)): s+=a[i]*(x[i]-s); y[i]=s
    return y
def whoosh(dur=.7,up=True):
    n=int(dur*SR); x=rng.standard_normal(n)
    k=np.linspace(.02,.35,n) if up else np.linspace(.35,.02,n)
    k=np.concatenate([np.linspace(.02,.4,n//2),np.linspace(.4,.02,n-n//2)])
    e=np.sin(np.linspace(0,np.pi,n))**2
    return lp(x,k)*e*.9
def boom(dur=1.2):
    n=int(dur*SR); t=np.arange(n)/SR; f=np.linspace(90,35,n)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3.5)
    s+=lp(rng.standard_normal(n),.05)*np.exp(-t*8)*.6
    return s
def pop(f0=900,f1=300,dur=.12):
    n=int(dur*SR); t=np.arange(n)/SR; f=np.geomspace(f0,f1,n)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*30)
def ping(f=1760,dur=.9):
    n=int(dur*SR); t=np.arange(n)/SR
    return (np.sin(2*np.pi*f*t)+.4*np.sin(2*np.pi*f*2.01*t))*np.exp(-t*5)*.5
def beep(f=2200,dur=.07):
    n=int(dur*SR); t=np.arange(n)/SR
    return np.sign(np.sin(2*np.pi*f*t))*.25*env(n,.003,.02)
def tick():
    n=int(.02*SR); return rng.standard_normal(n)*np.exp(-np.arange(n)/SR*300)*.35
def riser(dur=2.2):
    n=int(dur*SR); t=np.arange(n)/SR; f=np.geomspace(200,1400,n)
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*.15 + lp(rng.standard_normal(n),np.linspace(.01,.3,n))*.5
    return s*np.linspace(0,1,n)**2
# music bed: 100 bpm soft pulse
bpm=100; beat=60/bpm
def kick():
    n=int(.35*SR); t=np.arange(n)/SR; f=np.geomspace(120,45,n)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)
def hat():
    n=int(.06*SR); x=rng.standard_normal(n); x=x-lp(x,.5); return x*np.exp(-np.arange(n)/SR*60)*.25
bed=np.zeros(N)
t=0.0; bi=0
while t<D-1.0:
    if t>=3.2:
        i=int(t*SR); k=kick(); j=min(N,i+len(k)); bed[i:j]+=k[:j-i]*.55
    h=hat(); i=int((t+beat/2)*SR); j=min(N,i+len(h)); bed[i:j]+=h[:j-i]*(.6 if t>=3.2 else .3)
    t+=beat
# pad drone (A minor-ish)
tt=np.arange(N)/SR
pad=sum(np.sin(2*np.pi*f*tt+np.sin(tt*.3*k))*a for k,(f,a) in enumerate([(110,.12),(164.8,.08),(220,.06),(261.6,.05)]))
pad*=np.clip(tt/2,0,1)*np.clip((D-tt)/1.5,0,1)*(0.8+0.2*np.sin(2*np.pi*tt/beat/4))
bed+=pad
L+=bed*.5
# events
add(boom(),0.0,.9)
for tt_ in (.12,.30,.5): add(pop(1200,500),tt_,.5)
add(pop(700,250),1.3,.4)
add(whoosh(.5),2.8,.5)
add(riser(1.6),3.4,.4)
for k in range(6): add(tick(),3.4+k*.2,.55)
add(ping(1568),4.6,.5)
add(pop(800,300),4.6,.5); add(pop(900,400),5.0,.4)
add(pop(1300,600),5.6,.5); add(ping(1760),5.4,.35)
add(riser(1.2),6.0,.35)
for x in (7.15,11.15,15.65,21.65,31.65): add(whoosh(.75),x,.9)
for x in (7.5,11.5,16.0,22.0): add(boom(.8),x,.35)
for k in range(4): add(tick(),7.8+k*.2,.55)
add(ping(1568),8.6,.5)
add(boom(.5),8.75,.6); add(ping(2093),8.8,.6)
add(pop(800,300),8.8,.5); add(pop(900,400),9.6,.4)
add(riser(1.5),9.4,.4)
add(riser(1.5),11.7,.4)
for k in range(6): add(tick(),11.8+k*.18,.55)
add(ping(1568),12.9,.55)
add(pop(800,300),12.6,.5); add(pop(900,400),13.4,.4)
add(riser(.8),16.2,.3)
add(pop(1000,400),16.6,.45)
for k,x in enumerate((17.2,17.45,17.7)): add(beep(2000+k*300),x,.7)
add(ping(1568),18.2,.5)
add(boom(.5),19.05,.6); add(ping(2093),19.1,.6)
add(pop(800,300),19.0,.5); add(pop(900,350),19.5,.4)
for k,x in enumerate((22.5,22.75,23.0,23.3)): add(beep(2200+k*250),x,.7)
for k in range(8): add(tick(),23.4+k*.17,.5)
add(boom(.5),25.3,.65); add(ping(2093),25.35,.7)
add(pop(800,300),25.6,.5)
for x in (27.2,28.0,28.8): add(pop(1300,600),x,.55)
add(pop(800,300),29.4,.45)
add(boom(1.0),32.0,.5); add(boom(.5),33.1,.6); add(ping(1760),33.15,.6)
for x in (33.4,33.9,34.4): add(pop(1100,500),x,.4)
add(riser(.8),34.4,.3); add(pop(900,300),35.2,.55); add(ping(2349,1.4),35.25,.5)
add(boom(1.2),38.6,.35)
m=np.max(np.abs(L)); L=L/m*0.89
L=np.tanh(L*1.2)/np.tanh(1.2)
fade=np.clip((D-tt)/0.6,0,1); L*=fade
st=np.stack([L,L],1)
with wave.open(sys.argv[1],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes())
