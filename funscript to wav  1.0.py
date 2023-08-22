import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from  tkinter import *
import json
import wave
import numpy as np
from scipy.interpolate import Rbf
from scipy.interpolate import interp1d
import math
import threading
from time import sleep
class CONVERT:
    offset=20
    
    def __init__(self,framerate,minfra,maxfra):
        self.framerate=framerate
        self.minfra=minfra
        self.maxfra=maxfra
  
    def processing(self,progressbar, bar):
        self.minfra=int(self.minfra)
        self.maxfra=int(self.maxfra)
        self.framerate=int(self.framerate)
        f=open(filename, 'r',encoding = 'utf-8' )
        fun=f.read()
        fun_data=json.loads(fun)
        at=[]
        pos=[]
        t=[]
        global d
        d=0
        m=int(math.sqrt(1024*1048576*500*1))
        fra=self.framerate/1000
        for i in fun_data['actions']:
            at.append(i['at'])
            pos.append(i['pos'])
        #总时长
        if  'metadata' in fun_data.keys():
            duration=max(fun_data['metadata']['duration']*1000,max(at))
        else:
            duration=max(at)
        #转为array
        at=np.asarray(at)
        pos=np.asarray(pos)
        t= np.arange(0,duration,1/fra)
        t= np.append(t,duration)
        #获取时间增量,获取位置增量
        at1=np.delete(at,0)
        at2=np.delete(at,len(at)-1)
        dif_at=np.insert(at1-at2,0,(at1-at2)[0])
        mid_at=((at1-at2)/2+at2)
        mid_at=np.append(mid_at,at[len(at)-1])
        mid_at=np.insert(mid_at,0,0)
        pos1=np.delete(pos,0)
        pos2=np.delete(pos,len(pos)-1)
        dif_pos=np.insert(pos1-pos2,0,(pos1-pos2)[0])
        dif_pos=np.abs(dif_pos)
        mid_pos=pos-50
        mid_pos=np.insert(mid_pos,0,0)
        speed=dif_pos/dif_at
        if max(at)!=max(t):
            at=np.append(at,t[len(t)-1])
            speed=np.append(speed,0)
        if max(mid_at)!=max(t):
            mid_at=np.append(mid_at,t[len(t)-1])
            mid_pos=np.append(mid_pos,0)
        #分割
        len_t=len(t)
        i=int(len_t/m)
        if i==0:
            if min(mid_at)!=min(t):
                    mid_at=np.insert(mid_at,0,0)
                    mid_pos=np.insert(mid_pos,0,0)
            if max(mid_at)!=max(t):
                    mid_at=np.append(mid_at,max(t))
                    mid_pos=np.append(mid_pos,0)
            interp_amplitude=interp1d(mid_at,mid_pos,kind="quadratic")
            time_amplitude=interp_amplitude(t)
            interp_fra=interp1d(at,speed,kind="zero")
            time_fra=interp_fra(t)
            progressbar['value'] =950
            bar.update()
        else:    
            t_s=np.array_split(t,i)
            time_amplitude=np.asarray([])
            time_fra=np.asarray([])
            p=0
            for j in t_s:
                mid_at_s=mid_at[mid_at>=j[0]]
                mid_at_s=mid_at_s[mid_at_s<=j[len(j)-1]]
                at_s=at[at>=j[0]]
                at_s=at_s[at_s<=j[len(j)-1]]


                if len(mid_at_s)!=0:
                    indx1=np.where(mid_at==max(mid_at_s))
                    indx1=indx1[0][0]
                    indx2=np.where(mid_at==min(mid_at_s))
                    indx2=int(indx2[0][0])
                    mid_pos_s=mid_pos[indx2:indx1+1] 
                    if min(mid_at_s)!=min(j):
                        mid_at_s=np.insert(mid_at_s,0,min(j))
                        mid_pos_s=np.insert(mid_pos_s,0,0)
                        
                    if max(mid_at_s)!=max(j):
                        mid_at_s=np.append(mid_at_s,max(j))
                        mid_pos_s=np.append(mid_pos_s,0)
                else:
                    mid_pos_s=np.asarray([])


                    mid_at_s=np.append(mid_at_s,min(j))
                    mid_pos_s=np.append(mid_pos_s,0)
                    mid_at_s=np.append(mid_at_s,max(j))
                    mid_pos_s=np.append(mid_pos_s,0)
                if len(at_s)!=0:
                    indx3=np.where(at==max(at_s))
                    indx3=indx3[0][0]
                    indx4=np.where(at==min(at_s))
                    indx4=int(indx4[0][0])
                    speed_s=speed[indx4:indx3+1] 
                    if min(at_s)!=min(j):
                        at_s=np.insert(at_s,0,min(j))
                        speed_s=np.insert(speed_s,0,0)
                    if max(at_s)!=max(j):
                        at_s=np.append(at_s,max(j))
                        speed_s=np.append(speed_s,0)
                else:
                    speed_s=np.asarray([])
                    at_s=np.append(at_s,min(j))
                    speed_s=np.append(speed_s,0)
                    at_s=np.append(at_s,max(j))
                    speed_s=np.append(speed_s,0)

                interp_fra=interp1d(at_s,speed_s,kind="zero")
                interp_amplitude=Rbf(mid_at_s,mid_pos_s)
                new_pos=interp_amplitude(j)
                time_amplitude=np.append(time_amplitude,new_pos)
                time_amplitude=np.clip(time_amplitude,-50,50)
                new_fra=interp_fra(j)
                time_fra=np.append(time_fra,new_fra)
                p+=1
                progressbar['value'] =(p/i)*1000*0.95
                bar.update()

        #根据速度转换频率
        time_fra=np.clip(time_fra,1.5*min(time_fra),0.8*max(time_fra))
        t_strength=np.abs(time_fra/(max(time_fra)-min(time_fra)))
        time_fra=np.abs(time_fra/(max(time_fra)-min(time_fra))-1)
        time_fra=((1-time_fra)*self.minfra+(time_fra)*self.maxfra)
        # 转换为双通道
        L_a=time_amplitude+self.offset
        L_a=np.clip(L_a,0,(50+self.offset))*50/(50+self.offset)
        R_a=time_amplitude-10
        R_a=np.clip(R_a,-(50+self.offset),0)*50/(50+self.offset)
        t=t/1000
        m=1
        n=len(R_a)
        out1=np.zeros((m,2*n),dtype=R_a.dtype)
        out2=np.zeros((m,2*n),dtype=L_a.dtype)
        out3=np.zeros((m,2*n),dtype=time_fra.dtype)
        out4=np.zeros((m,2*n),dtype=t.dtype)
        out5=np.zeros((m,2*n),dtype=t_strength.dtype)
        out1[:,::2] =R_a 
        out2[:,::2] =L_a 
        out3[:,::2] =time_fra
        out4[:,::2] =t
        out5[:,::2] =t_strength
        R_a=out1[0]
        L_a=out2[0]
        L_fra=out3[0]
        L_t=out4[0]
        L_strength=out5[0]
        R_fra=np.insert(L_fra,0,0)
        R_fra=np.delete(R_fra,len(R_fra)-1)
        R_a=np.insert(R_a,0,0)
        R_a=np.delete(R_a,len(R_a)-1)
        R_a=R_a/(max(R_a)-min(R_a))
        L_a=L_a/(max(L_a)-min(L_a))
        R_t=np.insert(L_t,0,0)
        R_t=np.delete(R_t,len(R_t)-1)
        R_strength=np.insert(L_strength,0,0)
        R_strength=np.delete(R_strength,len(R_strength)-1)
        wave_data=(R_strength*R_a*np.sin(R_t*2*math.pi*R_fra)+L_strength*L_a*np.sin(L_t*2*math.pi*L_fra))*32767
        d=1

        progressbar['value'] =1000*0.98
        bar.update()
        return wave_data

    def write_wavadata(self,wave_data,progressbar, bar):
        wavename=filename.split("/")
        wavename=wavename[len(wavename)-1]
        wavename=wavename.split(".")
        wavename=wavename[0]
        wavename=wavename+".wav"
        f = wave.open(wavename, "wb")
        # 配置声道数、量化位数和取样频率
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(self.framerate)
        # 将wav_data转换为二进制数据写入文件
        f.writeframes(wave_data.tobytes())
        f.close()
        progressbar['value']=1000
        bar.update()

