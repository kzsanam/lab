import sys
import qdarkstyle
from PyQt5 import  QtGui, QtWidgets, QtCore
from mainwindow import Ui_MainWindow
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import cv2
import numpy as np
#from CameraClassWrapper import IDSCam
import csv
import os
import math 
from scipy.optimize import curve_fit
#import nicelib
#from instrumental import instrument, list_instruments
#from instrumental.drivers.cameras import uc480

import os, time
#from queue import Queue
from camWork import camWork
#from pyueye import ueye
#from pyueye_example_utils import (MemoryInfo, uEyeException, Rect, get_bits_per_pixel,ImageBuffer, check)

imageSizeUIx = 600
imageSizeUIy = 480


def readSpec(specName, delimiter):
    x = np.array([])
    y = np.array([])
    with open(specName, newline='') as f:
        fr = csv.reader(f, delimiter=delimiter, quotechar='|')
        for row in fr:
            if row != []:
                y = np.append(y, row[0])
                x = np.append(x, row[1])
                
    x = x.astype(np.float)
    y = y.astype(np.float)
    return y, x
tx, ty = readSpec('transmission_losgatos.dat', ' ')    

def func(x, a, b, c, d, e, f):
     return (a + b * x + c * x ** 2 + d * x ** 3 + e * x ** 4 + f * x ** 5)
     
def transM(y, x, ty, tx):
    
    xmin = min(np.where(tx >= min(x))[0])
    xmax = max(np.where(tx <= max(x))[0])
    xmax = max(np.where(tx <= max(x))[0])
    tx1 = tx[xmin:xmax]
    ty1 = ty[xmin:xmax]
    popt, pcov = curve_fit(func, tx1, 1/ty1)
    y1 = func(x,*popt)
    y1 = (y1 > 0) * y1
    y = y * y1
    y = y / y.max()
    
    return y,x
    
def checkName(file, add):
    fileList = os.listdir('data')
    fileGood = False
    ii = -1
    while fileGood is not True:
        ii += 1
        if file + str(ii) + add not in fileList:
            file = file + str(ii)
            fileGood = True
    file = 'data/' + file + add
    return file
            
def writeSpec(file, spec):
    file = checkName(file, '.csv')
    
    with open(file, mode='w', newline='') as f:
        fw = csv.writer(f, delimiter = ',')
        for ii in range(spec[0].shape[0]):
            fw.writerow([spec[0][ii], spec[1][ii]])
            
def makeSpec(arr, topY, bottomY, pointR, pointG, waveR, waveG, backGround, backGroundUse, specLogUse):
    arr3 = np.copy(arr)
    backGround = np.copy(backGround)
    if len(arr3.shape) == 3:
        arr3 = cv2.cvtColor(arr3, cv2.COLOR_BGR2GRAY)
    
    #threshold = arr3.max()/5
    #arr3 = (arr3 > threshold) * arr3
    if pointR == pointG: 
        pointR = pointR + 1
    b = (waveR - waveG) / (pointR - pointG)
    a = waveR - b * pointR
    #topY = int(topY * arr3.shape[0]/imageSizeUIy)
    #bottomY = int(bottomY * arr3.shape[0]/imageSizeUIy)
    arr3[0:bottomY] = 0
    arr3[topY:] = 0
    pixSum = np.array([])
    pixSum = pixSum.astype(int)
    pixSum = np.sum(arr3, axis = 0)
    #print(max(pixSum))
    if backGroundUse and backGround.shape == arr3.shape:   
        #print(np.sum(backGround - backGround.astype(int)))
        #backGround = backGround.astype(int)
        backGround[0:bottomY] = 0
        backGround[topY:] = 0
        backSum = np.array([])
        backSum = np.sum(backGround, axis = 0)
        #print(max(backSum))
        diffSum = np.array([])
        diffSum = (pixSum > backSum) * (pixSum - backSum)
        #print(max(diffSum))
        yAxes = (diffSum != 0) * (diffSum/ max(diffSum)) #erase condition?
    else:
        yAxes = (pixSum != 0) * (pixSum/ max(pixSum))
        
    xAxes = np.linspace(a + b * 0, a + b * arr3.shape[1], arr3.shape[1])
    if specLogUse:
        yAxes, xAxes = transM(yAxes, xAxes, ty, tx)
    #if not (np.isnan(yAxes[0])) and yAxes[0] > 0:
        #yAxes, xAxes = transM(yAxes, xAxes)
    return yAxes, xAxes

