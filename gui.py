from aula import AulaGet
from estilos import ESTILOS
import sys
import os
import re
import shutil
import tempfile
import threading
import zipfile
import mimetypes
from email.message import Message
from urllib.parse import urlparse, unquote
from PySide6 import QtCore, QtWidgets, QtGui
import webbrowser

aula = AulaGet()
candado = threading.Lock()
pool = QtCore.QThreadPool.globalInstance()
ajustes = {"destino": os.path.expanduser("~")}


class WorkerSignals(QtCore.QObject):
    resultado = QtCore.Signal(object)
    error = QtCore.Signal(str)
    progreso = QtCore.Signal(str)


class Worker(QtCore.QRunnable):
    def __init__(self, funcion, *args, progreso=False):
        super().__init__()
        self.funcion = funcion
        self.args = args
        self.progreso = progreso
        self.signals = WorkerSignals()

    @QtCore.Slot()
    def run(self):
        try:
            if (self.progreso):
                resultado = self.funcion(*self.args, self.signals.progreso.emit)
            else:
                resultado = self.funcion(*self.args)
        except Exception as e:
            self.signals.error.emit(str(e))
        else:
            self.signals.resultado.emit(resultado)


def EjecutarWorker(funcion, *args, resultado, error, progreso=None):
    worker = Worker(funcion, *args, progreso=progreso != None)
    worker.signals.resultado.connect(resultado)
    worker.signals.error.connect(error)

    if (progreso != None):
        worker.signals.progreso.connect(progreso)

    pool.start(worker)


def MostrarError(mensaje):
    QtWidgets.QMessageBox.critical(None, "Error", mensaje)


def NombreSeguro(nombre):
    nombre = re.sub(r'[\\/:*?"<>|\r\n\t]', '_', nombre).strip(' .')
    return nombre if nombre else 'archivo'


def NombreLibre(carpeta, nombre):
    base, ext = os.path.splitext(nombre)
    ruta = os.path.join(carpeta, nombre)
    i = 0

    while os.path.exists(ruta):
        i += 1
        ruta = os.path.join(carpeta, f"{base} ({i}){ext}")

    return ruta


