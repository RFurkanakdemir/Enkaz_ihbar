import serial
import time
import datetime

class GSM:
    def __init__(self):


        
        self.mac= "dc1211gu12"
    
   
    
    
    def send_post(self,counter_person,status):
        
        ser = serial.Serial('/dev/ttyTHS1', 9600, timeout=1)
        time.sleep(2)
        
        # GPRS bağlantısını ayarla
        ser.write(b'AT+SAPBR=3,1,"Contype","GPRS"\r\n')
        response = ser.read(1000)
        print("\n"+str(response)+"\n")
        
        ser.write(b'AT+SAPBR=3,1,"APN","internet"\r\n')
        response = ser.read(1000)
        print("\n"+str(response)+"\n")
        
        ser.write(b'AT+SAPBR=1,1\r\n')
        response = ser.read(1000)
        print("\n"+str(response)+"\n")
        time.sleep(5)
        
        ser.write(b'AT+SAPBR=2,1\r\n')
        response = ser.read(1000)
        print("\n"+str(response)+"\n")

		# HTTP isteği için hazırlık yap
  
        ser.write(b'AT+HTTPINIT\r\n')
        response = ser.read(1000)
        print("\n"+str(response)+"\n")
        ser.write(b'AT+HTTPSSL=1\r\n')
        response = ser.read(1000)
        print("\n"+str(response)+"\n")
        
        ser.write(b'AT+HTTPPARA="CID",1\r\n')
        response = ser.read(1000)
        print("\n"+str(response)+"\n")
        
        base_url='AT+HTTPPARA="URL","https://cihazdata.coware.com.tr/api/cihazdata/giriscikis1/?data='
        imei=self.mac
        print("\n"+imei+"\n")
        status = str(status)
        person_count = str(counter_person)
        date = datetime.datetime.now().strftime("%m/%d/%Y")
        
        message_url = base_url+imei+"_"+status+"_"+person_count+"_"+date+'"'
        byte_message_url=bytes(message_url,'utf-8')
        ser.write(byte_message_url)
        ser.write(b'\r\n')
        
        #ser.write(b'AT+HTTPPARA="URL","https://cihazdata.coware.com.tr/api/cihazdata/giriscikis1/?data=dc1211gu12_1_12_05/04/2024"\r\n')
        #ser.write(message_url)
        #response = ser.read(1000)
        #print("\n"+str(response)+"\n")
        
        #ser.write(b'AT+HTTPPARA="USERDATA","data:"adrer""\\r\\n')
		#response = ser.read(1000)
		#print("\n"+str(response)+"\n")


		#ser.write(b'AT+HTTPPARA="CONTENT","application/x-www-form-urlencoded"\r\n')
		#response = ser.read(1000)
		#print("\n"+str(response)+"\n")
		#tarih= time.ctime(time.time())




		#ser.write(b'AT+HTTPPARA="SSL",1\r\n')
		#response = ser.read(1000)
		#print("\n"+str(response)+"\n")

		#ser.write(b'AT+HTTPPARA="SSLlevel",1\r\n')
		#response = ser.read(1000)
		#print("\n"+str(response)+"\n")

		#data = b'param=test'
		#byte_data = data.encode()
		#bos_data=b""
		#length = len(data)
		#print("\n"+str(length)+"\n")
		#ser.write(b'AT+HTTPDATA=10,10000\n\n')
		#response = ser.read(5000)
		#print("\n"+str(response)+"\n")

		#ser.write(data)
		#response = ser.read(1000)
		#print("\n"+str(response)+"\n")
        
        time.sleep(0.5)
        ser.write(b'AT+HTTPACTION=0\r\n')
        time.sleep(1)
        response = ser.read(100000)
        print("\n"+str(response)+"\n")# HTTP cevabını oku
        time.sleep(1) # Cevabın hazır olması için bekleyin
        ser.write(b'AT+HTTPREAD\r\n')
        response = ser.read(100000)
        time.sleep(5)
        print("\n"+str(response)+"\n")
        ser.write(b'AT+HTTPTERM\r\n')
        response = ser.read(1000)
        print("\n"+str(response)+"\n")
        ser.close() 		

        return 1

	
