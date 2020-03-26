from pyueye import ueye
from pyueye_example_utils import (uEyeException, Rect, get_bits_per_pixel,
                                  ImageBuffer, check)


class Camera:
    def __init__(self, device_id=0):
        self.h_cam = ueye.HIDS(device_id)
        self.img_buffers = []

    def __enter__(self):
        self.Init()
        return self

    def __exit__(self, _type, value, traceback):
        self.Exit()

    def Handle(self):
        return self.h_cam

    def Alloc(self, buffer_count=10):
        rect = self.GetAoi()
        bpp = get_bits_per_pixel(self.GetColormode())

        for buff in self.img_buffers:
            check(ueye.is_FreeImageMem(self.h_cam, buff.mem_ptr, buff.mem_id))

        for i in range(buffer_count):
            buff = ImageBuffer()
            ueye.is_AllocImageMem(self.h_cam,
                                  rect.width, rect.height, bpp,
                                  buff.mem_ptr, buff.mem_id)

            check(ueye.is_AddToSequence(self.h_cam, buff.mem_ptr, buff.mem_id))

            self.img_buffers.append(buff)

        ueye.is_InitImageQueue(self.h_cam, 0)

    def Init(self):
        ret = ueye.is_InitCamera(self.h_cam, None)
        if ret != ueye.IS_SUCCESS:
            self.h_cam = None
            raise uEyeException(ret)
        return ret

    def GetNumberOfCameras(self):
        number=ueye.int()
        ret = ueye.is_GetNumberOfCameras(number)
        if ret != ueye.IS_SUCCESS:
            self.h_cam = None
            raise uEyeException(ret)
        return number

    def GetSerialNumber(self):
        result=ueye.CAMINFO()
        ret = ueye.is_GetCameraInfo(self.h_cam, result)
        if ret != ueye.IS_SUCCESS:
            self.h_cam = None
            raise uEyeException(ret)
        return result.SerNo.decode()

    def GetDeviceID(self):
        result=ueye.CAMINFO()
        ret = ueye.is_GetCameraInfo(self.h_cam, result)
        if ret != ueye.IS_SUCCESS:
            self.h_cam = None
            raise uEyeException(ret)
        return result.Select

    def SetDeviceID(self, ID):
        ID=ueye.int(ID)
        ret = ueye.is_SetCameraID(self.h_cam, ID)
        if ret != ueye.IS_SUCCESS:
            self.h_cam = None
            raise uEyeException(ret)
        return ret

    def Exit(self):
        ret = None
        if self.h_cam is not None:
            ret = ueye.is_ExitCamera(self.h_cam)
        if ret == ueye.IS_SUCCESS:
            self.h_cam = None

    def GetAoi(self,readable=0):
        rect_aoi = ueye.IS_RECT()
        ueye.is_AOI(self.h_cam, ueye.IS_AOI_IMAGE_GET_AOI, rect_aoi, ueye.sizeof(rect_aoi))
        if readable==0:
            return Rect(rect_aoi.s32X.value,
                    rect_aoi.s32Y.value,
                    rect_aoi.s32Width.value,
                    rect_aoi.s32Height.value)
        else:
            return rect_aoi.s32X.value, rect_aoi.s32Y.value, rect_aoi.s32Width.value, rect_aoi.s32Height.value

    def SetAoi(self, x, y, width, height):
        rect_aoi = ueye.IS_RECT()
        rect_aoi.s32X = ueye.int(x)
        rect_aoi.s32Y = ueye.int(y)
        rect_aoi.s32Width = ueye.int(width)
        rect_aoi.s32Height = ueye.int(height)
        return ueye.is_AOI(self.h_cam, ueye.IS_AOI_IMAGE_SET_AOI, rect_aoi, ueye.sizeof(rect_aoi))

    def SetExposure(self, time):
        time=ueye.double(time)
        return ueye.is_Exposure(self.h_cam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, time, ueye.sizeof(time))        

    def GetExposure(self):
        time=ueye.double()
        ueye.is_Exposure(self.h_cam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, time, ueye.sizeof(time))
        return time.value

    def GetExposureRange(self):
        values=ueye.IS_RANGE_F64()
        ueye.is_Exposure(self.h_cam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE, values, ueye.sizeof(values))        
        return values.f64Min.value,values.f64Max.value, values.f64Inc.value

    def SetPixelclock(self, clock):
        clock=ueye.uint(clock)
        return ueye.is_PixelClock(self.h_cam, ueye.IS_PIXELCLOCK_CMD_SET, clock, ueye.sizeof(clock))

    def GetPixelclock(self):
        clock=ueye.uint()
        ueye.is_PixelClock(self.h_cam, ueye.IS_PIXELCLOCK_CMD_GET, clock, ueye.sizeof(clock))
        return clock.value   

    def GetPixelclockRange(self):
        values=ueye.IS_RANGE_S32()
        ueye.is_PixelClock(self.h_cam, ueye.IS_PIXELCLOCK_CMD_GET_RANGE, values, ueye.sizeof(values))        
        return values.s32Min.value,values.s32Max.value, values.s32Inc.value

    def SetFramerate(self, fps):
        fps=ueye.double(fps)
        newfps=ueye.double()
        ueye.is_SetFrameRate(self.h_cam, fps, newfps)  
        return newfps.value

    def GetFramerate(self):
        newfps=ueye.double()
        ueye.is_SetFrameRate(self.h_cam, ueye.IS_GET_FRAMERATE, newfps)  
        return newfps.value

    def GetFramerateRange(self):
        min=ueye.double()   
        max=ueye.double()
        inc=ueye.double()   
        ueye.is_GetFrameTimeRange(self.h_cam,min,max,inc)        
        return 1./max.value,1./min.value,1./(min.value+inc.value)

    def GetActualLiveFramerate(self):
        fps=ueye.double()
        ueye.is_GetFramesPerSecond(self.h_cam,fps)
        return fps.value

    def GetMissedImagesCount(self):
        status=ueye.UEYE_CAPTURE_STATUS_INFO()
        ueye.is_CaptureStatus(self.h_cam,ueye.IS_CAPTURE_STATUS_INFO_CMD_GET,status,ueye.sizeof(status))
        return status.adwCapStatusCnt_Detail[ueye.IS_CAP_STATUS_USB_TRANSFER_FAILED].value

    def CaptureVideo(self, wait=False):
        wait_param = ueye.IS_WAIT if wait else ueye.IS_DONT_WAIT
        return ueye.is_CaptureVideo(self.h_cam, wait_param)

    def StopVideo(self):
        return ueye.is_StopLiveVideo(self.h_cam, ueye.IS_FORCE_VIDEO_STOP)

    def FreezeVideo(self, wait=False):
        wait_param = ueye.IS_WAIT if wait else ueye.IS_DONT_WAIT
        return ueye.is_FreezeVideo(self.h_cam, wait_param)

    def SetColormode(self, colormode):
        return ueye.is_SetColorMode(self.h_cam, colormode)

    def GetColormode(self):
        ret = ueye.is_SetColorMode(self.h_cam, ueye.IS_GET_COLOR_MODE)
        return ret

    def GetFormatList(self):
        count = ueye.UINT()
        check(ueye.is_ImageFormat(self.h_cam, ueye.IMGFRMT_CMD_GET_NUM_ENTRIES, count, ueye.sizeof(count)))
        format_list = ueye.IMAGE_FORMAT_LIST(ueye.IMAGE_FORMAT_INFO * count.value)
        format_list.nSizeOfListEntry = ueye.sizeof(ueye.IMAGE_FORMAT_INFO)
        format_list.nNumListElements = count.value
        check(ueye.is_ImageFormat(self.h_cam, ueye.IMGFRMT_CMD_GET_LIST,
                                  format_list, ueye.sizeof(format_list)))
        return format_list

    def GetGain(self):
        mastergain=ueye.int()
        ret= ueye.is_SetHWGainFactor(self.h_cam,ueye.IS_GET_MASTER_GAIN_FACTOR,mastergain)
        return ret

    def SetGain(self,gain):
        gain=ueye.int(gain)
        ret=ueye.is_SetHWGainFactor(self.h_cam,ueye.IS_SET_MASTER_GAIN_FACTOR,gain)
        return ret