from aula import AulaGet
import sys
from PySide6 import QtCore, QtWidgets, QtGui
import webbrowser

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
        self.tabs = QtWidgets.QTabWidget()


    def Mostrar(self):
        self.index = 0
        self.combo = QtWidgets.QComboBox()
        for i, (nombre, link) in enumerate(aula.cursos.items()):
            self.combo.addItem(nombre)

        self.layout.addWidget(self.combo)
        self.layout.addWidget(self.tabs)

        aula.GetSecciones(aula.cursos[self.combo.currentText()])
        for seccion in aula.secciones:
            self.tabs.addTab(Seccion(aula.secciones[seccion]), seccion)

        self.tabs.currentChanged.connect(self.CargarElementos)
        self.combo.currentTextChanged.connect(self.MostrarSecciones)

        self.CargarElementos()


    def MostrarSecciones(self, curso):
        self.tabs.clear()
        aula.GetSecciones(aula.cursos[curso])
        for seccion in aula.secciones:
            self.tabs.addTab(Seccion(aula.secciones[seccion]), seccion)
    
        self.CargarElementos()

    def CargarElementos(self):
        if (self.tabs.currentWidget() != None):
            self.tabs.currentWidget().MostrarElementos()


class Seccion(QtWidgets.QWidget):
    def __init__(self, link):
        super().__init__()
        self.link = link
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(2)                   
        self.layout.setContentsMargins(4, 4, 4, 4) 
        self.elementos = None

    def MostrarElementos(self):
        if (self.elementos == None):
            self.elementos = aula.GetElementos(self.link)
            for elemento in self.elementos:
                layoutH = QtWidgets.QHBoxLayout()

                check = QtWidgets.QCheckBox("")
                boton = QtWidgets.QPushButton(elemento)
                boton.setStyleSheet("text-align: left; padding: 6px 10px;")

                l = self.elementos[elemento]['link']
                boton.clicked.connect(lambda checked=False, link=l: self.Abrir(link))

                layoutH.addWidget(check)
                layoutH.addWidget(boton)
                layoutH.addStretch()

                self.layout.addLayout(layoutH)

            self.layout.addStretch()

    def Abrir(self, link):
        webbrowser.open(link)

if __name__ == "__main__":
    app = QtWidgets.QApplication()

    window = Window()
    window.resize(800, 800)
    window.show()


    sys.exit(app.exec())
