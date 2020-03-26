# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage
import numpy as np 
 
imageSizeUIx = 600
imageSizeUIy = 480

def restore(settings):
    finfo = QFileInfo(settings.fileName())
    print((settings.fileName()))
    print('lolo')
    if finfo.exists() and finfo.isFile():
        print('lolo')
        for w in qApp.allWidgets():
            mo = w.metaObject()
            if w.objectName() != "":
                for i in range(mo.propertyCount()):
                    name = mo.property(i).name()
                    val = settings.value("{}/{}".format(w.objectName(), name), w.property(name))
                    w.setProperty(name, val)
                    print('lolo')

def save(settings):
    print(settings.fileName())
    for w in qApp.allWidgets():
        mo = w.metaObject()
        if w.objectName() != "":
            for i in range(mo.propertyCount()):
                name = mo.property(i).name()
                #print(w.objectName())
                #print(w.property(name))
                settings.setValue("{}/{}".format(w.objectName(), name), w.property(name))
                

class Ui_MainWindow(QObject):
    takeTopLevel = pyqtSignal(int)
    takeBottomLevel = pyqtSignal(int)
    takeWVLeft = pyqtSignal(float)
    takeWVRight = pyqtSignal(float)
    takePointWVLeft =  pyqtSignal(int)
    takePointWVRight =  pyqtSignal(int)
    takeCalimPointLeft = pyqtSignal()
    takeCalimPointRight = pyqtSignal()
    takeFps = pyqtSignal(float)
    takeExposure = pyqtSignal(float)
    takeBoost = pyqtSignal(int)
    takeTriggerDelay = pyqtSignal(int)
    takeAvgVid = pyqtSignal(int)
    backUse = pyqtSignal(bool)
    SpecLog = pyqtSignal(bool)
    gainBoost = pyqtSignal(bool)
    trigger = pyqtSignal(bool)
    exposureMax = pyqtSignal(bool)
    startStop = pyqtSignal(bool)
    
    settings = QSettings("gui.ini", QSettings.IniFormat)
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 1000)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        #video
        #image = QPixmap("lolo.png")
        self.graphicsVideoL = QLabel(self.centralWidget)
        self.graphicsVideoL.setGeometry(QtCore.QRect(20, 2, imageSizeUIx, imageSizeUIy))
        self.graphicsVideoL.setObjectName("graphicsVideoL")
        #self.graphicsVideoL.setPixmap(image)
		#spectrum
        self.graphicsSpectrum = pg.PlotWidget(self.centralWidget)
        #self.graphicsSpectrum = QLabel(self.centralWidget)
        self.graphicsSpectrum.setGeometry(QtCore.QRect(20, 485, imageSizeUIx, imageSizeUIy - 40))
        self.graphicsSpectrum.setObjectName("graphicsSpectrum")
		
        #self.graphicsSpectrum = QtWidgets.QGraphicsView(self.centralWidget)
        #self.graphicsSpectrum.setGeometry(QtCore.QRect(40, 310, 521, 281))
        #self.graphicsSpectrum.setObjectName("graphicsSpectrum")
		
		#parameters of the camera
        self.groupBoxCamParam = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBoxCamParam.setGeometry(QtCore.QRect(630, 20, 400, 150))
        self.groupBoxCamParam.setObjectName("groupBoxCamParam")
        
        self.labelStartStop = QtWidgets.QLabel(self.groupBoxCamParam)
        self.labelStartStop.setGeometry(QtCore.QRect(10, 30, 60, 20))
        self.labelStartStop.setObjectName("labelStartStop")

        self.checkBoxStartStop = QtWidgets.QCheckBox(self.groupBoxCamParam)
        self.checkBoxStartStop.setGeometry(QtCore.QRect(80, 30, 20, 20))
        self.checkBoxStartStop.setObjectName("checkBoxStartStop")
        
        self.labelFps = QtWidgets.QLabel(self.groupBoxCamParam)
        self.labelFps.setGeometry(QtCore.QRect(10, 50, 60, 20))
        self.labelFps.setObjectName("labelFps")
        self.labelExposure = QtWidgets.QLabel(self.groupBoxCamParam)
        self.labelExposure.setGeometry(QtCore.QRect(10, 70, 60, 20))
        self.labelExposure.setObjectName("labelExposure")
        
        self.labelExposureMax = QtWidgets.QLabel(self.groupBoxCamParam)
        self.labelExposureMax.setGeometry(QtCore.QRect(150, 70, 60, 20))
        self.labelExposureMax.setObjectName("labelExposureMax")
        
        self.checkBoxExposureMax = QtWidgets.QCheckBox(self.groupBoxCamParam)
        self.checkBoxExposureMax.setGeometry(QtCore.QRect(220, 70, 20, 20))
        self.checkBoxExposureMax.setObjectName("checkBoxExposureMax")
        
        self.labelBoost = QtWidgets.QLabel(self.groupBoxCamParam)
        self.labelBoost.setGeometry(QtCore.QRect(10, 90, 60, 20))
        self.labelBoost.setObjectName("labelBoost")
        
        self.labelGainBoost = QtWidgets.QLabel(self.groupBoxCamParam)
        self.labelGainBoost.setGeometry(QtCore.QRect(150, 90, 60, 20))
        self.labelGainBoost.setObjectName("labelGainBoost")
        
        self.spinBoxFps = QtWidgets.QDoubleSpinBox(self.groupBoxCamParam)
        self.spinBoxFps.setMaximum(1000)
        self.spinBoxFps.setGeometry(QtCore.QRect(80, 50, 60, 20))
        self.spinBoxFps.setValue(3)
        self.spinBoxFps.setObjectName("spinBoxFps")
        
        self.labelTrigger = QtWidgets.QLabel(self.groupBoxCamParam)
        self.labelTrigger.setGeometry(QtCore.QRect(150, 50, 65, 20))
        self.labelTrigger.setObjectName("labelTrigger")
        
        self.checkBoxTrigger = QtWidgets.QCheckBox(self.groupBoxCamParam)
        self.checkBoxTrigger.setGeometry(QtCore.QRect(220, 50, 20, 20))
        self.checkBoxTrigger.setObjectName("checkBoxTrigger")
        
        self.labelTriggerDelay = QtWidgets.QLabel(self.groupBoxCamParam)
        self.labelTriggerDelay.setGeometry(QtCore.QRect(250, 50, 35, 20))
        self.labelTriggerDelay.setObjectName("labelTriggerDelay")
        
        self.spinBoxTriggerDelay = QtWidgets.QDoubleSpinBox(self.groupBoxCamParam)
        self.spinBoxTriggerDelay.setMaximum(100000)
        self.spinBoxTriggerDelay.setGeometry(QtCore.QRect(290, 50, 100, 20))
        self.spinBoxTriggerDelay.setValue(9960)
        self.spinBoxTriggerDelay.setObjectName("spinBoxTriggerDelay")
        
        self.spinBoxExposure = QtWidgets.QDoubleSpinBox(self.groupBoxCamParam)
        self.spinBoxExposure.setMaximum(1000)
        self.spinBoxExposure.setMinimum(0.001)
        self.spinBoxExposure.setGeometry(QtCore.QRect(80, 70, 60, 20))
        self.spinBoxExposure.setValue(300)
        self.spinBoxExposure.setObjectName("spinBoxExposure")
        self.spinBoxBoost = QtWidgets.QSpinBox(self.groupBoxCamParam)
        self.spinBoxBoost.setMaximum(10000)
        self.spinBoxBoost.setGeometry(QtCore.QRect(80, 90, 60, 20))
        self.spinBoxBoost.setValue(10000)
        self.spinBoxBoost.setObjectName("spinBoxBoost")
        self.spinBoxBoost.setSingleStep(100)
        self.checkBoxGainBoost = QtWidgets.QCheckBox(self.groupBoxCamParam)
        self.checkBoxGainBoost.setGeometry(QtCore.QRect(220, 90, 20, 20))
        self.checkBoxGainBoost.setObjectName("checkBoxGainBoost")
        
        self.labelAvgVid = QtWidgets.QLabel(self.groupBoxCamParam)
        self.labelAvgVid.setGeometry(QtCore.QRect(10, 110, 60, 20))
        self.labelAvgVid.setObjectName("labelAvgVid")

        self.spinBoxAvgVid = QtWidgets.QSpinBox(self.groupBoxCamParam)
        self.spinBoxAvgVid.setMaximum(1000)
        self.spinBoxAvgVid.setGeometry(QtCore.QRect(80, 110, 60, 20))
        self.spinBoxAvgVid.setValue(1)
        self.spinBoxAvgVid.setObjectName("spinBoxAvgVid")
        self.spinBoxAvgVid.setSingleStep(1)
        
		#lines for area
        self.groupBox = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox.setGeometry(QtCore.QRect(630, 170, 311, 81))
        self.groupBox.setObjectName("areaForSpec")
        self.spinBoxBottom = QtWidgets.QSpinBox(self.groupBox)
        self.spinBoxBottom.setMaximum(10000)
        self.spinBoxBottom.setGeometry(QtCore.QRect(63, 50, 60, 22))
        self.spinBoxBottom.setValue(10)
        self.spinBoxBottom.setObjectName("spinBoxBottom")
        self.spinBoxTop = QtWidgets.QSpinBox(self.groupBox)
        self.spinBoxTop.setMaximum(10000)
        self.spinBoxTop.setGeometry(QtCore.QRect(63, 20, 60, 22))
        self.spinBoxTop.setValue(470)
        self.spinBoxTop.setObjectName("spinBoxTop")
        self.spinBoxLeft = QtWidgets.QSpinBox(self.groupBox)
        self.spinBoxLeft.setGeometry(QtCore.QRect(170, 20, 42, 22))
        self.spinBoxLeft.setObjectName("spinBoxLeft")
        self.spinBoxRight = QtWidgets.QSpinBox(self.groupBox)
        self.spinBoxRight.setGeometry(QtCore.QRect(170, 50, 42, 22))
        self.spinBoxRight.setObjectName("spinBoxRight")
		
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 20, 50, 17))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(10, 50, 50, 17))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(120, 20, 50, 17))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(120, 50, 50, 17))
        self.label_4.setObjectName("label_4")

        #calibration
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBox_3.setGeometry(QtCore.QRect(630, 250, 311, 151))
        self.groupBox_3.setObjectName("calibration")
		
        self.pushButtonTakeLeftPoint = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButtonTakeLeftPoint.setGeometry(QtCore.QRect(10, 30, 101, 23))
        self.pushButtonTakeLeftPoint.setObjectName("pushButtonTakeLeftPoint")
		
        self.pushButtonTakeRightPoint = QtWidgets.QPushButton(self.groupBox_3)
        self.pushButtonTakeRightPoint.setGeometry(QtCore.QRect(160, 30, 101, 23))
        self.pushButtonTakeRightPoint.setObjectName("pushButtonTakeRightPoint")
		
        self.label_6 = QtWidgets.QLabel(self.groupBox_3)
        self.label_6.setGeometry(QtCore.QRect(10, 60, 61, 16))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.groupBox_3)
        self.label_7.setGeometry(QtCore.QRect(160, 60, 61, 16))
        self.label_7.setObjectName("label_7")
		
        self.labelLeftPoint = QtWidgets.QLabel(self.groupBox_3)
        self.labelLeftPoint.setGeometry(QtCore.QRect(10, 90, 61, 16))
        self.labelLeftPoint.setObjectName("labelLeftPoint")
        self.labelRightPoint = QtWidgets.QLabel(self.groupBox_3)
        self.labelRightPoint.setGeometry(QtCore.QRect(160, 90, 61, 16))
        self.labelRightPoint.setObjectName("labelRightPoint")
		
        self.spinBoxPointWLLeft = QtWidgets.QSpinBox(self.groupBox_3)
        self.spinBoxPointWLLeft.setGeometry(QtCore.QRect(80, 60, 70, 22))
        self.spinBoxPointWLLeft.setObjectName("spinBoxCalibrationLeft")
        self.spinBoxPointWLLeft.setMaximum(10000)
        self.spinBoxPointWLLeft.setValue(20)
		
        self.spinBoxPointWLRight = QtWidgets.QSpinBox(self.groupBox_3)
        self.spinBoxPointWLRight.setGeometry(QtCore.QRect(230, 60, 70, 22))
        self.spinBoxPointWLRight.setObjectName("spinBox_3")
        self.spinBoxPointWLRight.setMaximum(10000)
        self.spinBoxPointWLRight.setValue(580)
		
        self.doubleSpinBoxWLLeft = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBoxWLLeft.setGeometry(QtCore.QRect(80, 90, 70, 22))
        self.doubleSpinBoxWLLeft.setObjectName("doubleSpinBoxWLLeft")
        self.doubleSpinBoxWLLeft.setMaximum(2000)
        self.doubleSpinBoxWLLeft.setValue(580)
		
        self.doubleSpinBoxWLRight = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBoxWLRight.setGeometry(QtCore.QRect(230, 90, 70, 22))
        self.doubleSpinBoxWLRight.setObjectName("doubleSpinBoxWLRight")
        self.doubleSpinBoxWLRight.setMaximum(2000)
        
        #spectum
        self.groupBoxSpec = QtWidgets.QGroupBox(self.centralWidget)
        self.groupBoxSpec.setGeometry(QtCore.QRect(630, 450, 311, 250))
        self.groupBoxSpec.setObjectName("calibration")
        
        self.pushButtonSave = QtWidgets.QPushButton(self.groupBoxSpec)
        self.pushButtonSave.setText("save")
        self.pushButtonSave.setGeometry(QtCore.QRect(20, 40, 100, 22))
        
        self.pushButtonBackTake = QtWidgets.QPushButton(self.groupBoxSpec)
        self.pushButtonBackTake.setText("take background")
        self.pushButtonBackTake.setGeometry(QtCore.QRect(20, 70, 100, 22))   
        
        #self.labelBackGTake = QtWidgets.QLabel(self.groupBoxSpec)
        #self.labelBackGTake.setGeometry(QtCore.QRect(20, 70, 130, 20))
        #self.labelBackGTake.setObjectName("labelBackGTake")
        #self.labelBackGTake.setText("take background")        

        #self.checkBoxBackGTake = QtWidgets.QCheckBox(self.groupBoxSpec)
        #self.checkBoxBackGTake.setGeometry(QtCore.QRect(140, 70, 20, 20))
        #self.checkBoxBackGTake.setObjectName("checkBoxBackGTake")

        self.labelBackGUse = QtWidgets.QLabel(self.groupBoxSpec)
        self.labelBackGUse.setGeometry(QtCore.QRect(20, 100, 130, 20))
        self.labelBackGUse.setObjectName("labelBackGUse")
        self.labelBackGUse.setText("use background")      
        
        self.checkBoxBackGUse = QtWidgets.QCheckBox(self.groupBoxSpec)
        self.checkBoxBackGUse.setGeometry(QtCore.QRect(140, 100, 20, 20))
        self.checkBoxBackGUse.setObjectName("checkBoxBackGUse")
        
        self.labelSpecLog1 = QtWidgets.QLabel(self.groupBoxSpec)
        self.labelSpecLog1.setGeometry(QtCore.QRect(20, 160, 130, 20))
        self.labelSpecLog1.setObjectName("labelSpecLog1")
        self.labelSpecLog1.setText("set log scale") 

        self.checkBoxSpecLog1 = QtWidgets.QCheckBox(self.groupBoxSpec)
        self.checkBoxSpecLog1.setGeometry(QtCore.QRect(140, 160, 20, 20))
        self.checkBoxSpecLog1.setObjectName("checkBoxSpecLog1")
        
        self.labelSpecLog = QtWidgets.QLabel(self.groupBoxSpec)
        self.labelSpecLog.setGeometry(QtCore.QRect(20, 130, 130, 20))
        self.labelSpecLog.setObjectName("labelSpecLog")
        self.labelSpecLog.setText("add transmission")     
        
        self.checkBoxSpecLog = QtWidgets.QCheckBox(self.groupBoxSpec)
        self.checkBoxSpecLog.setGeometry(QtCore.QRect(140, 130, 20, 20))
        self.checkBoxSpecLog.setObjectName("checkBoxSpecLog")
        
        #menu
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1063, 21))
        self.menuBar.setObjectName("menuBar")
        self.menufile = QtWidgets.QMenu(self.menuBar)
        self.menufile.setObjectName("menufile")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.menuBar.addAction(self.menufile.menuAction())

        self.spinBoxTop.valueChanged.connect(self.valuechangeTopY)
        self.spinBoxBottom.valueChanged.connect(self.valuechangeBottomY)
        self.doubleSpinBoxWLLeft.valueChanged.connect(self.valuechangeWLLeft)
        self.doubleSpinBoxWLRight.valueChanged.connect(self.valuechangeWLRight)
        self.spinBoxPointWLRight.valueChanged.connect(self.valuechangePointWLRight)
        self.spinBoxPointWLLeft.valueChanged.connect(self.valuechangePointWLLeft)
        self.pushButtonTakeLeftPoint.clicked.connect(self.CalimPointLeft)
        self.pushButtonTakeRightPoint.clicked.connect(self.CalimPointRight)
        self.checkBoxBackGUse.stateChanged.connect(self.backUseChanged)
        self.checkBoxGainBoost.stateChanged.connect(self.gainBoostChanged)
        self.checkBoxStartStop.stateChanged.connect(self.startStopChanged) 
        self.checkBoxTrigger.stateChanged.connect(self.triggerChanged)
        self.checkBoxExposureMax.stateChanged.connect(self.exposureMaxChanged)
        self.checkBoxSpecLog.stateChanged.connect(self.SpecLogChanged)
        self.checkBoxSpecLog1.stateChanged.connect(self.SpecLogChanged1)
        
        self.spinBoxFps.valueChanged.connect(self.valueChangeFps)
        self.spinBoxExposure.valueChanged.connect(self.valueChangeExposure)
        self.spinBoxBoost.valueChanged.connect(self.valueChangeBoost)
        self.spinBoxTriggerDelay.valueChanged.connect(self.valueChangeTriggerDelay)
        self.spinBoxAvgVid.valueChanged.connect(self.valueAvgVid)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
		
        #restore
        #restore(self.settings)
        
    @pyqtSlot(QImage)
    def setImage(self, image):
        self.graphicsVideoL.setPixmap(QPixmap.fromImage(image))
      
    @pyqtSlot(tuple)
    def setSpectrum(self, spectrum):
        #if not (np.isnan(spectrum[0][0])) or spectrum[0] == []:
        self.graphicsSpectrum.plot(spectrum[1], spectrum[0], clear=True)
            
    def SpecLogChanged1(self):
        if self.checkBoxSpecLog1.isChecked():
            self.graphicsSpectrum.setLogMode(y = True)
        else:
            self.graphicsSpectrum.setLogMode(y = False)

    @pyqtSlot(float)
    def changeFpsS(self, fps):
        self.spinBoxFps.setValue(fps)

    @pyqtSlot(float)
    def changeExposureS(self, exposure):
        self.spinBoxExposure.setValue(exposure)

    @pyqtSlot(float)
    def changeBoostS(self, boost):
        self.spinBoxBoost.setValue(boost)   
	
    def CalimPointLeft(self):
        self.takeCalimPointLeft.emit()

    def CalimPointRight(self):
        self.takeCalimPointRight.emit()
		
    def valuechangeTopY(self):
        self.takeTopLevel.emit(self.spinBoxTop.value())
	  
    def valuechangeBottomY(self):
        self.takeBottomLevel.emit(self.spinBoxBottom.value())
		
    def valuechangeWLLeft(self):
        self.takeWVLeft.emit(self.doubleSpinBoxWLLeft.value())
		
    def valuechangeWLRight(self):
        self.takeWVRight.emit(self.doubleSpinBoxWLRight.value())
	
    def valuechangePointWLRight(self):
        self.takePointWVRight.emit(self.spinBoxPointWLRight.value())
	
    def valuechangePointWLLeft(self):
        self.takePointWVLeft.emit(self.spinBoxPointWLLeft.value())
        
    def valueChangeFps(self):
        self.takeFps.emit(self.spinBoxFps.value())
        
    def valueChangeExposure(self):
        self.takeExposure.emit(self.spinBoxExposure.value())

    def valueChangeBoost(self):
        self.takeBoost.emit(self.spinBoxBoost.value())
    
    def valueChangeTriggerDelay(self):
        self.takeTriggerDelay.emit(self.spinBoxTriggerDelay.value())
        
    def valueAvgVid(self):
        self.takeAvgVid.emit(self.spinBoxAvgVid.value())
        
    def backUseChanged(self):
        self.backUse.emit(self.checkBoxBackGUse.isChecked())
   
    def gainBoostChanged(self):
        self.gainBoost.emit(self.checkBoxGainBoost.isChecked())
        
    def triggerChanged(self):
        self.trigger.emit(self.checkBoxTrigger.isChecked())
    
    def exposureMaxChanged(self):
        self.exposureMax.emit(self.checkBoxExposureMax.isChecked())
    
    def startStopChanged(self):
        self.startStop.emit(self.checkBoxStartStop.isChecked())
        
    def SpecLogChanged(self):
        self.SpecLog.emit(self.checkBoxSpecLog.isChecked())
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "area for the spectrum"))
        self.label.setText(_translate("MainWindow", "y top"))
        self.label_2.setText(_translate("MainWindow", "y bottom"))
        self.label_3.setText(_translate("MainWindow", "x left"))
        self.label_4.setText(_translate("MainWindow", "x right"))
        self.groupBoxCamParam.setTitle(_translate("MainWindow", "parameters of the camera"))
        self.labelStartStop.setText(_translate("MainWindow", "start/stop"))
        self.labelFps.setText(_translate("MainWindow", "fps"))
        self.labelExposure.setText(_translate("MainWindow", "exposure"))
        self.labelExposureMax.setText(_translate("MainWindow", "max exp."))
        self.labelBoost.setText(_translate("MainWindow", "boost"))
        self.labelGainBoost.setText(_translate("MainWindow", "gain_boost"))
        self.labelTrigger.setText(_translate("MainWindow", "ext. trigger"))
        self.labelTriggerDelay.setText(_translate("MainWindow", "delay"))
        self.labelAvgVid.setText(_translate("MainWindow", "avg"))
        
        self.groupBox_3.setTitle(_translate("MainWindow", "calibration"))
        self.groupBoxSpec.setTitle(_translate("MainWindow", "spectrum"))        
        self.pushButtonTakeLeftPoint.setText(_translate("MainWindow", "take left point"))
        self.pushButtonTakeRightPoint.setText(_translate("MainWindow", "take right point"))
        self.label_6.setText(_translate("MainWindow", "coordinate"))
        self.label_7.setText(_translate("MainWindow", "coordinate"))
        self.labelLeftPoint.setText(_translate("MainWindow", "wavelenght"))
        self.labelRightPoint.setText(_translate("MainWindow", "wavelenght"))
        self.menufile.setTitle(_translate("MainWindow", "file"))


    
    def closeEvent(self):
        #MainWindow.
        save(self.settings)
        #QMainWindow.closeEvent(self)
        print("event")