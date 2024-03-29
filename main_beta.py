##Contador de personas
##from picamera.array import PiRGBArray
##from picamera import PiCamera
import numpy as np
import cv2 as cv
from peopleCount import Person
import time
import threading
import datetime
from bmi_mainn import BMI160
from httppost import GSM

sensor_bmi = BMI160()
gsm = GSM()

def ServerDataSender(stop_server_flag):
    server_timer=time.time()
    init=0
    
    
    while not stop_server_flag.is_set():
        
        if(init ==0):
        
            if(time.time()-server_timer>5):
                print("server data sender loop")
                gsm.send_post_amount(counter_person=getTotalAmount(),status=0)
                init=1
                server_timer=time.time()
                

        if( time.time() - server_timer > 20 and init == 1):
            print("server data sender loop")
            gsm.send_post_amount(counter_person=getTotalAmount(),status=0)
            server_timer = time.time()
            

    print("server thread stopped")
        




def gyro_control(stop_gyro_flag):
    while not stop_gyro_flag.is_set():
        
        if(sensor_bmi.get_gyro_data()):
                print("bina yıkıldı")
                #thread_server.stop()
                
                stop_server_thread()
                time.sleep(0.5)
                thread_server.join()
                
                gsm.send_post_amount(counter_person=getTotalAmount(),status=1)
                stop_gyro_thread()
                
                #gsm.send_post_earthquake()
                # burası için baştan bina yıkıldı postu yazılacak.
        else:
                time.sleep(1)
                print("bina sağlam") 
    
    print("gyro thread stopped")



    

          
def setTotalAmount(number):
    try:
        print("dosyaya değer girildi")
        f = open("TotalAmount.afet", "w")
        f.write(str(number))
        f.flush()
        f.close()
        getTotalAmount()
        return 1
    except:
        print( "Cannot open file")
        return 0
    
def getTotalAmount():
    try:
        f = open("TotalAmount.afet", "r")
        number=f.read()
        f.flush()
        f.close()
        print("dosya okundu :"+str(number)+"kişi var" )
        return int(number)
    except:
        print( "Cannot open file")
        return 0

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=160,
    capture_height=120,
    display_width=640,
    display_height=480,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d !"
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

def stop_server_thread():
    stop_server_flag.set()

def stop_gyro_thread():
    stop_gyro_flag.set()

    
