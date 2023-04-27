#!/usr/bin/python3
import Jetson.GPIO as GPIO
import time 
import cv2
import datetime
from bmi_mainn import BMI160
from httppost import GSM

sensor_bmi = BMI160()
gsm = GSM()

pir_pin = 11
pir2_pin = 12
kayitok = 0
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(pir_pin,GPIO.IN)
GPIO.setup(pir2_pin,GPIO.IN)

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=840,
    capture_height=480,
    display_width=960,
    display_height=540,
    framerate=10,
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






    
def record_camera():
    kayitok = 0
    pir1 = 0
    pir2 = 0
    pir1_sec = 0
    pir2_sec = 0
    timer2=0
    person_counter=0
      
    while True :
        #print("pır bekliyor")
        timevariable=time.time()

        # print(float(timevariable))
        if(time.time()-timer2 >3):
            if (GPIO.input(pir_pin)) :
                pir1 = 1
                print("pır 1 tetiklendi")
                time.sleep(0.5)

            if(GPIO.input(pir2_pin)):
                pir2=1
                print("pır 2 tetiklendi")
                time.sleep(0.5)

        if(sensor_bmi.get_gyro_data()):
            print("bina yıkıldı")
            gsm.send_post(counter_person=12,status=1)
        else:
            print("bina sağlam")

        if(pir1 or pir2):
            print("pırlar tetiklendi kamera aktif ")
            window_title = "CSI Camera"
            filename=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = "video_{}.mp4".format(filename)
            video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
            time.sleep(0.5)
            
            if(video_capture.isOpened()):
                print("video capture open")
                frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(video_capture.get(cv2.CAP_PROP_FPS))
                fourcc = cv2.VideoWriter_fourcc(*'X264')
                out = cv2.VideoWriter(output_filename, fourcc, fps, (frame_width, frame_height))
                #start_time = datetime.datetime.now()
                time.sleep(1)
                while (1):
                    if(sensor_bmi.get_gyro_data()):
                        print("bina yıkıldı")
                        gsm.send_post(counter_person=12,status=1)


                    else:
                        print("bina sağlam")
                        
                    print("sonsuz döngüde okuyor")
                    ret_val, frame = video_capture.read()
                
                    if ret_val:
                        out.write(frame)
                        #cv2.imshow(window_title, frame)
                        #keyCode = cv2.waitKey(1) & 0xFF
                        
                        if(time.time()-timevariable >6):
                            if (GPIO.input(pir_pin)) :
                                pir1_sec = 1
                                print("pir 1 ikinci tetiklenme")

                            if(GPIO.input(pir2_pin)):
                                pir2_sec=1
                                print("pir 2 ikinci tetiklenme")
                            
                            

                        if (time.time() - timevariable > 15 and  (pir1_sec== 1 or  pir2_sec== 1 )  ) : 
                            print("timera girdi işlem bitti")
                            print(time.time() - timevariable)
                            video_capture.release() 
                            out.release() 
                            #cv2.destroyAllWindows()  
                            pir1 = 0
                            pir2 =0
                            pir1_sec = 0
                            pir2_sec = 0   
                            time.sleep(2)
                            timer2=time.time()
                            

                            break 
                    
                    else:
                        print("ret val hatalı geldi")
                        video_capture.release() 
                        out.release()
                        
                        break
            else:
                out.release()
                video_capture.release()
                print("video capture not opened")
                 
                       
    
   
            
 



if __name__ == "__main__":
   record_camera()

