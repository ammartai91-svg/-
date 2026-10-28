import numpy as np, wave, sys, os
SR=48000; D=40.0; N=int(SR*D); out=sys.argv[1]
rng=np.random.default_rng(3); tt=np.arange(N)/SR
def put(buf,sig,t,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig)); buf[i:j]+=sig[:j-i]*g
def lp(x,k):
    y=np.empty_like(x); s=0.0
    for i in range(len(x)): s+=k*(x[i]-s); y[i]=s
    return y
def fftconv(x,ir):
    n=len(x)+len(ir); n2=1<<(n-1).bit_length()
    return np.fft.irfft(np.fft.rfft(x,n2)*np.fft.rfft(ir,n2),n2)[:len(x)]
ir_n=int(2.6*SR); ir=rng.standard_normal(ir_n)*np.exp(-np.arange(ir_n)/SR*2.2); ir=lp(ir,.25); ir/=np.abs(ir).sum()/30
def hz(m): return 440*2**((m-69)/12)
# ---------- MUSIC ----------
music=np.zeros(N)
def piano(f,dur=3.0,vel=1.0):
    n=int(dur*SR); t=np.arange(n)/SR
    s=sum(a*np.sin(2*np.pi*f*h*t*(1+0.0004*h))*np.exp(-t*(1.6+h*.9)) for h,a in [(1,1),(2,.45),(3,.22),(4,.1),(5,.05)])
    s*=np.minimum(1,t/0.004); return s*vel*.32
def pad(freqs,dur):
    n=int(dur*SR); t=np.arange(n)/SR
    s=sum(np.sin(2*np.pi*f*t)+.5*np.sin(2*np.pi*f*1.003*t)+.3*np.sin(2*np.pi*f*2*t) for f in freqs)
    e=np.minimum(1,t/1.2)*np.minimum(1,(dur-t)/1.2)
    return s*e*.045
beat=0.8
chords=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]  # Am F C G
for k in range(13):
    t0=k*3.2; ch=chords[k%4]
    put(music,pad([hz(m-12) for m in ch]+[hz(ch[0]-24)],3.6),t0,1.0 if t0>=4.8 else .55)
    if 7.0<=t0<38:   # arpeggio
        pat=[0,1,2,1,0+12,2,1,2]
        for i,p in enumerate(pat):
            m=ch[p%3]+(12 if p>=12 else 0)+12
            put(music,piano(hz(m),2.4,.8 if i%4==0 else .55),t0+i*0.4)
    if t0<7.0 and k%2==0: put(music,piano(hz(ch[2]+24),3,.5),t0+.4)
# soft pulse in map section
def kick():
    n=int(.3*SR); t=np.arange(n)/SR; f=np.geomspace(110,45,n)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*10)
x=20.0
while x<33.8: put(music,kick(),x,.35); x+=beat
put(music,piano(hz(45),6,1.2),34.0); put(music,piano(hz(57),6,.9),34.0); put(music,piano(hz(64),6,.8),34.02); put(music,piano(hz(72),6,.7),34.04)

# ---- music-only version: strings swell + sub + soft pulse so the track carries the story ----
def strings(freqs,dur):
    n=int(dur*SR); t=np.arange(n)/SR; s=np.zeros(n)
    for f in freqs:
        for det in (-0.004,0,0.005):
            ph=(f*(1+det)*t)%1.0; s+=(2*ph-1)
    s=lp(s,.06); e=np.minimum(1,t/1.0)*np.minimum(1,(dur-t)/0.8)
    return s*e*.02
for k in range(13):
    t0=k*3.2; ch=chords[k%4]
    if 6.4<=t0<38:
        put(music,strings([hz(m) for m in ch],3.5),t0,1.0 if t0<20 or t0>=32 else .7)
    sub=piano(hz(ch[0]-24),3.0,1.0); put(music,sub,t0,.6 if t0>=7 else .3)
def softkick():
    n=int(.28*SR); t=np.arange(n)/SR; f=np.geomspace(90,42,n)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*12)
