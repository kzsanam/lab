import sys, os, logModule, time
from queue import Queue
from CameraClass import Camera
from pyueye import ueye
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
import numpy as np
from pyueye_example_utils import (MemoryInfo, uEyeException, Rect, get_bits_per_pixel,ImageBuffer, check)

##needs the following packages installed:
#! pyueye
#! PyQt5
#! pyqtgraph
#! numpy

#! You have to enter the correct FPS, ExposureTime, AOI and Pixelclock in lines 237-241 for this code to work


class IDSCam(QtCore.QObject):  ##The main class controlling the IDS Camera
	responseSignal = pyqtSignal([list])

	def __init__(self,queue,settings,camPipeline,GUIPipeline=None,camID=0):
		super().__init__()
		self.log = logModule.SetupLogger("IDSCam camID:"+str(camID)) #The log module logs the state of the camera during operation
		self.log.debug("__init__")
		self.queue=queue	#the queue is the main way for the camera exisitng in a thread to communicate with the main thread
		self.camPipeline=camPipeline	#the camPipeline is the queue in which the camera pushes images which can be collected by the main thread
		self.GUIPipeline=GUIPipeline	#the GUIPipelike is a second queue similar to the camPipeline
		self.oldsettings=settings		#the settings to be set during startup of the camera
		self.currentFrameRate=self.oldsettings[0]
		self.exposureTime=self.oldsettings[1]
		self.width=int(self.oldsettings[2][0])
		self.height=int(self.oldsettings[2][1])
		self.offsetAOIFromSide=int(self.oldsettings[2][2])
		self.offsetAOIFromTop=int(self.oldsettings[2][3])
		self.currentPixelclock=self.oldsettings[3]
		self.running=False	#is the camera running at the moment?
		self.frameNumber=0	#how many frames were accquired
		self.camID=camID	#each camera has a hardware ID which can be set. If it hasn't been set previously it is 1. camID=0 means that the first available camera is used
		self.serialNumber=None	#the serial number of the connected camera
		
	def Connect(self):
		try:
			self.cam = Camera(self.camID)	#connect to the camera with the hardware ID
			print(f"Number of cameras: {self.cam.GetNumberOfCameras()}")
			ret = self.cam.Init()	#the return value of the camera initialization
			self.log.debug([f"IDS {self.camID}, Connecting"])
			self.serialNumber=self.cam.GetSerialNumber()
			self.log.debug([f"IDS {self.camID}, SerialNumber {self.serialNumber} found"])

			#! use this part of the Code if you want to change the DeviceID in the EEPROM of the camera
			#print(f"DeviceID: {self.cam.GetDeviceID()}")
			#print(f"SetDeviceID: {self.cam.SetDeviceID(2)}")
			#print(f"DeviceID: {self.cam.GetDeviceID()}")

		except Exception as e: #if the camera has not been found (which can happen if the USB connection was not closed properly) retry to find the camera. Usually it works after three attempts.
			attempt=0
			while attempt<5:
				print(f"Failed to connect. Trying again to connect to IDSCam{camID}. Attempt: {attempt}")
				self.log.debug(["IDS"+str(self.camID),"Connecting Attempt "+str(attempt)])
				time.sleep(2)
				try:
					self.cam = Camera(self.camID)
					ret = self.cam.Init()
					self.serialNumber=self.cam.GetSerialNumber()
					break
				except:
					attempt+=1
		finally:
			if self.serialNumber is None: #if no SerialNumber has been found there is no camera connected
				self.camPipeline.put([None,None,None,None]) #let the main thread know that no camera was found

			else:
				self.running = False
				self.ChangeSettings(self.oldsettings) #set the wanted camera settings

				if ret == ueye.IS_SUCCESS:
					self.camPipeline.put(["Image",np.zeros(1),0,0]) #let the main thread know that a camera was found and images will follow

	def ChangeSettings(self,settings):
		##AOI settings
		width=int(settings[2][2])
		height=int(settings[2][3])
		offsetX=int(settings[2][0])
		offsetY=int(settings[2][1])

		if self.running == True: #if the camera is running it first has to be stopped to change the settings
			self.cam.StopVideo()

		#first set the AOI
		self.cam.SetAoi(offsetX,offsetY,width,height)
		res=self.cam.GetAoi(readable=1)
		self.width=res[2]
		self.height=res[3]
		self.log.debug([f"IDS {self.camID}, GetAoi: OffsetX {res[0]}, OffsetY {res[1]}, Width {res[2]}, Height {res[3]}"])

		#then the colormode and the pixelclock
		self.cam.SetColormode(ueye.IS_CM_MONO8) #! Colormode is important to set correctly
		self.cam.SetPixelclock(settings[3])
		self.log.debug([f"IDS {self.camID}, GetPixelClockRange: {self.cam.GetPixelclockRange()}"])
		self.log.debug([f"IDS {self.camID}, Pixelclock: {self.cam.GetPixelclock()}"])

		#Allocate enough memory for the images
		self.cam.Alloc()

		#et the exposure time
		self.cam.SetExposure(settings[1])
		self.exposureTime=self.cam.GetExposure()
		self.exposureRange=self.cam.GetExposureRange()
		self.log.debug([f"IDS {self.camID}, ExposureRange: ({self.cam.GetExposureRange()[0]:.2f},{self.cam.GetExposureRange()[1]:.2f},{self.cam.GetExposureRange()[2]:.2f})"])
		self.log.debug([f"IDS {self.camID}, GetExposure: {self.cam.GetExposure():.2f}"])

		#and the framerate
		self.cam.SetFramerate(settings[0])
		self.currentFrameRate=self.cam.GetFramerate()
		self.frameRateRange=self.cam.GetFramerateRange()
		self.log.debug([f"IDS {self.camID}, GetFrameRateRange: ({self.cam.GetFramerateRange()[0]:.2f},{self.cam.GetFramerateRange()[1]:.2f},{self.cam.GetFramerateRange()[2]:.2f})"])
		self.log.debug([f"IDS {self.camID}, GetFrameRate: {self.cam.GetFramerate():.2f}"])

		#set the Gain. The gain here has to be divided by 100. So settings gain 100 here is equal to a gain 1
		self.cam.SetGain(100)
		self.log.debug([f"IDS {self.camID}, Gain: {self.cam.GetGain()/100.}"])

	def StartVideo(self):
		self.timeout=0
		self.running = True
		self.img_buffer = ImageBuffer() #create a buffer for the images to come

		while not self.queue.empty(): #if there are stop commands in the queue clear them first
			self.queue.get(False)
		self.cam.CaptureVideo() #start the camera taking images
		self.GetImage() #the images have to be collected from the camera

	def GetImage(self):
		#get some needed information from the camera which is needed to decode the image
		self.color_mode = ueye.is_SetColorMode(self.cam.Handle(), ueye.IS_GET_COLOR_MODE)
		self.bits_per_pixel = get_bits_per_pixel(self.color_mode)
		start=time.time_ns()
		last=time.time()
		while self.running == True: #as long as the camera is taking images the loop collects them
			#first wait for a new image to be taken
			ret = ueye.is_WaitForNextImage(self.cam.Handle(),self.timeout,self.img_buffer.mem_ptr,self.img_buffer.mem_id)
			if ret == ueye.IS_SUCCESS:
				self.meminfo = MemoryInfo(self.cam.Handle(), self.img_buffer)

				#check if the camera settings are wrong leading to the code missing images
				missedImages=self.cam.GetMissedImagesCount()
				if missedImages>10:
					self.log.error([f"IDS {self.camID} has missed more than {missedImages} images."])

				#finally the image
				self.array = ueye.get_data(self.img_buffer.mem_ptr,
						self.meminfo.width,
						self.meminfo.height,
						self.meminfo.bits,
						self.meminfo.pitch,
						False)
				ueye.is_UnlockSeqBuf(self.cam.Handle(), self.img_buffer.mem_id, self.img_buffer.mem_ptr)

				#create a copy of the image array, convert it to uint16 and reshape it to the size of the AOI
				image=self.array.copy()
				#image=np.frombuffer(image,dtype='uint16')
				image=np.reshape(image,(self.width,self.height, int(ueye.INT(8) / 8)))

				#increase the number of frames taken
				self.frameNumber+=1

				#if there is still an old image in the camera pipeline get that image out first
				if self.camPipeline.empty()==False:
					self.camPipeline.get_nowait()
				#then out the new image in
				self.camPipeline.put(["Image",image,self.frameNumber,time.time()])
				if self.GUIPipeline is not None: #if there is a gui pipeline which uses more information about the image
					#Update GUI with 40Hz
					updateRate=40.
					if (time.time()-last)>(1./updateRate):
						stats=[]
						stats_Mean=np.mean(image)
						stats.append(stats_Mean)
						stats_Std=np.std(image)
						stats.append(stats_Std)
						stats_Max=np.max(image)
						stats.append(stats_Max)
						stats_Min=np.min(image)
						stats.append(stats_Min)
						stats.append((stats_Max-stats_Min)/(stats_Max+stats_Min))
						min=stats_Min-stats_Std*0.25
						stats.append(min)
						max=stats_Max+stats_Std*0.25
						stats.append(max)
						if self.camID==1:
							self.GUIPipeline.SetMessage(["Image",image,self.frameNumber,time.time_ns(),stats])
						elif self.camID==2:
							self.GUIPipeline.SetMessage(["Image2",image,self.frameNumber,time.time_ns(),stats])
						else:
							pass
						last=time.time()

				#last check if the camera was told to stop
				if self.queue.empty()==False:
					msg=self.queue.get()
					if msg=="Stop":
						self.Stop()
	def Stop(self): #stops the camera from taking further images
		self.running = False
		self.cam.StopVideo()

	def Commandhandler(self,command): #this function takes a list as a command argument and calls the respective function within the class
		try:
			function=getattr(self,str(command[0]))
			if len(command)==1:
				function()
			if len(command)>1:
				args=command[1:]
				function(*args)
		except Exception as e:
			print(f"IDSCam Class encountered {e} while executing command {command}")

	def closeEvent(self):
		if self.serialNumber is None:
			pass
		else:
			self.log.debug([f"IDS {self.camID}, Camera closing"])
			self.queue.put("Stop")
			self.Stop()
			self.cam.Exit()