def getCenter(image):
    image = np.copy(image)
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #threshold = image.max()/4
    #image = (image>=threshold)*image
    #moments = cv2.moments(image, 0) 
    #dM01 = moments['m01']                     # pixel sum in row
    #dM10 = moments['m10']                     # pixel sum in column
    #dArea = moments['m00']                     # pixel sum
    yAxes = np.sum(image, axis = 0) / ((max(np.sum(image, axis = 0))) + 1)
    #xAxes = np.linspace(a + b * 0, a + b * arr3.shape[1], arr3.shape[1])
    x = np.argmax(yAxes)
    y = 0
    #if dArea:
    #    x = int(dM10 / dArea)
    #    y = int(dM01 / dArea)       
    #else :
    #    y, x = image.shape
    #    y = y // 2
    #    x = x // 2
    return (int(x),int(y))
    
class Thread(QThread):
    changePixmap = pyqtSignal(QImage)
    changePixmap2 = pyqtSignal(tuple)
    
    changeFps = pyqtSignal(float)
    changeExposure = pyqtSignal(float)
    changeBoost = pyqtSignal(int)
    
    getCenterL = pyqtSignal(int)
    getCenterR = pyqtSignal(int)
    save = False
    backTake = False
    backGroundUse = False
    gainBoost = False
    specLogUse = False
    backGround = np.array([])
    backGroundAvg = []
    arrAvL = []
    topY = 640
    bottomY = 0
    WVLeft = 0
    WVRight = 10
    pointWVLeft = 10
    pointWVRight = 580
    fps = 3
    exposure = 0.02
    boost = 2000
    triggerDelay = 9960
    avgVid = 1
    findCenterLeft = False
    findCenterRight = False
    exposureMaxChecked = False
    iAv = 0
    iFAv = 0
    #camCommandSignal = pyqtSignal([list])
    cam = camWork(20)
    
    @pyqtSlot(int)
    def takeTopLevelS(self, topY):
        self.topY = topY
        
    @pyqtSlot(int)
    def takeBottomLevelS(self, bottomY):
        self.bottomY = bottomY
    
    @pyqtSlot(int)
    def takepointWVLeftS(self, pointWVLeft):
        self.pointWVLeft = pointWVLeft
    
    @pyqtSlot(int)
    def takepointWVRightS(self, pointWVRight):
        self.pointWVRight = pointWVRight

    @pyqtSlot(float)
    def takeWVLeftS(self, WVLeft):
        self.WVLeft = WVLeft

    @pyqtSlot(float)
    def takeWVRightS(self, WVRight):
        self.WVRight = WVRight
        
    @pyqtSlot()
    def takeCalimPointLeftS(self):
        self.findCenterLeft = True            
        
    @pyqtSlot()
    def takeCalimPointRightS(self):
        self.findCenterRight = True
        
    @pyqtSlot(float)
    def takeFpsS(self, fps):
        self.fps = fps
        self.cam.SetFramerate(self.fps)
    
    @pyqtSlot(float)
    def takeExposureS(self, exposure):
        self.exposure = exposure
        self.cam.SetExposure(self.exposure)
        
    @pyqtSlot(int)
    def takeBoostS(self, boost):
        self.boost = boost
        self.cam.SetGain(self.boost)
       
    @pyqtSlot(int)
    def takeTriggerDelayS(self, triggerDelay):
        self.triggerDelay = triggerDelay
        self.cam.setTriggerDelay(self.triggerDelay)
        
    @pyqtSlot(int)
    def takeAvgVidS(self, avgVid):
        self.avgVid = avgVid
        
    @pyqtSlot()
    def saveS(self):
        self.save = True

    @pyqtSlot()
    def backTakeS(self):
        self.backTake = True
        
    @pyqtSlot(bool)
    def backUseS(self, checked):
        self.backGroundUse = checked
    
    @pyqtSlot(bool)
    def gainBoostS(self, checked):
        self.cam.setGainBoost(checked)
        
        #self.gainBoost = checked
    
    @pyqtSlot(bool)
    def triggerS(self, checked):
        self.cam.setExternalTrigger(checked)
        self.cam.setTriggerDelay(self.triggerDelay)
        #self.gainBoost = checked
    
    @pyqtSlot(bool)
    def startStopS(self, checked):
        self.cam.freezeVIdeo(checked)
    
    @pyqtSlot(bool)
    def exposureMaxS(self, checked):
        self.exposureMaxChecked = checked
    
    @pyqtSlot(bool)
    def SpecLogS(self, checked):
        self.specLogUse = checked
        
    def run(self):
        self.cam.SetFramerate(self.fps)
        self.cam.SetExposure(self.exposure)
        self.cam.SetGain(self.boost)

        #self.cam.GetExposure(),
        #self.cam.GetFramerate(),
        #self.cam.GetPixelclock()
        self.cam.captureVideo()
        
        iSum = 0
        arrSum = []
        
        while True:     
            frame = self.cam.takeImage()
            self.iFAv = self.iFAv + 1
            self.arrAvL.append(np.copy(frame))
            
            if self.iFAv == self.avgVid:
                arr = np.sum(self.arrAvL, axis = 0) / self.iFAv  #np.copy(frame)
                arr = arr.astype(dtype = 'uint8')
                self.arrAvL = []
                self.iFAv = 0
                
                
                #here we compare real values and ui values
                if(self.boost != self.cam.GetGain()):
                    self.boost = self.cam.GetGain()
                    self.changeBoost.emit(self.boost)
                
                if(self.exposure != self.cam.GetExposure()):
                    self.exposure = self.cam.GetExposure()
                    self.changeExposure.emit(self.exposure)
                
                if(self.fps != self.cam.GetFramerate()):
                    self.fps = self.cam.GetFramerate()
                    self.changeFps.emit(self.fps)
                
                if self.exposureMaxChecked:
                    if self.cam.getExposureMax != self.cam.GetExposure():
                        self.cam.setExposureMax()
                
                if self.backTake:
                    self.backGroundAvg.append(arr)
                    self.iAv += 1
                    if self.iAv == 1:
                        self.backGroundAvg = np.array(self.backGroundAvg)
                        self.backGround = np.sum(self.backGroundAvg, axis = 0)/ self.iAv
                        self.backGround = self.backGround.astype(dtype = 'uint8') #dtype = 'uint')
                        self.backGroundAvg = []
                        self.iAv = 0
                        self.backTake = False
                        
                spectrum = makeSpec(arr, self.topY, self.bottomY, self.pointWVRight, self.pointWVLeft, self.WVRight, self.WVLeft, self.backGround, self.backGroundUse, self.specLogUse)
                
                #arr[0:self.topY] = 0
                #arr[self.bottomY:] = 0
                #arr[0:self.bottomY] = 0
                #arr[self.topY:] = 0
                if self.findCenterLeft == True:
                    self.findCenterLeft = False
                    xCenterL, yCenterL = getCenter(arr)
                    self.getCenterL.emit(xCenterL)

                if self.findCenterRight == True:
                    self.findCenterRight = False
                    xCenterR, yCenterR = getCenter(arr)
                    self.getCenterR.emit(xCenterR)
                    
                if self.backGround.shape == arr.shape and self.backGroundUse:
                    arr = (arr>self.backGround) * (arr - self.backGround)
                    
                if len(arr.shape) == 3:
                    h, w, ch = arr.shape    
                    bytesPerLine = ch * w
                    convertToQtFormat = QtGui.QImage(arr.data, w, h, bytesPerLine, QtGui.QImage.Format_Grayscale8)
                else:
                    h, w = arr.shape
                    bytesPerLine = w
                    
                    convertToQtFormat = QtGui.QImage(arr.data, w, h, bytesPerLine, QtGui.QImage.Format_Grayscale8)
                p = convertToQtFormat.scaled(imageSizeUIx, imageSizeUIy)#, Qt.KeepAspectRatio)
                #print(p.height())
                #print(p.width())
                painter = QPainter()
                painter.begin(p)
                painter.setPen(QPen(Qt.blue, 3))
                topYUI = int(self.topY * imageSizeUIy / arr.shape[0])
                bottomYUI = int(self.bottomY * imageSizeUIy  / arr.shape[0])
                #print(self.bottomY)
                #print(topYUI)
                pointWVRightUI = self.pointWVRight * imageSizeUIx / arr.shape[1]
                pointWVLeftUI = self.pointWVLeft * imageSizeUIx / arr.shape[1]
                painter.drawLine(0, topYUI, imageSizeUIx, topYUI)
                painter.drawLine(0, bottomYUI, imageSizeUIx, bottomYUI)
                painter.setPen(QPen(Qt.green, 3))
                painter.drawLine(pointWVRightUI, 0, pointWVRightUI, imageSizeUIy)
                painter.drawLine(pointWVLeftUI, 0, pointWVLeftUI, imageSizeUIy)
                
                painter.end()                                  
                self.changePixmap.emit(p)
                self.changePixmap2.emit(spectrum)
                
                if self.save:
                    self.save = False
                    fileIm = checkName('img', '.png')
                    cv2.imwrite(fileIm, arr)
                    writeSpec('spec', spectrum)
                    
