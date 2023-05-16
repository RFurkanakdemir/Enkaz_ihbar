#!/usr/bin/env python3

from bmi160 import gyro 
import time 
import json 


class BMI160:
    def __init__(self):
        self.sensor = gyro()
        self.p_list = []
        self.r_list = []
        self.y_list = []
        self.data_list = [self.p_list,self.r_list,self.y_list]
        self.back_data = [0,0,0,0,0,0]
        
        self.outs = [0,0,0]
        self.one=0
        self.frst=0
        self.frstinit=0
        self.ref=[0,0,0]
        while True:
            p,r,y = self.sensor.getData()
            
            self.data_list[0].append(r)
            self.data_list[1].append(p)
            self.data_list[2].append(y)
            
            if len(self.data_list[0])%50 ==0:
                for i in range(len(self.data_list)):
                    self.outs[i]= sum(self.data_list[i])/len(self.data_list[i])
                    self.data_list[i].clear()
            
            r= self.outs[0]
            p = self.outs[1]
            y = self.outs[2]
            print({'pitch' :round(p,3),
                   'roll' : round(r,3),
                   'yaw' : round(y,3)
                   
                   })
            
            if (self.frst <300):
                self.frst +=1
                self.ref[0] += round(p,3)
                self.ref[1] += round(r,3)
                self.ref[2] += round(y,3)
                if(self.frst == 300):
                    self.ref[0] = self.ref[0]/300
                    self.ref[1] = self.ref[1]/300
                    self.ref[2] = self.ref [2]/300
                    self.frstinit = 1
                    print("\ninit okey ref0: "+ str(self.ref[0])+"  ref1: "+str(self.ref[1]) +"  ref2: "+ str(self.ref[2]))
                    time.sleep(1)
                    break
                
                
    def get_gyro_data(self):
        p,r,y = self.sensor.getData()
        one = 0
        self.back_data[3] = round (p,3)
        self.back_data[4] = round (r, 3 )
        self.back_data[5] = round (y,3)
        
        if(((self.ref[0]> self.back_data[3]+9) or (self.ref[0]<self.back_data[3]-9) or (self.ref[1]<self.back_data[4]-9) or (self.ref[1]>self.back_data[4]+10)) and (self.frstinit==1)):
            print("bina yikildi")
            time.sleep(3)
            return 1
        else:
            return 0
