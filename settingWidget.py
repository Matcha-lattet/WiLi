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

class settingWidget(QWidget):
  def __init__(self, parent=None):
    super(settingWidget, self).__init__()

    file_label = QLabel("設定ファイル")
    file_combo = QComboBox(self)
    file_combo.addItem("A")

    file_Hbox = QHBoxLayout()
    file_Hbox.addWidget(file_label)
    file_Hbox.addWidget(file_combo)

    new_button = QPushButton("New")
    save_button = QPushButton("Save")
  
    map_label = QLabel("射点写真")
    map_open = QPushButton("Open")
    map_name = QLineEdit()
    map_box = QHBoxLayout()
    map_box.addWidget(map_label)
    map_box.addWidget(map_open)
    map_box.addWidget(map_name)

    angle_calibration_box = QHBoxLayout()
    angle_calibration_label =  QLabel("磁気偏角")
    angle_calibration = QLineEdit()
    angle_calibration_tani = QLabel('°')
    # angle_calibration_box.addWidget(angle_calibration_label)
    # angle_calibration_box.addWidget(angle_calibration)
    # angle_calibration_box.addWidget(angle_calibration_tani)

    lanchpoint_label = QLabel("射点")
    lanchpoint_button = QPushButton("選択")
    lanchpoint_button.setCheckable(True)
    lanchpoint_button.toggled.connect(self.setting_button_toggled)
    lanchpoint_x_label = QLabel("X:")
    self.lanchpoint_x = QLineEdit()
    lanchpoint_y_label = QLabel("Y:")
    self.lanchpoint_y = QLineEdit()
    lanchpoint_Hbox = QHBoxLayout()
    lanchpoint_Hbox.addWidget(lanchpoint_label)
    lanchpoint_Hbox.addWidget(lanchpoint_button)
    lanchpoint_Hbox.addWidget(lanchpoint_x_label)
    lanchpoint_Hbox.addWidget(self.lanchpoint_x)
    lanchpoint_Hbox.addWidget(lanchpoint_y_label)
    lanchpoint_Hbox.addWidget(self.lanchpoint_y)

    securityRangeGroup = QGroupBox("落下可能範囲")
    writer_button = QPushButton("選択")
    writer_button.setCheckable(True)
    delete_button = QPushButton("削除") 
    starting_point_label = QLabel("内部領域点")
    starting_point_button = QPushButton("選択")
    starting_point_button.setCheckable(True)
    starting_point_x_Label = QLabel("X:")
    self.starting_point_x = QLineEdit()
    starting_point_y_label = QLabel("Y:")
    self.starting_point_y = QLineEdit()
    calculation_button = QPushButton("Calculation")
    calculation_button.clicked.connect(self.calculation)
    securityRange_Hbox = QHBoxLayout()
    securityRange_Hbox.addWidget(writer_button)
    securityRange_Hbox.addWidget(delete_button)
    starting_point = QHBoxLayout()
    starting_point.addWidget(starting_point_label)
    starting_point.addWidget(starting_point_button)
    starting_point.addWidget(starting_point_x_Label)
    starting_point.addWidget(self.starting_point_x)
    starting_point.addWidget(starting_point_y_label)
    starting_point.addWidget(self.starting_point_y)
    securityRange_Vbox = QVBoxLayout()
    securityRange_Vbox.addLayout(starting_point)
    securityRange_Vbox.addLayout(securityRange_Hbox)
    securityRange_Vbox.addWidget(calculation_button)
    securityRangeGroup.setLayout(securityRange_Vbox)


    Vbox = QVBoxLayout()
    Vbox.addLayout(file_Hbox)
    Vbox.addWidget(new_button)
    Vbox.addWidget(save_button)
    Vbox.addLayout(map_box)
    Vbox.addLayout(angle_calibration_box)
    Vbox.addLayout(lanchpoint_Hbox)
    Vbox.addWidget(securityRangeGroup)

    self.setting_group = QButtonGroup()
    self.setting_group.addButton(lanchpoint_button)
    self.setting_group.addButton(writer_button)
    self.setting_group.addButton(starting_point_button)

    self.setLayout(Vbox)

  def setting_button_toggled(self, checked):
    print('toggled')

  def calculation(self):
    self.list = [[]]
    file = open(os.path.dirname(os.path.abspath(sys.argv[0]))+'/taiki.dat','r')
    for point in file:
      point = point.rstrip("\n").split(' ')
      self.list[0].append(QPoint(int(point[0]),int(point[1])))
    file.close()

    Flag = True
    okline = 0
    while(Flag == True):
      print("clear")
      
      for i in range(okline,len(self.list)-1):
        okline = i
        if(float(self.list[i+1][0])-float(self.list[i][0]) > 1):
          self.list.insert(i+1,[self.list[i][0]+1,self.list[i][1]])
          break
        if(float(self.list[i+1][0])-float(self.list[i][0]) < -1):
          self.list.insert(i+1,[self.list[i][0]-1,self.list[i][1]])
          break
        if(float(self.list[i+1][1])-float(self.list[i][1]) > 1):
          self.list.insert(i+1,[self.list[i][0],self.list[i][1]+1])
          break
        if(float(self.list[i+1][1])-float(self.list[i][1]) < -1):
          self.list.insert(i+1,[self.list[i][0],self.list[i][1]-1])
          break
        if(i == len(self.list)-2):
          Flag = False

    for point in self.list:
      self.securityLine[int(point[0])][int(point[1])] = True
      self.securityRange[int(point[0])][int(point[1])] = True
      self.psets.append(QPoint(int(point[0]),int(point[1])))
    

    #Scan Line Method
    self.buffer.append(self.startingPoint)
    
    while(len(self.buffer)):
      self.point = self.buffer[0]
      # print(self.point)
      del self.buffer[0]
      
      if(self.securityRange[self.point[0]][self.point[1]] == True): continue
      # print(self.point[1],self.securityRange[self.point[0]][self.point[1]])
      
      self.leftX = self.point[0]
      while(0<=self.leftX):
        if(self.securityLine[self.leftX-1][self.point[1]]==True): break
        self.leftX -= 1

      self.rightX = self.point[0]
      while(self.rightX<=560):
        if(self.securityLine[self.rightX+1][self.point[1]]==True): break
        self.rightX += 1

      for i in range(self.leftX,self.rightX+1):
        self.securityRange[i][self.point[1]] = True
      # print(self.securityRange[self.leftX][self.point[1]],self.securityRange[self.rightX][self.point[1]])
      # print(self.point[1],self.leftX,self.rightX,self.securityRange[self.leftX+1][self.point[1]])
      if(self.point[1]+1 <= 560): self.scanLine(self.point[1]+1,self.leftX,self.rightX)
      if(0 <= self.point[1]-1): self.scanLine(self.point[1]-1,self.leftX,self.rightX)

      self.outputfilldata()

  def outputfilldata(self):
    with open(os.path.dirname(os.path.abspath(sys.argv[0]))+'/securityRange.csv', 'w') as file:
      writer = csv.writer(file, lineterminator='\n') # 改行コード（\n）を指定しておく
      writer.writerows(self.securityRange) # 2次元配列も書き込める
    
  def scanLine(self,y,leftX,rightX):
    while(leftX <= rightX):

      while(leftX <= rightX):
        if(self.securityRange[leftX][y] == False): break
        leftX += 1

      if(rightX < leftX): break

      while(leftX <= rightX):
        if(self.securityRange[leftX][y] == True): break
        leftX += 1

      self.buffer.append([leftX-1,y])
      # print(leftX-1,y)
      if(leftX%10 == 0): print(self.buffer)
      # print(y,self.securityRange[leftX-1][y])