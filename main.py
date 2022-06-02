# -*- coding: utf-8 -*-
# запуск приложения

import os
import sys

from PyQt5.QtWidgets import QApplication

import primary_window

app = QApplication(sys.argv)
ex = primary_window.MyWidget()
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
ex.show()
sys.exit(app.exec_())
