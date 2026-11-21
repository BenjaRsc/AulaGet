from aula import AulaGet
import sys
from PySide6 import QtCore, QtWidgets, QtGui

aula = AulaGet()

class SesionMoodle(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.titulo = QtWidgets.QLabel("Moodle Session")
        self.sesion = QtWidgets.QLineEdit()

        self.button = QtWidgets.QPushButton("Iniciar Sesión")

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.addWidget(self.titulo)
        self.layout.addWidget(self.sesion)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.Iniciar)

    def Iniciar(self):
        aula.IniciarMoodle(self.sesion.text())
        aula.GetCursos()
        print(aula.cursos)

if __name__ == "__main__":
    app = QtWidgets.QApplication()

    widget_sesion = SesionMoodle()
    widget_sesion.resize(800, 600)
    widget_sesion.show()

    sys.exit(app.exec())
