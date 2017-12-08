# -*- coding: utf-8 -*-

import sys
from PyQt5.QtCore import Qt,QPoint,QPointF
from PyQt5.QtWidgets import QWidget,QApplication,QVBoxLayout,QHBoxLayout,QPushButton,QLineEdit,QGroupBox,QGridLayout,QLabel,QTabWidget,QFileDialog,QComboBox,QButtonGroup
from PyQt5.QtGui import QPixmap,QImage,QPainter,QPen,QPolygonF,QTransform
import random
import csv
from PIL import Image
import os
import numpy as np

class MapView(QWidget):
  def __init__(self,securityRange):
    super().__init__()

    self.px = None
    self.py = None
    self.points = []
    self.psets = []
    self.securityLine = [[False] * 801 for i in range(801)]# 801x801の２次元配列
    self.Landing_Range = [[1] * 4 for i in range(56)]
    self.buffer = []
    self.startingPoint = [220,243]
    self.landingPoint = [[QPoint(0,0)]*9 for i in range(7)]
    

    self.securityRange = securityRange

    self.loadSecurityRange()

    self.setMinimumSize(600, 600)
    self.setMaximumSize(600,600)
    # pic = Image.open(os.path.dirname(os.path.abspath(sys.argv[0]))+'/pic/TaikiLand8deg.png').resize((560,560),Image.LANCZOS) #ここでピクセル指定する。
    # pic.save(os.path.dirname(os.path.abspath(sys.argv[0]))+'/pic/map.png')

    self.image = QImage(os.path.dirname(os.path.abspath(sys.argv[0]))+'/'+settingFile+'/map.png')

  def drawLandingRange(self,Landing_Range,scalefacter,lanchpoint):
    for i in range(56):
      for j in range(2): 
        Landing_Range[i][2*j] = Landing_Range[i][2*j]/scalefacter+lanchpoint[0]
        Landing_Range[i][1+2*j] = -Landing_Range[i][1+2*j]/scalefacter+lanchpoint[1]

    for i in range(56):
      self.landingPoint[i//8][i%8] = QPoint(Landing_Range[i][0],Landing_Range[i][1])
      if(i%8 == 7): self.landingPoint[i//8][8] = self.landingPoint[i//8][0]
    
    self.update()

  def paintEvent(self, e):
    
    painter = QPainter(self)
    pen = QPen()

    painter.drawImage(0, 0,self.image)
    
    painter.drawPoint(0,0)
    painter.setPen(Qt.red)
    
    # for points in self.list:
      # painter.drawPolyline(*points)
    painter.drawPoint(int(self.startingPoint[0]),self.startingPoint[1])

    # draw securityRange
    for i in range(560): 
      for j in range(560):
        if(self.securityRange[i][j]=='True'):
          pass
          # painter.drawPoint(i,j)

    painter.setPen(QPen(Qt.yellow, 1, Qt.SolidLine))

    for points in self.landingPoint:
      painter.drawPolyline(*points)

    # draw lanchpoint
    # painter.drawPoint(self.lanchpoint[0],self.lanchpoint[1])



    for points in self.psets: 
      painter.drawPolyline(*points) 

    painter.drawLine(496, 556, 549, 556) # scale config
  
  def mousePressEvent(self, event):
    self.points.append(event.pos())
    self.update()
  
  # def mouseMoveEvent(self, event):
  #   self.points.append(event.pos())
  #   self.update()
  
  # def mouseReleaseEvent(self, event):
  #   self.pressed = False
  #   self.psets.append(self.points)
  #   self.update()
  
  def loadSecurityRange(self):
    with open(os.path.dirname(os.path.abspath(sys.argv[0]))+'/'+settingFile+'/securityRange.csv', 'r') as file:
      reader = csv.reader(file)
      for (i,line)  in zip(range(560),reader):
        for (j,row)  in zip(range(560),line):
          self.securityRange[i][j] = row