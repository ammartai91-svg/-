import sys, json, numpy as np, cv2
S=sys.argv[1]
out={}
for n in ['wide','close','street']:
    im=cv2.imread(f'{S}/{n}.jpg')
    im=im[:,746:1831]  # 1085 wide x 1932
    h,w=im.shape[:2]
    b,g,r=[im[:,:,i].astype(int) for i in range(3)]
    mask=((r>150)&(r-g>70)&(r-b>50)).astype(np.uint8)*255
    if n=='close': mask[1580:1760,:]=0  # player UI area handled separately
    ys,xs=np.where(mask>0)
    # path points for outline (in 1080x1920 output coords)
    sx=1080/w; sy=1920/h
    pts=np.stack([xs*sx,ys*sy],1)
    out[n]={'n':int(len(xs)),'bbox':[float(xs.min()*sx),float(ys.min()*sy),float(xs.max()*sx),float(ys.max()*sy)]}
    # contour ordered
    cnts,_=cv2.findContours(cv2.dilate(mask,np.ones((5,5))),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cnts,key=cv2.contourArea)[:,0,:]
    c=c[::max(1,len(c)//160)]
    out[n]['contour']=[[round(float(x*sx),1),round(float(y*sy),1)] for x,y in c]
    m2=cv2.dilate(mask,np.ones((9,9),np.uint8),iterations=2)
    clean=cv2.inpaint(im,m2,7,cv2.INPAINT_TELEA)
    if n=='close':
        # remove video player UI: fill region from texture above via inpaint
        ui=np.zeros((h,w),np.uint8); ui[1560:1790,40:1045]=255
        clean=cv2.inpaint(clean,ui,9,cv2.INPAINT_TELEA)
    up=cv2.resize(clean,(1080,1920),interpolation=cv2.INTER_LANCZOS4)
    bl=cv2.GaussianBlur(up,(0,0),1.2); up=cv2.addWeighted(up,1.5,bl,-0.5,0)
    cv2.imwrite(f'{S}/plates/{n}.jpg',up,[cv2.IMWRITE_JPEG_QUALITY,95])
json.dump(out,open(f'{S}/paths.json','w'))
for k,v in out.items(): print(k,v['n'],v['bbox'],len(v['contour']))
