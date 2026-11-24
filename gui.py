from aula import AulaGet
import sys
import threading
from PySide6 import QtCore, QtWidgets, QtGui
import webbrowser

aula = AulaGet()
candado = threading.Lock()
pool = QtCore.QThreadPool.globalInstance()


class WorkerSignals(QtCore.QObject):
    resultado = QtCore.Signal(object)
    error = QtCore.Signal(str)


class Worker(QtCore.QRunnable):
    def __init__(self, funcion, *args):
        super().__init__()
        self.funcion = funcion
        self.args = args
        self.signals = WorkerSignals()

    @QtCore.Slot()
    def run(self):
        try:
            resultado = self.funcion(*self.args)
        except Exception as e:
            self.signals.error.emit(str(e))
        else:
            self.signals.resultado.emit(resultado)


def EjecutarWorker(funcion, *args, resultado, error):
    worker = Worker(funcion, *args)
    worker.signals.resultado.connect(resultado)
    worker.signals.error.connect(error)
    pool.start(worker)


def MostrarError(mensaje):
    QtWidgets.QMessageBox.critical(None, "Error", mensaje)


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
        self.button.setEnabled(False)
        EjecutarWorker(self.ObtenerCursos, self.sesion.text(),
                       resultado=self.CursosListos, error=self.Error)

    def ObtenerCursos(self, sesion):
        aula.IniciarMoodle(sesion)
        aula.GetCursos()
        return aula.cursos

    def CursosListos(self, cursos):
        self.button.setEnabled(True)

        if(cursos):
            self.cursos.Mostrar()

    def Error(self, mensaje):
        self.button.setEnabled(True)
        MostrarError(mensaje)



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

        self.tabs.currentChanged.connect(self.CargarElementos)
        self.combo.currentTextChanged.connect(self.MostrarSecciones)

        self.MostrarSecciones(self.combo.currentText())


    def ObtenerSecciones(self, curso):
        with candado:
            aula.GetSecciones(aula.cursos[curso])
            return curso, dict(aula.secciones)

    def MostrarSecciones(self, curso):
        self.tabs.clear()
        EjecutarWorker(self.ObtenerSecciones, curso,
                       resultado=self.AgregarSecciones, error=MostrarError)

    def AgregarSecciones(self, datos):
        curso, secciones = datos

        if (curso != self.combo.currentText()):
            return

        self.tabs.clear()
        for seccion in secciones:
            self.tabs.addTab(Seccion(secciones[seccion]), seccion)

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
        self.cargando = False

    def MostrarElementos(self):
        if (self.elementos == None and not self.cargando):
            self.cargando = True
            EjecutarWorker(aula.GetElementos, self.link,
                           resultado=self.AgregarElementos, error=self.Error)

    def AgregarElementos(self, elementos):
        self.elementos = elementos
        self.cargando = False

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

    def Error(self, mensaje):
        self.cargando = False
        MostrarError(mensaje)

    def Abrir(self, link):
        webbrowser.open(link)

if __name__ == "__main__":
    app = QtWidgets.QApplication()

    window = Window()
    window.resize(800, 800)
    window.show()

    sys.exit(app.exec())
