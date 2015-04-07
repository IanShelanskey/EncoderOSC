import OSC
import RPi.GPIO as GPIO
import time, threading

send_address = '192.168.0.11' ,10000
receive_address = '192.168.0.17' ,9000

panelNum = 1
pinA = 23
pinB = 24

panel = OSC.OSCClient()
s = OSC.OSCServer(receive_address)
panel.connect(send_address)
s.addDefaultHandlers()



GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


error = 0
counts = 0

Encoder_A,Encoder_B = GPIO.input(pinA),GPIO.input(pinB)
Encoder_B_old = GPIO.input(pinB)

def reset(addr,tags,stuff,source):
	global counts
	global error
	counts = 0
	error = 0

def encodercount(term):
	global counts       
	global Encoder_A
	global Encoder_B
	global Encoder_B_old
	global error

	Encoder_A,Encoder_B = GPIO.input(pinA),GPIO.input(pinB)
	
	if ((Encoder_A,Encoder_B_old) == (1,0)) or ((Encoder_A,Encoder_B_old) == (0,1)):
		# this will be clockwise rotation
   	 	counts += 1
    	#print 'Encoder count is %s\nAB is %s %s' % (counts, Encoder_A, Encoder_B)

	elif ((Encoder_A,Encoder_B_old) == (1,1)) or ((Encoder_A,Encoder_B_old) == (0,0)):
		# this will be counter-clockwise rotation
   	 	counts -= 1
    	#print 'Encoder count is %s\nAB is %s %s' % (counts, Encoder_A, Encoder_B)

	else:
		#this will be an error
   	 	error += 1
   	 	#print 'Error count is %s' %error

	Encoder_B_old = Encoder_B



# Initialize the interrupts - these trigger on the both the rising and falling 
GPIO.add_event_detect(pinA, GPIO.BOTH, callback = encodercount)   # Encoder A
GPIO.add_event_detect(pinB, GPIO.BOTH, callback = encodercount)   # Encoder B
s.addMsgHandler("/reset", reset)
st = threading.Thread(target = s.serve_forever)
st.start()

# This is the part of the code which runs normally in the background
try:
	while True:
		msg = OSC.OSCMessage()
		msg.setAddress("/panel/"+str(panelNum))
		msg.append(counts)
		panel.send(msg)
		time.sleep(.1)
except KeyboardInterrupt:
	s.close()
	st.join