class Descargador():
    def __init__(self, destino, comprimir, nombre_zip):
        self.destino = destino
        self.comprimir = comprimir
        self.nombre_zip = NombreSeguro(nombre_zip) + '.zip'

        self.zip = None
        self.ruta_zip = None
        self.usados = set()
        self.descargados = []
        self.errores = []

    def Descargar(self, items, reportar):
        reportar("Preparando descarga...")
        archivos = []

        # Las carpetas se expanden a los archivos que contienen
        for nombre, tipo, link in items:
            try:
                if (tipo == 'folder'):
                    carpeta = NombreSeguro(nombre)
                    contenidos = aula.GetCarpetaContenidos(link)
                    for nombre_archivo, link_archivo in contenidos.items():
                        archivos.append((carpeta, nombre_archivo, link_archivo))
                else:
                    archivos.append(('', nombre, link))
            except Exception as e:
                self.errores.append(f"{nombre}: {e}")

        if (self.comprimir and archivos):
            self.ruta_zip = NombreLibre(self.destino, self.nombre_zip)
            self.zip = zipfile.ZipFile(self.ruta_zip, 'w', zipfile.ZIP_DEFLATED)

        try:
            for i, (carpeta, nombre, link) in enumerate(archivos, 1):
                reportar(f"Descargando {i}/{len(archivos)}: {nombre}")
                try:
                    self.DescargarArchivo(carpeta, nombre, link)
                except Exception as e:
                    self.errores.append(f"{nombre}: {e}")
        finally:
            if (self.zip != None):
                self.zip.close()

        # No dejar un zip vacío si todas las descargas fallaron
        if (self.ruta_zip != None and not self.descargados):
            os.remove(self.ruta_zip)
            self.ruta_zip = None

        return {
            'descargados': self.descargados,
            'errores': self.errores,
            'ruta': self.ruta_zip if self.ruta_zip != None else self.destino
        }

    def ResolverLink(self, link):
        # Los enlaces de carpetas ya son directos, el resto se valida con LinkPdf
        if ('pluginfile.php' in link):
            return link

        return aula.LinkPdf(link)

    def DescargarArchivo(self, carpeta, nombre, link):
        url = self.ResolverLink(link)

        with aula.session.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            tipo = r.headers.get('Content-Type', '')

            # Si Moodle devuelve una página en vez de un archivo, no es descargable
            if ('text/html' in tipo):
                raise Exception("el enlace no apunta a un archivo descargable")

            nombre_archivo = self.NombreArchivo(r, nombre, tipo)

            with tempfile.TemporaryFile() as temporal:
                for chunk in r.iter_content(65536):
                    temporal.write(chunk)
                temporal.seek(0)

                if (self.comprimir):
                    ruta = self.NombreEnZip(carpeta, nombre_archivo)
                    with self.zip.open(ruta, 'w') as destino:
                        shutil.copyfileobj(temporal, destino)
                else:
                    carpeta_destino = os.path.join(self.destino, carpeta)
                    os.makedirs(carpeta_destino, exist_ok=True)
                    ruta = NombreLibre(carpeta_destino, nombre_archivo)
                    with open(ruta, 'wb') as destino:
                        shutil.copyfileobj(temporal, destino)

        self.descargados.append(ruta)

    def NombreArchivo(self, respuesta, hint, tipo):
        msg = Message()
        msg['Content-Disposition'] = respuesta.headers.get('Content-Disposition', '')
        nombre = msg.get_filename()

        if (nombre):
            # requests decodifica los headers como latin-1
            try:
                nombre = nombre.encode('latin-1').decode('utf-8')
            except (UnicodeEncodeError, UnicodeDecodeError):
                pass
        else:
            nombre = os.path.basename(unquote(urlparse(respuesta.url).path))

        if (not nombre):
            nombre = hint

        if (not os.path.splitext(nombre)[1]):
            nombre += mimetypes.guess_extension(tipo.split(';')[0].strip()) or ''

        return NombreSeguro(nombre)

    def NombreEnZip(self, carpeta, nombre):
        base, ext = os.path.splitext(nombre)
        i = 0

        while True:
            n = nombre if i == 0 else f"{base} ({i}){ext}"
            ruta = f"{carpeta}/{n}" if carpeta else n

            if (ruta not in self.usados):
                self.usados.add(ruta)
                return ruta

            i += 1


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('AulaGet')

        layout = QtWidgets.QVBoxLayout()
        labelBottom = QtWidgets.QLabel("Footer")
        labelBottom.setObjectName("footer")
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
        else:
            MostrarError("No se encontraron cursos. Revisa que la cookie MoodleSession sea válida.")

    def Error(self, mensaje):
        self.button.setEnabled(True)
        MostrarError(mensaje)



