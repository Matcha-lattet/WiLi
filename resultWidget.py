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

class resultWidget(QWidget):
  def __init__(self, parent=None):
    super(resultWidget, self).__init__()
    
    Vbox = QVBoxLayout()
    
    landingRange_box = QHBoxLayout()
    self.open_button = QPushButton('Open')
    self.landingRange_textbox = QLineEdit()
    self.landingRange_textbox.setReadOnly(True)
    landingRange_box.addWidget(self.open_button)
    landingRange_box.addWidget(self.landingRange_textbox)
     
    button_box = QHBoxLayout()
    self.judge_button = QPushButton('Judge')
    button_box.addWidget(self.judge_button)

    windlimit = QGroupBox("風向風速制限")
      
    self.grid = QGridLayout()
    azimuth_list = ['E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE']
       
    positions = [(j,0) for j in range(8)]
    self.azimuth_label = []
    for i,positions,name in zip(range(8),positions,azimuth_list):
      self.azimuth_label.append(QLabel(name))
      self.grid.addWidget(self.azimuth_label[i], *positions)
    
    positions = [(j,1) for j in range(8)]
    self.windLimit_label = []
    for i,positions in zip(range(8),positions):
      self.windLimit_label.append(QLabel('NaN'))
      self.grid.addWidget(self.windLimit_label[i],*positions)
    
    windlimit.setLayout(self.grid)

    self.radarchart = radarChart()
    
    Vbox.addLayout(landingRange_box)
    Vbox.addLayout(button_box)
    Vbox.addWidget(windlimit)
    Vbox.addWidget(self.radarchart)
  
    self.setLayout(Vbox)

  
  def load_data(self,Landing_Range,scalefacter,lanchpoint):
    filename = QFileDialog.getOpenFileName(self, 'Open file', os.path.expanduser(os.path.dirname(os.path.abspath(sys.argv[0]))+'/Landing_Range_v2.csv'))
    self.landingRange_textbox.setText(filename[0])

    with open(filename[0], 'r') as file:
      reader = csv.reader(file)
      for (i,line)  in zip(range(56),reader):
        for (j,row)  in zip(range(4),line):
          Landing_Range[i][j] = int(float(row))
    
    # for i in range(56):
    #   for j in range(2): 
    #     Landing_Range[i][2*j] = Landing_Range[i][2*j]/scalefacter+lanchpoint[0]
    #     Landing_Range[i][1+2*j] = -Landing_Range[i][1+2*j]/scalefacter+lanchpoint[1]


  def judge(self,Landing_Range,securityRange):
    flag = [True]*8
    for i in range(56):
      if(flag[i%8] is not True ): continue
      if(securityRange[int(Landing_Range[i][0])][int(Landing_Range[i][1])] == 'False'): 
        flag[i%8] = i 

    for i in range(8):
      if(flag[i] == True): flag[i] = 56
      self.windLimit_label[i].setText(str(flag[i]//8))
      self.radarchart.limitWind[i] = int(flag[i]//8) 
  
  
class radarChart(QWidget):
  def __init__(self):
    super().__init__()
    self.limitWind = [0,0,0,0,0,0,0,0]

  def paintEvent(self, e):
    painter = QPainter()
    painter.begin(self)
    pen = QPen()
    pen.setColor(Qt.red)
    pen.setWidth(2)
    painter.setPen(pen)

    painter.translate(self.width() / 2, self.height() / 2)

    x0 = self.width() / 2
    y0 = self.height() / 2

    point_zero = QPoint(0, 0)

    radius = 12
    N = 8

    qpoints = [QPointF(self.limitWind[i]*radius * np.cos(2. * np.pi / N * i), self.limitWind[i]*-1. * radius * np.sin(2. * np.pi / N * i)) for i in range(0, N)]
    poly = QPolygonF(qpoints)
    painter.drawPolygon(poly)

    pen.setColor(Qt.black)
    pen.setWidth(0.5)
    painter.setPen(pen)
    for i in range(1,8):
      N = 8
      qpoints = [QPointF(i*radius * np.sin(2. * np.pi / N * j), i*-1. * radius * np.cos(2. * np.pi / N * j)) for j in range(0, N)]

      poly = QPolygonF(qpoints)
      painter.drawPolygon(poly)
      for i, v in enumerate(qpoints):
        painter.drawLine(point_zero, v)

    