def MainCode():
    #Entry and exit counters
    
    cnt_up   = 0
    cnt_down = 0
    first_person_amount=0
    setTotalAmount(str(first_person_amount))
    
    #cap = cv.VideoCapture(0)
    #cap = cv.VideoCapture(gstreamer_pipeline(flip_method=0), cv.CAP_GSTREAMER)
    cap = cv.VideoCapture('peopleCount/Test Files/video2.mp4')
    #camera = PiCamera()
    ##camera.resolution = (160,120)
    ##camera.framerate = 5
    ##rawCapture = PiRGBArray(camera, size=(160,120))
    ##time.sleep(0.1)
    
    ##cap.set(3,160) #Width
    ##cap.set(4,120) #Height
    
    for i in range(19):
        print( i, cap.get(i))
    
    h = 480
    w = 640
    frameArea = h*w
    areaTH = frameArea/250
    print( 'Area Threshold', areaTH)
    
    #Input/output lines
    line_up = int(2*(h/5))
    line_down   = int(3*(h/5))
    
    up_limit =   int(1*(h/5))
    down_limit = int(4*(h/5))
    
    print( "Red line y:",str(line_down))
    print( "Blue line y:", str(line_up))
    line_down_color = (255,0,0)
    line_up_color = (0,0,255)
    pt1 =  [0, line_down];
    pt2 =  [w, line_down];
    pts_L1 = np.array([pt1,pt2], np.int32)
    pts_L1 = pts_L1.reshape((-1,1,2))
    pt3 =  [0, line_up];
    pt4 =  [w, line_up];
    pts_L2 = np.array([pt3,pt4], np.int32)
    pts_L2 = pts_L2.reshape((-1,1,2))
    
    pt5 =  [0, up_limit];
    pt6 =  [w, up_limit];
    pts_L3 = np.array([pt5,pt6], np.int32)
    pts_L3 = pts_L3.reshape((-1,1,2))
    pt7 =  [0, down_limit];
    pt8 =  [w, down_limit];
    pts_L4 = np.array([pt7,pt8], np.int32)
    pts_L4 = pts_L4.reshape((-1,1,2))
    
    #background subtractor
    fgbg = cv.createBackgroundSubtractorMOG2(detectShadows = True)
    
    #Structuring elements for morphological filters
    kernelOp = np.ones((3,3),np.uint8)
    kernelOp2 = np.ones((5,5),np.uint8)
    kernelCl = np.ones((11,11),np.uint8)
    
    #Variables
    font = cv.FONT_HERSHEY_SIMPLEX
    persons = []
    max_p_age = 5
    pid = 1
    
    while(cap.isOpened()):

        # Read an image from the video source
        ret, frame = cap.read()
        for i in persons:
            i.age_one() #age every person one frame
        #########################
        #   PRE-PROCESSING   #
        #########################
        
        #Apply background subtraction
        fgmask = fgbg.apply(frame)
        fgmask2 = fgbg.apply(frame)
    
        #Binarization to remove shadows (gray color)
        try:
            ret,imBin= cv.threshold(fgmask,200,255,cv.THRESH_BINARY)
            ret,imBin2 = cv.threshold(fgmask2,200,255,cv.THRESH_BINARY)
            #Opening (erode->dilate) to remove noise.
            mask = cv.morphologyEx(imBin, cv.MORPH_OPEN, kernelOp)
            mask2 = cv.morphologyEx(imBin2, cv.MORPH_OPEN, kernelOp)
            #Closing (dilate -> erode) to join white regions.
            mask =  cv.morphologyEx(mask , cv.MORPH_CLOSE, kernelCl)
            mask2 = cv.morphologyEx(mask2, cv.MORPH_CLOSE, kernelCl)
        except:
            print('EOF')
            print( 'UP:',cnt_up)
            print ('DOWN:',cnt_down)
            break
        #################
        #   CONTOURS   #
        #################
        
        # RETR_EXTERNAL returns only extreme outer flags. All child contours are left behind.
        _,contours0, hierarchy = cv.findContours(mask2,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
        for cnt in contours0:
            area = cv.contourArea(cnt)
            if area > areaTH:
                #################
                #   TRACKING    #
                #################
                
                #It remains to add conditions for multi-persons, exits and screen entrances.
                
                M = cv.moments(cnt)
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                x,y,w,h = cv.boundingRect(cnt)
                new = True
                if cy in range(up_limit,down_limit):
                    for i in persons:
                        if abs(x-i.getX()) <= w and abs(y-i.getY()) <= h:
                            # the object is close to one that was detected before
                            new = False
                            i.updateCoords(cx,cy)   #updates coordinates on the object and resets age
                            if i.going_UP(line_down,line_up) == True:
                                cnt_up += 1;
                                print( "ID:",i.getId(),'crossed going up at',time.strftime("%c"))
                                setTotalAmount((getTotalAmount()+1))
                            
                            elif i.going_DOWN(line_down,line_up) == True:
                                cnt_down += 1;
                                print( "ID:",i.getId(),'crossed going down at',time.strftime("%c"))
                                setTotalAmount((getTotalAmount()-1))
                            break
                        if i.getState() == '1':
                            if i.getDir() == 'down' and i.getY() > down_limit:
                                i.setDone()
                            elif i.getDir() == 'up' and i.getY() < up_limit:
                                i.setDone()
                        if i.timedOut():
                            #remove i from persons list
                            index = persons.index(i)
                            persons.pop(index)
                            del i     #liberar la memoria de i
                    if new == True:
                        p = Person.MyPerson(pid,cx,cy, max_p_age)
                        persons.append(p)
                        pid += 1     
                #################
                #   DRAWINGS     #
                #################
                cv.circle(frame,(cx,cy), 5, (0,0,255), -1)
                img = cv.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)            
                #cv.drawContours(frame, cnt, -1, (0,255,0), 3)
                
        #END for cnt in contours0
                
        #########################
        #   DRAW TRAJECTORIES  #
        #########################
        for i in persons:
            cv.putText(frame, str(i.getId()),(i.getX(),i.getY()),font,0.3,i.getRGB(),1,cv.LINE_AA)
            
        #################
        #   IMAGES    #
        #################
        str_up = 'UP: '+ str(cnt_up)
        str_down = 'DOWN: '+ str(cnt_down)
        frame = cv.polylines(frame,[pts_L1],False,line_down_color,thickness=2)
        frame = cv.polylines(frame,[pts_L2],False,line_up_color,thickness=2)
        frame = cv.polylines(frame,[pts_L3],False,(255,255,255),thickness=1)
        frame = cv.polylines(frame,[pts_L4],False,(255,255,255),thickness=1)
        cv.putText(frame, str_up ,(10,40),font,0.5,(255,255,255),2,cv.LINE_AA)
        cv.putText(frame, str_up ,(10,40),font,0.5,(0,0,255),1,cv.LINE_AA)
        cv.putText(frame, str_down ,(10,90),font,0.5,(255,255,255),2,cv.LINE_AA)
        cv.putText(frame, str_down ,(10,90),font,0.5,(255,0,0),1,cv.LINE_AA)
        
        cv.imshow('Frame',frame)
        #cv.imshow('Mask',mask)    
        
    
    ##    rawCapture.truncate(0)
        k = cv.waitKey(30) & 0xff
        if k == 27:
            break
        if(sensor_bmi.get_gyro_data()):
            break
    #END while(cap.isOpened())
        
    #################
    #   CLEANING    #
    #################
    cap.release()
    cv.destroyAllWindows()
    #thread_gyro.kill()
    #thread_server.kill()


stop_server_flag= threading.Event()
stop_gyro_flag = threading.Event()
thread_server = threading.Thread(target=ServerDataSender,args=(stop_server_flag,))       #thread nesnesi
thread_gyro = threading.Thread(target=gyro_control,args=(stop_gyro_flag,))          #thread nesnesi

if __name__ == "__main__":

    
    thread_gyro.start()
    thread_server.start()
    
    
   
    MainCode()
 




   

