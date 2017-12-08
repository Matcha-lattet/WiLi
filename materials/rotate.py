# -*- coding:utf-8 -*-

from PIL import Image

img = Image.open('./pic/TaikiLand.png','r')

# 45°回転
tmp = img.rotate(-8.203)
tmp.save('TaikiLand8deg.png')


    # painter = QPainter(self)
    # # tf = QTransform()
    # # tf.translate(self.width() / 2, self.height() / 2)
    # # tf.rotate(8.203)
    # # painter.setTransform(tf)
    # pen = QPen()

    # # tf.translate(-self.image.width() / 2, -self.image.height() / 2)
    # # painter.setTransform(tf)
    # painter.drawImage(0, 0,self.image)
    # # tf.translate(self.width() / 2, self.height() / 2)
    
    # # tf.rotate(8.203)
    # # painter.setTransform(tf)