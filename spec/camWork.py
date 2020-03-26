#from CameraClass import Camera
from pyueye import ueye
import numpy as np
import cv2
import sys


# is_SetExternalTrigger (HIDS hf, INT nTriggerMode)
#IS_SET_TRIG_LO_HI
#IS_SET_TRIG_OFF
# is_SetTriggerDelay (HIDS hf, INT nDelay)

class camWork():
    def __init__(self, camNum = 0):
        lolo = ueye.UEYE_CAMERA_LIST()
        #lolo.dwCount = ueye.is_GetNumberOfCameras()
        ret = ueye.is_GetCameraList(lolo)
        print(lolo.dwCount)
        print(lolo.uci[0].SerNo)
        print(lolo.uci[-1].dwDeviceID)
        self.camNum = camNum
        self.hCam = ueye.HIDS(camNum)             #0: first available camera;  1-254: The camera with the specified camera ID
        self.sInfo = ueye.SENSORINFO()
        self.cInfo = ueye.CAMINFO()
        self.pcImageMemory = ueye.c_mem_p()
        self.MemID = ueye.int()
        self.rectAOI = ueye.IS_RECT()
        self.pitch = ueye.INT()
        #self.nBitsPerPixel = ueye.INT(24)    #24: bits per pixel for color mode; take 8 bits per pixel for monochrome
        #self.channels = 3                    #3: channels for color mode(RGB); take 1 channel for monochrome
        self.m_nColorMode = ueye.INT()		# Y8/RGB16/RGB24/REG32
        #self.bytes_per_pixel = int(self.nBitsPerPixel / 8)

        self.nRet = ueye.is_InitCamera(self.hCam, None)

        self.m_nColorMode = ueye.IS_CM_MONO8
        self.nBitsPerPixel = ueye.INT(8)
        self.bytes_per_pixel = int(self.nBitsPerPixel / 12)

        self.nRet = ueye.is_AOI(self.hCam, ueye.IS_AOI_IMAGE_GET_AOI, self.rectAOI, ueye.sizeof(self.rectAOI))

        self.width = self.rectAOI.s32Width
        self.height = self.rectAOI.s32Height

        self.nRet = ueye.is_AllocImageMem(self.hCam, self.width, self.height, self.nBitsPerPixel, self.pcImageMemory, self.MemID)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_AllocImageMem ERROR")
        else:
            # Makes the specified image memory the active memory
            self.nRet = ueye.is_SetImageMem(self.hCam, self.pcImageMemory, self.MemID)
            if self.nRet != ueye.IS_SUCCESS:
                print("is_SetImageMem ERROR")
            else:
                # Set the desired color mode
                #self.nRet = ueye.is_SetColorMode(self.hCam, self.m_nColorMode)
                ueye.is_SetColorMode(self.hCam, self.m_nColorMode)
        
        #self.nRet = 
        #ueye.is_SetExternalTrigger(self.hCam, ueye.IS_SET_TRIGGER_HI_LO)        
        #ueye.is_SetTriggerDelay(self.hCam, 9960)
        
        
    def __exit__(self, _type, value, traceback):
        self.Exit()

    def Exit(self):
        ret = None
        if self.hCam is not None:
            ret = ueye.is_ExitCamera(self.hCam)
        if ret == ueye.IS_SUCCESS:
            self.hCam = None

    #def triggerMode(self, ):
    
    #def continuousMode(self, ):
    def GetExposureRange(self):
        values=ueye.IS_RANGE_F64()
        ueye.is_Exposure(self.hCam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE, values, ueye.sizeof(values))        
        return values.f64Min.value,values.f64Max.value, values.f64Inc.value

    def getExposureMax(self):
        #print(self.hcam.GetExposureRange(self))
        values=ueye.IS_RANGE_F64()
        ueye.is_Exposure(self.hCam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE, values, ueye.sizeof(values))      
        return values.f64Max.value
        
    def setExposureMax(self):
        time = ueye.double(self.getExposureMax())
        return ueye.is_Exposure(self.hCam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, time, ueye.sizeof(time))   
        
    def freezeVIdeo(self, onOff):
        if onOff:
            ueye.is_FreezeVideo(self.hCam, ueye.IS_DONT_WAIT)
        else:
            self.nRet = ueye.is_CaptureVideo(self.hCam, ueye.IS_DONT_WAIT)
            if self.nRet != ueye.IS_SUCCESS:
                print("is_CaptureVideo ERROR")

    def stopVIdeo(self, onOff):
        if onOff:
            ueye.is_StopLiveVideo(self.hCam, ueye.IS_DONT_WAIT)
        else:
            self.nRet = ueye.is_CaptureVideo(self.hCam, ueye.IS_DONT_WAIT)
            if self.nRet != ueye.IS_SUCCESS:
                print("is_CaptureVideo ERROR")
                
    def setGainBoost(self, onOff):
        if onOff:
            return ueye.is_SetGainBoost(self.hCam, ueye.IS_SET_GAINBOOST_ON)
        if not onOff:
            return ueye.is_SetGainBoost(self.hCam, ueye.IS_SET_GAINBOOST_OFF)
    
    def setExternalTrigger(self, onOff):
        if onOff:
            ueye.is_StopLiveVideo(self.hCam, ueye.IS_DONT_WAIT)
            ueye.is_SetExternalTrigger(self.hCam, ueye.IS_SET_TRIGGER_HI_LO)
            self.nRet = ueye.is_CaptureVideo(self.hCam, ueye.IS_DONT_WAIT)
            if self.nRet != ueye.IS_SUCCESS:
                print("is_CaptureVideo ERROR")
            #return ueye.is_SetExternalTrigger(self.hCam, ueye.IS_SET_TRIGGER_HI_LO)   
        if not onOff:
            ueye.is_StopLiveVideo(self.hCam, ueye.IS_DONT_WAIT)
            ueye.is_SetExternalTrigger(self.hCam, ueye.IS_SET_TRIGGER_OFF)
            self.nRet = ueye.is_CaptureVideo(self.hCam, ueye.IS_DONT_WAIT)
           
    def setTriggerDelay(self, delay):
        return ueye.is_SetTriggerDelay(self.hCam, delay)
    
    def SetGain(self,gain):
        gain=ueye.int(gain)
        ret=ueye.is_SetHWGainFactor(self.hCam,ueye.IS_SET_MASTER_GAIN_FACTOR,gain)
        return ret
        
    def SetExposure(self, time):
        time=ueye.double(time)
        return ueye.is_Exposure(self.hCam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, time, ueye.sizeof(time))        

    def SetFramerate(self, fps):
        fps=ueye.double(fps)
        newfps=ueye.double()
        ueye.is_SetFrameRate(self.hCam, fps, newfps)  
        return newfps.value

    def SetPixelclock(self, clock):
        clock=ueye.uint(clock)
        return ueye.is_PixelClock(self.hCam, ueye.IS_PIXELCLOCK_CMD_SET, clock, ueye.sizeof(clock))
    
    def GetGain(self):
        mastergain=ueye.int()
        ret= ueye.is_SetHWGainFactor(self.hCam,ueye.IS_GET_MASTER_GAIN_FACTOR,mastergain)
        return ret
        
    def GetExposure(self):
        time=ueye.double()
        ueye.is_Exposure(self.hCam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, time, ueye.sizeof(time))
        return time.value
        
    def GetFramerate(self):
        newfps=ueye.double()
        ueye.is_SetFrameRate(self.hCam, ueye.IS_GET_FRAMERATE, newfps)  
        return newfps.value

    def GetPixelclock(self):
        clock=ueye.uint()
        ueye.is_PixelClock(self.hCam, ueye.IS_PIXELCLOCK_CMD_GET, clock, ueye.sizeof(clock))
        return clock.value   
        
    def captureVideo(self):
    # Activates the camera's live video mode (free run mode)
        self.nRet = ueye.is_CaptureVideo(self.hCam, ueye.IS_DONT_WAIT)
        if self.nRet != ueye.IS_SUCCESS:
            print("is_CaptureVideo ERROR")
			
    def takeImage(self):
        # Enables the queue mode for existing image memory sequences
        self.nRet = ueye.is_InquireImageMem(self.hCam, self.pcImageMemory, self.MemID, self.width, self.height, self.nBitsPerPixel, self.pitch)
        if self.nRet == ueye.IS_SUCCESS:
            array = ueye.get_data(self.pcImageMemory, self.width, self.height, self.nBitsPerPixel, self.pitch, copy=False)
            frame = np.reshape(array,(self.height.value, self.width.value))
            return frame
		