def start(): 
    th1=threading.Thread(target=Pro_Bar)
    th1.start()



def start_conv(progressbar, bar):
    progressbar['value'] =0
    bar.update()
    if inp1.get()=="8000(default)" :
        framerate=8000
    else :
        framerate=inp1.get()
    if inp2.get()=="60(default)":
        minfra=60
    else :
        minfra=inp2.get()
    if inp3.get()=="560(default)":
        maxfra=560
    else :
        maxfra=inp3.get()
    c=CONVERT(framerate,minfra,maxfra)
    wave_data=c.processing(progressbar, bar)

    c.write_wavadata(wave_data,progressbar, bar)
    if d:
        out=filename.split(".")
        out="wav file path:"+out[0]+".wav"
        out=Label(root, text=out,font=('', 14))
        out.place(x=350,y=350)


def Value_Bar(progressbar, bar):
    th2=threading.Thread(target=start_conv,args=(progressbar, bar))
    th2.start()

def Pro_Bar():
    def complete():
        if progressbar['value']==1000:
                button1 = tk.Button(bar, text='Conversion completed, click to close',command=close, font=('', 12),relief=RAISED)
                button1.place(x=200, y=100)
        else :
            bar.after(10,complete)
    def close():
        bar.destroy()

    def rate():
        k=int(progressbar['value']/progressbar['maximum']*10000)
        k=str(k/100)
        label3 = tk.Label(bar, text=k+'%', font=('', 12))
        label3.place(x=400, y=60)
        bar.after(10,rate)
    bar = tk.Tk()
    bar.title('Please wait')

    screenWidth = bar.winfo_screenwidth()   # 屏幕宽度
    screenHeight = bar.winfo_screenheight()  # 屏幕高度
    w = 600
    h = 200
    x = (screenWidth - w) / 2
    y = (screenHeight - h) / 2


    bar.geometry("%dx%d+%d+%d" % (w, h, x, y))
    label = tk.Label(bar, text='Converting:', font=('', 12))
    label.place(x=10, y=60)

    progressbar = ttk.Progressbar(bar)
    progressbar.place(x=120, y=60)
    progressbar['maximum'] = 1000
    progressbar['length'] = 280







    Value_Bar(progressbar, bar)
    rate()
    complete()
    bar.mainloop()
   