class CamTestClass(QtWidgets.QMainWindow):

	camCommandSignal = pyqtSignal([list])
	def __init__(self,imgItem,camID=1):
		super().__init__()

		#app.aboutToQuit.connect(self.closeEvent)

		self.log = logModule.SetupLogger("CamTestClass")
		self.imgItem=imgItem

		self.cam_FPS=3
		self.cam_Exposure=19
		self.IDSCam_AOI=[0,0,1936,1216]
		self.IDSCam_Pixelclock=190
		self.IDSCamSavedSettings=[self.cam_FPS,self.cam_Exposure,self.IDSCam_AOI,self.IDSCam_Pixelclock]

		self.camThread=QtCore.QThread() #create a thread for the camera to live in
		self.camQueue=Queue()	#this queue is used to communicate with the camera and telling it to stop taking images
		self.camPipeline=Queue(1)	#this queue is the storage for the images sent form the camera
		self.camID=camID	#the hardware ID of the camera
		#create the camera class
		self.camObject=IDSCam(self.camQueue,self.IDSCamSavedSettings,self.camPipeline,None,self.camID)
		#now move the camera to a seperate thread and connect the needed signal (i.e. the commandhandler)
		self.camObject.moveToThread(self.camThread)
		self.camCommandSignal.connect(self.camObject.Commandhandler)
		self.camThread.start()

		#when all that is done tell the camera thread to connect to the camera
		self.camCommandSignal.emit(["Connect"])

		self.connected=False
		##wait till the camera has finished the connection attempts
		while self.camPipeline.empty()==False:
			time.sleep(0.01)
		firstResponse=self.camPipeline.get()[0]
		if firstResponse is not None:
			self.camCommandSignal.emit(["StartVideo"])
			self.connected=True
			QtCore.QTimer.singleShot(100, self.ImageUpdate)
		else:
			print("Camera not connected")
			sys.exit()

	def closeEvent(self):
		self.camObject.closeEvent()
		time.sleep(0.1)
		self.camThread.terminate()
		self.camThread.wait()

	def ImageUpdate(self):
		#get an image
		image=self.camPipeline.get()[1:4]
		#display every fifth image
		if image[1]%5==0:
			self.imgItem.setImage(image[0])

		QtCore.QTimer.singleShot(10, self.ImageUpdate)


if __name__=="__main__":
	import sys, os, logModule, time
	from CameraClassWrapper import CamTestClass
	from PyQt5.QtWidgets import QApplication, QDialog
	from PyQt5.QtCore import QCoreApplication
	import pyqtgraph as pg
	import sys
	app = QCoreApplication.instance()
	if app is None:
		app = QApplication(sys.argv)
		
	win = pg.GraphicsLayoutWidget()
	win.show()
	view = win.addViewBox()
	view.setAspectLocked(True)

	## Create image item
	img1 = pg.ImageItem(border='w')
	view.addItem(img1)
	cam1=CamTestClass(img1,camID=0)

	sys.exit(app.exec_())
