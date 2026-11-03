# Sound design for the 30s clinic ad — all synthesized (no licensed samples).
import numpy as np, wave, sys
sr=48000;D=30;N=sr*D;rng=np.random.default_rng(3)
def wr(name,a,norm=.9):
    a=a/(np.max(np.abs(a))+1e-9)*norm
    st=np.stack([a,np.roll(a,int(.009*sr))],1)
    w=wave.open(name,'wb');w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((st*32767).astype('<i2').tobytes());w.close()
def place(buf,t0,s,g=1):
    i=int(t0*sr)
    if i<0: s=s[-i:];i=0
    j=min(len(buf),i+len(s));buf[i:j]+=s[:j-i]*g
def lp(x,c):  # one-pole lowpass, c can be array
    y=np.zeros_like(x);a=0.0;c=np.broadcast_to(c,x.shape)
    for i in range(len(x)): a+=c[i]*(x[i]-a);y[i]=a
    return y
def whoosh(d=.9,bright=.25):
    n=int(d*sr);t=np.arange(n)/sr
    return lp(rng.standard_normal(n),0.02+bright*np.sin(np.pi*t/d))*np.sin(np.pi*np.clip(t/d,0,1))**2
def swish(d=.4):  # short airy swipe for underlines
    n=int(d*sr);t=np.arange(n)/sr;x=rng.standard_normal(n)
    hp=x-lp(x,0.08);env=np.sin(np.pi*t/d)**1.5*np.exp(-t*2)
    return hp*env*0.6
def tick(f=2600):  # soft text "type-on" click
    n=int(.09*sr);t=np.arange(n)/sr
    click=lp(rng.standard_normal(n),.5)*np.exp(-t*220)
    tone=np.sin(2*np.pi*f*t)*np.exp(-t*60)*.5
    return (click+tone)
def chime(f=1567.98,d=1.6):
    t=np.arange(int(d*sr))/sr
    return sum((1/k)*np.sin(2*np.pi*f*k*t)*np.exp(-t*(3+k*2)) for k in (1,2.76,5.4))*np.minimum(1,t/.002)
def shimmer(d=2.2,n=14):
    out=np.zeros(int(d*sr))
    for i in range(n): place(out,i*0.06,chime(2000+rng.random()*3000,1.2)*.35)
    return out*np.linspace(1,.3,len(out))
def riser(d=1.6):
    n=int(d*sr);t=np.arange(n)/sr;u=t/d
    noise=lp(rng.standard_normal(n),0.01+0.3*u**2)*u**2
    tone=np.sin(2*np.pi*(200*t+900*t*u/2))*u**3*.25
    return noise+tone
def impact(d=2.5):
    t=np.arange(int(d*sr))/sr
    return np.sin(2*np.pi*(55-15*t)*t)*np.exp(-t*2.2)+rng.standard_normal(len(t))*np.exp(-t*9)*.25
def pop():
    t=np.arange(int(.25*sr))/sr;return np.sin(2*np.pi*(600+900*np.exp(-t*30))*t)*np.exp(-t*22)
def heartbeat():
    t=np.arange(int(1.2*sr))/sr;return np.sin(2*np.pi*52*t)*np.exp(-t*16)

s=np.zeros(N)
# ---- intro ----
place(s,1.35,swish(.9),0.35)                 # ECG line morphs into DNA
place(s,2.55,shimmer(1.6,8),0.25)            # DNA collapses into glowing embryo (flash)
place(s,2.62,whoosh(.6,.35),0.30)
for t0 in (3.33,3.48,3.63): place(s,t0,tick(2400),0.22)   # "حلمچ تصيرين أم؟"
place(s,3.72,swish(),0.30)                   # gold underline
# ---- scene cuts ----
for t0 in (5.2,8.6,10.8,13.8): place(s,t0-0.45,whoosh(),0.5); place(s,t0-0.05,shimmer(.8,5),0.12)
# ---- doctor ----
place(s,5.25,swish(.6),0.35)                 # doctor slides in
place(s,5.5,shimmer(),0.25)                  # name card
for t0 in (7.2,7.32,7.44): place(s,t0,tick(2400),0.22)    # "وياچ خطوة بخطوة"
place(s,7.6,swish(),0.30)
# ---- science ----
for t0 in (8.70,9.22,9.73): place(s,t0,tick(2200),0.2)    # service text
for t0 in (8.84,9.36,9.87): place(s,t0,chime(1567.98),0.22)  # gold checks
place(s,9.40,shimmer(1,5),0.18)              # fertilization flash
# ---- family ----
place(s,10.9,swish(.9),0.25)                 # gold ring draws
for t0 in (11.2,11.34,11.48): place(s,t0,tick(2400),0.22) # "لأن حلمچ يستاهل"
place(s,11.4,shimmer(1.4,8),0.18)            # light sweep
place(s,11.7,swish(),0.30)
# ---- outro ----
place(s,12.95,riser(1.6),0.45)               # build into logo
place(s,14.55,impact(),0.75);place(s,14.6,shimmer(3),0.35)
place(s,15.95,swish(.5),0.3)                 # logo moves up, clinic name types in
for t0 in (15.99,16.06,16.13,16.22): place(s,t0,tick(2600),0.18)
place(s,16.38,swish(),0.28)
for i,t0 in enumerate((16.74,16.92,17.09)): place(s,t0,chime([1318.5,1568,1975.5][i]),0.2)
place(s,17.26,tick(2200),0.2)                # "للحجز والاستفسار"
place(s,17.38,pop(),0.35)                    # phone button
place(s,27.6,heartbeat(),0.9);place(s,27.88,heartbeat(),0.6)
wr(sys.argv[1] if len(sys.argv)>1 else 'sfx.wav',s)
print('sfx ok')