def file():
    global f1,filename
    filename = filedialog.askopenfilename()
    f1=Label(root, text=filename,font=('', 14))
    f1.place(x=100,y=290)
    if  'd1' in globals():
        d1.destroy()


def directory():
    global d1
    filename = filedialog.askdirectory() 
    d1=Label(root, text=filename,font=('', 14))
    d1.place(x=400,y=290)
    if  'f1' in globals():
        f1.destroy()




if __name__ == '__main__':
    root = tk.Tk()
    
    global filename
    filename=""
    root.title("funscript to wav  1.0")
    screenWidth = root.winfo_screenwidth()   # 屏幕宽度
    screenHeight = root.winfo_screenheight()  # 屏幕高度
    w = 1000
    h = 600
    x = (screenWidth - w) / 2
    y = (screenHeight - h) / 2




    root.geometry("%dx%d+%d+%d" % (w, h, x, y))
    lb = Label(root,text='\n           audio sample rate(Hz):\n \n audio out put max framerate(Hz):\n \n audio out put min framerate(Hz):',\
            anchor='ne',\
            font=('',20),\
            width=35,\
            height=6,\
            bd=2,\
            
            )
    lb.place(x=0,y=5)
    
    inp1 = Entry(root,font=('',20))
    inp1.insert(0, "8000(default)")
    inp1.place(x=500,y=25, width=200,height=50,)
    inp2 = Entry(root,font=('',20))
    inp2.insert(0, "60(default)")
    inp2.place(x=500,y=75, width=200,height=50,)
    inp3= Entry(root,font=('',20))
    inp3.insert(0, "560(default)")
    inp3.place(x=500,y=125, width=200,height=50,)
    button1= tk.Button(root, text="select a file",font=('',20), command=file,width=20, height=2)
    button1.place(x=150,y=200)
    button2= tk.Button(root, text="select a directory\n(Temporarily unavailable)",font=('',18), command=directory,width=25, height=3)
    button2.place(x=600,y=200)
    button3=tk.Button(root, text="convert",font=('',20), command=start,width=20, height=2)
    button3.place(x=380,y=400)
  
    root.mainloop()
