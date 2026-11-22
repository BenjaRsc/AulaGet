from aula import AulaGet
import sys
from PySide6 import QtCore, QtWidgets, QtGui

aula = AulaGet()


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('AulaGet')

        layout = QtWidgets.QVBoxLayout()
        labelBottom = QtWidgets.QLabel("Footer")

        sesion = SesionMoodle()
        layout.addWidget(sesion)

        layout.addWidget(labelBottom)


        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)



class SesionMoodle(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.titulo = QtWidgets.QLabel("Moodle Session")
        self.sesion = QtWidgets.QLineEdit()

        self.button = QtWidgets.QPushButton("Iniciar Sesión")
        self.cursos = Cursos()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layoutH = QtWidgets.QHBoxLayout()

        self.layoutH.setContentsMargins(10, 10, 10, 10)
        self.layoutH.addWidget(self.titulo)
        self.layoutH.addWidget(self.sesion)
        self.layoutH.addWidget(self.button)

        self.layout.addLayout(self.layoutH)
        self.layout.addWidget(self.cursos)

        self.button.clicked.connect(self.Iniciar)


    def Iniciar(self):
        aula.IniciarMoodle(self.sesion.text())
        aula.GetCursos()

        if(aula.cursos):
            self.cursos.Mostrar()



class Cursos(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("Cursos")
        self.layout.addWidget(label)

    def Mostrar(self):
        self.index = 0
        self.combo = QtWidgets.QComboBox()
        for i, (nombre, link) in enumerate(aula.cursos.items()):
            self.combo.addItem(nombre)

        self.layout.addWidget(self.combo)
        self.combo.currentTextChanged.connect(self.MostrarValor)
        print(f'Nombre principio: {self.combo.currentText()}')

    def MostrarValor(self, value):
        print(value)


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    window = Window()
    window.resize(800, 800)
    window.show()


    sys.exit(app.exec())