class Cursos(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.tabs = QtWidgets.QTabWidget()
        self.combo = QtWidgets.QComboBox()
        self.generacion = 0

        # Se crean una sola vez, Mostrar solo los actualiza
        self.layout.addWidget(self.combo)
        self.layout.addWidget(self.tabs)

        self.tabs.currentChanged.connect(self.CargarElementos)
        self.combo.currentTextChanged.connect(self.MostrarSecciones)

        self.hide()


    def Mostrar(self):
        self.index = 0

        self.combo.blockSignals(True)
        self.combo.clear()
        for i, (nombre, link) in enumerate(aula.cursos.items()):
            self.combo.addItem(nombre)
        self.combo.blockSignals(False)

        self.show()
        self.MostrarSecciones(self.combo.currentText())


    def ObtenerSecciones(self, curso, generacion):
        with candado:
            aula.GetSecciones(aula.cursos[curso])
            return generacion, dict(aula.secciones)

    def MostrarSecciones(self, curso):
        self.tabs.clear()

        # Cada petición lleva un número, solo se acepta la más reciente
        self.generacion += 1
        EjecutarWorker(self.ObtenerSecciones, curso, self.generacion,
                       resultado=self.AgregarSecciones, error=MostrarError)

    def AgregarSecciones(self, datos):
        generacion, secciones = datos

        if (generacion != self.generacion):
            return

        self.tabs.clear()
        for seccion in secciones:
            self.tabs.addTab(Seccion(secciones[seccion], seccion), seccion)

        self.CargarElementos()

    def CargarElementos(self):
        if (self.tabs.currentWidget() != None):
            self.tabs.currentWidget().MostrarElementos()


class Seccion(QtWidgets.QWidget):
    def __init__(self, link, nombre):
        super().__init__()
        self.link = link
        self.nombre = nombre
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(2)                   
        self.layout.setContentsMargins(4, 4, 4, 4) 
        self.elementos = None
        self.cargando = False
        self.descargando = False
        self.checks = {}
        self.botonesDescarga = []

        self.seleccionar = QtWidgets.QCheckBox("Seleccionar todo")
        self.comprimir = QtWidgets.QCheckBox("Comprimir en ZIP")
        self.descargar = QtWidgets.QPushButton("Descargar seleccionados")
        self.estado = QtWidgets.QLabel("")
        self.estado.setObjectName("estado")

        self.seleccionar.setEnabled(False)
        self.descargar.setEnabled(False)

        layoutH = QtWidgets.QHBoxLayout()
        layoutH.addWidget(self.seleccionar)
        layoutH.addStretch()
        layoutH.addWidget(self.comprimir)
        layoutH.addWidget(self.descargar)

        self.layout.addLayout(layoutH)
        self.layout.addWidget(self.estado)

        self.seleccionar.toggled.connect(self.SeleccionarTodo)
        self.descargar.clicked.connect(self.DescargarSeleccionados)

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

            tipo = self.elementos[elemento]['tipo']
            descargable = tipo in ('archivo', 'folder')

            check = QtWidgets.QCheckBox("")
            check.setEnabled(descargable)
            boton = QtWidgets.QPushButton(elemento)
            boton.setObjectName("elemento")
            boton.setProperty("tipo", tipo)

            botonDescarga = QtWidgets.QPushButton("Descargar")
            botonDescarga.setObjectName("descarga")
            botonDescarga.setEnabled(descargable)

            if (descargable):
                self.botonesDescarga.append(botonDescarga)
            else:
                botonDescarga.setToolTip("Este tipo de elemento no se puede descargar")

            l = self.elementos[elemento]['link']
            boton.clicked.connect(lambda checked=False, link=l: self.Abrir(link))
            botonDescarga.clicked.connect(lambda checked=False, e=elemento: self.Descargar([e]))

            self.checks[elemento] = check

            layoutH.addWidget(check)
            layoutH.addWidget(boton, 1)
            layoutH.addWidget(botonDescarga)

            self.layout.addLayout(layoutH)

        self.layout.addStretch()

        self.seleccionar.setEnabled(True)
        self.descargar.setEnabled(True)

    def SeleccionarTodo(self, marcado):
        for check in self.checks.values():
            if (check.isEnabled()):
                check.setChecked(marcado)

    def DescargarSeleccionados(self):
        nombres = [e for e, check in self.checks.items() if check.isChecked()]

        if (not nombres):
            self.estado.setText("Selecciona al menos un elemento para descargar")
            return

        self.Descargar(nombres)

    def Descargar(self, nombres):
        if (self.descargando):
            return

        destino = QtWidgets.QFileDialog.getExistingDirectory(self, "Carpeta de destino", ajustes["destino"])

        if (not destino):
            return

        ajustes["destino"] = destino

        items = [(n, self.elementos[n]['tipo'], self.elementos[n]['link']) for n in nombres]
        nombre_zip = nombres[0] if len(nombres) == 1 else self.nombre
        descargador = Descargador(destino, self.comprimir.isChecked(), nombre_zip)

        self.Bloquear(True)
        EjecutarWorker(descargador.Descargar, items,
                       resultado=self.DescargaTerminada, error=self.ErrorDescarga,
                       progreso=self.estado.setText)

    def Bloquear(self, bloqueado):
        self.descargando = bloqueado
        self.descargar.setEnabled(not bloqueado)

        for boton in self.botonesDescarga:
            boton.setEnabled(not bloqueado)

    def DescargaTerminada(self, resultado):
        self.Bloquear(False)
        self.estado.setText(f"{len(resultado['descargados'])} archivo(s) descargado(s) en {resultado['ruta']}")

        if (resultado['errores']):
            QtWidgets.QMessageBox.warning(self, "Descarga incompleta",
                "No se pudo descargar:\n\n" + "\n".join(resultado['errores']))

    def ErrorDescarga(self, mensaje):
        self.Bloquear(False)
        self.estado.setText("Error en la descarga")
        MostrarError(mensaje)

    def Error(self, mensaje):
        self.cargando = False
        MostrarError(mensaje)

    def Abrir(self, link):
        webbrowser.open(link)

if __name__ == "__main__":
    app = QtWidgets.QApplication()
    app.setStyleSheet(ESTILOS)

    window = Window()
    window.resize(800, 800)
    window.show()

    sys.exit(app.exec())
