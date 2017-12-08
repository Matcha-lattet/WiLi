# -*- coding: utf-8 -*-

# from Widget import *
from MapView import *
from resultWidget import *
from settingWidget import *


class Main(QWidget):
  def __init__(self):
    QWidget.__init__(self)

    self.setMinimumSize(1000, 600)
    self.setMaximumSize(1000, 600)
    self.setWindowTitle('Taiyaki_kun')

    self.Landing_Range = [[1] * 4 for i in range(56)]
    self.securityRange = [[False] * 801 for i in range(801)]

    self.lanchpoint = [160,375]
    self.scalefacter = 200.0 / 53.0

    self.resultwidget = resultWidget(self)
    self.settingwidget = settingWidget(self)

    qtab = QTabWidget()
    qtab.addTab(self.resultwidget, 'Result')
    qtab.addTab(self.settingwidget, 'Setting')
    mapView = MapView(self.securityRange)

    H_layout = QHBoxLayout()
    H_layout.addWidget(mapView)
    H_layout.addWidget(qtab)

    self.setLayout(H_layout)

    self.resultwidget.open_button.clicked.connect(lambda: self.resultwidget.load_data(self.Landing_Range,self.scalefacter,self.lanchpoint))
    self.resultwidget.open_button.clicked.connect(lambda: mapView.drawLandingRange(self.Landing_Range,self.scalefacter,self.lanchpoint))
    self.resultwidget.judge_button.clicked.connect(lambda: self.resultwidget.judge(self.Landing_Range,self.securityRange))


if __name__ == '__main__':
  app = QApplication(sys.argv)
  w = Main()
  w.show()
  sys.exit(app.exec_())