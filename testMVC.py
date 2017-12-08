# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget,QApplication,QPushButton,QLabel
import sys

class View(QWidget): 
  def __init__(self, model):
    super().__init__()

    self.model = model

  def register(self,controller):
    self.controller = controller
    # controller生成後にinitUIしないとcontrollerのメソッドにバインドできない
    # これであってるかは不明...
    self.initUI() 
  
  def initUI(self):
    self.setGeometry(200,200,150,100)
    button = QPushButton('sayHello!!',self)
    button.clicked.connect(self.controller.pushButton)
    self.label = QLabel("none",self)
    self.label.setGeometry(20,50,50,20)

  def updateUI(self):
    self.label.setText(model.word)

class Model(object): # 何も継承しないときは'object'を継承することが推奨されている
  def __init__(self):
    self.word = 'none'
  
  def sayHello(self):
    # Modelは自身のデータを処理するだけ
    self.word = 'Hello'

class Controller(object):
  def __init__(self, view, model):
    self.view = view
    self.model = model

    self.view.register(self)
  
  def pushButton(self):
    # 複数の処理を行いたい際などに直接Modelに渡すのでなくControllerを挟むということが活きてくる
    self.model.sayHello()
    self.view.updateUI()


if __name__ == '__main__':
  app = QApplication(sys.argv)

  model = Model()
  view = View(model)
  controller = Controller(view,model)

  view.show()
  sys.exit(app.exec_())
  