def main():
    app = QtWidgets.QApplication( sys.argv )
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi( MainWindow )
    #ui.graphicsVideo
    #image = QPixmap("lolo.png")
    #image = image.scaled(ui.graphicsVideoL.width(), ui.graphicsVideoL.width(), Qt.KeepAspectRatio, Qt.FastTransformation)
    #ui.setImage(image)
    #ui.setImage(image)

    MainWindow.show()
    app.aboutToQuit.connect(ui.closeEvent)
    th = Thread()
    th.changePixmap.connect(ui.setImage)
    th.changePixmap2.connect(ui.setSpectrum)
    ui.takeTopLevel.connect(th.takeTopLevelS)
    ui.takeBottomLevel.connect(th.takeBottomLevelS)
    ui.takeWVLeft.connect(th.takeWVLeftS)
    ui.takeWVRight.connect(th.takeWVRightS)
    ui.takePointWVLeft.connect(th.takepointWVLeftS)
    ui.takePointWVRight.connect(th.takepointWVRightS)
    ui.takeCalimPointLeft.connect(th.takeCalimPointLeftS)
    ui.takeCalimPointRight.connect(th.takeCalimPointRightS)
    ui.takeFps.connect(th.takeFpsS)
    ui.takeExposure.connect(th.takeExposureS)
    ui.takeBoost.connect(th.takeBoostS)
    ui.takeTriggerDelay.connect(th.takeTriggerDelayS)
    ui.takeAvgVid.connect(th.takeAvgVidS)
    ui.pushButtonSave.clicked.connect(th.saveS)
    ui.pushButtonBackTake.clicked.connect(th.backTakeS)
    ui.backUse.connect(th.backUseS)
    ui.gainBoost.connect(th.gainBoostS)
    ui.trigger.connect(th.triggerS)
    ui.startStop.connect(th.startStopS)
    ui.exposureMax.connect(th.exposureMaxS)
    
    ui.SpecLog.connect(th.SpecLogS)
    th.changeFps.connect(ui.spinBoxFps.setValue)
    th.changeExposure.connect(ui.spinBoxExposure.setValue)
    th.changeBoost.connect(ui.spinBoxBoost.setValue)
    
    th.getCenterL.connect(ui.spinBoxPointWLLeft.setValue)
    th.getCenterR.connect(ui.spinBoxPointWLRight.setValue)
    #th..connect(ui.checkBoxGainBoost.isChecked)
    
    th.start()
    
    ui.spinBoxTop.setValue(999)
    ui.spinBoxBottom.setValue(452)
    ui.doubleSpinBoxWLLeft.setValue(587.49 )
    ui.doubleSpinBoxWLRight.setValue(578.74)
    ui.spinBoxPointWLRight.setValue(445)
    ui.spinBoxPointWLLeft.setValue(100)
 
    sys.exit( app.exec_() )
    
if __name__ == "__main__":
    main()