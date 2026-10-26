import subprocess,numpy as np,sys
t=sys.argv[1]; v=f"input/10plus_{t}.mp4"
raw=subprocess.run(["ffmpeg","-v","error","-i",v,"-vf","fps=5,scale=120:262,format=gray","-f","rawvideo","-"],capture_output=True).stdout
np.save(f"/tmp/g/{t}.npy",np.frombuffer(raw,np.uint8).reshape(-1,262,120))
a=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",v,"-vn","-ac","1","-ar","8000","-f","s16le","-"],capture_output=True).stdout,np.int16).astype(float)
np.save(f"/tmp/g/{t}_rms.npy",np.array([np.sqrt((a[i*400:(i+1)*400]**2).mean()+1) for i in range(len(a)//400)]))