x=12.0
while x<20: put(music,softkick(),x,.25); x+=beat*2
wet=fftconv(music,ir); music=music*.75+wet*.5
# ---------- SFX ----------
sfx=np.zeros(N)
def heartbeat():
    n=int(.5*SR); t=np.arange(n)/SR
    def th(t0,f0,g):
        tt_=np.clip(t-t0,0,None); f=np.geomspace(f0,f0*.45,n)
        return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt_*28)*(t>=t0)*g
    return th(0,75,1)+th(.17,65,.7)
for b in [0.35,1.15,1.95,2.75,3.55,4.35]: put(sfx,heartbeat(),b,.9)
for b in [34.2,35.0,35.8]: put(sfx,heartbeat(),b,.45)
def whoosh(dur=.7):
    n=int(dur*SR); x=rng.standard_normal(n); k=np.concatenate([np.linspace(.02,.35,n//2),np.linspace(.35,.02,n-n//2)])
    y=np.empty(n); s=0.0
    for i in range(n): s+=k[i]*(x[i]-s); y[i]=s
    return y*np.sin(np.linspace(0,np.pi,n))**2
def boom(dur=1.2):
    n=int(dur*SR); t=np.arange(n)/SR; f=np.linspace(80,32,n)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3.5)
def pop(f0=900,f1=300,dur=.12):
    n=int(dur*SR); t=np.arange(n)/SR; f=np.geomspace(f0,f1,n)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*30)
def ping(f=1760,dur=1.0):
    n=int(dur*SR); t=np.arange(n)/SR
    return (np.sin(2*np.pi*f*t)+.4*np.sin(2*np.pi*f*2.01*t))*np.exp(-t*5)*.5
def tick():
    n=int(.02*SR); return rng.standard_normal(n)*np.exp(-np.arange(n)/SR*300)*.3
def beep(f=2200,dur=.07):
    n=int(dur*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*f*t)*.3*np.minimum(1,(dur-t)/0.02)
def riser(dur=1.6):
    n=int(dur*SR); x=rng.standard_normal(n); k=np.linspace(.01,.3,n); y=np.empty(n); s=0.0
    for i in range(n): s+=k[i]*(x[i]-s); y[i]=s
    return y*np.linspace(0,1,n)**2
def shimmer():
    s=np.zeros(int(2.8*SR))
    for i,m in enumerate([81,84,88,93]): p=ping(hz(m),2.4); s[int(i*.06*SR):int(i*.06*SR)+len(p)]+=p*.6
    return s
put(sfx,riser(1.6),5.4,.5); put(sfx,boom(1.4),6.95,.7); put(sfx,shimmer(),7.0,.5)
put(sfx,shimmer(),8.0,.35)
put(sfx,whoosh(.6),11.8,.4); put(sfx,pop(700,300),12.2,.3)
for a in (14.6,15.6,16.6): put(sfx,pop(1000,500),a,.35)
put(sfx,whoosh(.8),19.4,.7)
for x in (23.25,26.25,29.05): put(sfx,whoosh(.7),x,.6)
for a in (20.2,23.8,26.8,29.6):
    for k in range(5): put(sfx,tick(),a+.1+k*.18,.5)
for a in (21.4,24.6,27.8): put(sfx,ping(1568,.8),a,.35)
for a in (20.8,22.0,24.2,27.2): put(sfx,pop(900,350),a,.4)
for k,x in enumerate((29.7,29.95,30.2)): put(sfx,beep(2000+k*300),x,.6)
put(sfx,boom(.6),31.65,.55); put(sfx,ping(2093,1.2),31.7,.55); put(sfx,pop(800,300),31.8,.45)
put(sfx,whoosh(.8),33.6,.5); put(sfx,shimmer(),34.6,.4)
sfx+=fftconv(sfx,ir)*.15
def norm(x,peak): return x/np.max(np.abs(x))*peak
music=norm(music,.72); sfx=norm(sfx,.5)
fadeout=np.clip((D-tt)/1.2,0,1); fadein=np.clip(tt/0.05,0,1)
music*=fadeout*fadein; sfx*=fadeout
mix=np.tanh((music+sfx)*1.1)/np.tanh(1.1)*.9
def wr(name,x):
    st=np.stack([x,x],1)
    with wave.open(os.path.join(out,name),'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st,-1,1)*32767).astype('<i2').tobytes())
wr('ad_music.wav',music); wr('ad_sfx.wav',sfx); wr('ad_mix.wav',mix)
