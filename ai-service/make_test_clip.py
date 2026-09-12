import cv2
import numpy as np
from pathlib import Path
out=Path('ai-service/samples');out.mkdir(parents=True,exist_ok=True)
writer=cv2.VideoWriter(str(out/'urban_test_clip.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),10,(640,360))
for i in range(20):
    frame=np.full((360,640,3),220,dtype=np.uint8)
    cv2.rectangle(frame,(0,240),(640,360),(75,75,75),-1)
    cv2.rectangle(frame,(190+i*2,155),(430+i*2,285),(30,50,190),-1)
    cv2.rectangle(frame,(215+i*2,170),(300+i*2,215),(150,190,220),-1)
    cv2.rectangle(frame,(315+i*2,170),(400+i*2,215),(150,190,220),-1)
    writer.write(frame)
writer.release()
print(out/'urban_test_clip.mp4')
