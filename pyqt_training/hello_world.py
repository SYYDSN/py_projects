# -*- coding: utf-8 -*-
import sys
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import qApp
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication


class Example(QWidget):
    def __init__(self):
        super(Example, self).__init__()
        self.__init_ui()

    def __init_ui(self):
        QToolTip.setFont(QFont("SansSerif", 14))
        self.setToolTip("This is a <b>Qwidget</b> widget")
        btn = QPushButton("Button", self)
        btn.setToolTip("this is a <b>QPushButton</b> widget")
        btn.resize(btn.sizeHint())
        btn.move(50, 50)
        close_btn = QPushButton("关闭", self)
        close_btn.clicked.connect(QCoreApplication.instance().quit)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle("Tooltips")
        self.show()
        time.sleep(1)
        self.center()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Message", "你好!", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.statusBar().showMessage("就绪")
        self.setGeometry(300, 300, 250, 250)
        self.setWindowTitle("状态栏")
        exit_act = QAction("Exit", parent=self)
        exit_act.setShortcut("Ctrl+Q")
        exit_act.setStatusTip("Exit Application")
        exit_act.triggered.connect(qApp.quit)
        self.statusBar()

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(exit_act)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    example = MyWindow()
    sys.exit(app.exec_())