from bs4 import BeautifulSoup
import requests


class AulaGet():
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent":"Mozilla/5.0"})

        self.cursos = {}
        self.secciones = {} 
        self.elementos = {}

    def IniciarMoodle(self, moodle_session):
        self.session.cookies.set("MoodleSession", moodle_session, domain="aula.usm.cl")

    def GetCursos(self):
        url = "https://aula.usm.cl"
        html = self.session.get(url)
        soup = BeautifulSoup(html.text, "lxml")

        cursos = soup.find_all(class_='aalink coursename mr-2 mb-1')
        cur = {}

        for curso in cursos:
            nombre_curso = curso.text.strip()
            link_curso = curso['href'].strip()
            cur[nombre_curso] = link_curso

        self.cursos = cur

    def GetSecciones(self, url):
        html = self.session.get(url)
        soup = BeautifulSoup(html.text, "lxml")

        secc = {}

        secciones = soup.find_all('a', class_='nav-link')
        secciones = secciones[12:-2]

        for seccion in secciones:
            if('disabled' not in seccion['class']):
                seccion_nombre = seccion.get('title')
                if (seccion_nombre != None):
                    seccion_link = seccion['href']
                    secc[seccion_nombre] = seccion_link

        self.secciones = secc


    def LinkPdf(self, url):
        r = self.session.head(url + "&redirect=1", allow_redirects=True, timeout=15)
        return r.url

    def GetElementos(self, url):
        html = self.session.get(url, timeout=15)
        soup = BeautifulSoup(html.text, "lxml")

        elem = {}
        elementos = soup.find_all(class_='aalink stretched-link')

        for elemento in elementos:
            nombre_elemento = elemento.text.strip()
            link_elemento = elemento['href']
            tipo_elemento = self.GetTipo(link_elemento)

            if (tipo_elemento == 'archivo'):
                link_elemento = self.LinkPdf(link_elemento)

            elem[nombre_elemento] = {'tipo': tipo_elemento, 'link': link_elemento}

        return elem

    def GetTipo(link):
        if ('forum' in link):
            return 'forum'

        elif ('folder' in link):
            return 'folder'

        elif ('quiz' in link):
            return 'quiz'

        return 'archivo'

    def GetForo(self, url):
        html = self.session.get(url)
        soup = BeautifulSoup(html.text, "lxml")

        foro = {}

        discusiones = soup.find_all(class_='w-100 h-100 d-block')

        for discusion in discusiones:
            nombre_discusion = discusion['title'].strip()
            link_discusion = discusion['href'].strip()
            foro[nombre_discusion] = link_discusion

        return foro


    def GetDiscusion(self, url):
        html = self.session.get(url)
        soup = BeautifulSoup(html.text, "lxml")

        dis = {}
        
        contenido = soup.find(class_='post-content-container')
        contenido_texto = contenido.text.strip()

        dis['contenido'] = str(contenido_texto)
        dis['archivos'] = {}

        docs = soup.find(class_='no-overflow w-100 content-alignment-container')
        documentos = docs.find_all('a', class_=None)
        #print(documentos)
        for documento in documentos:
            documento_nombre = documento['aria-label'].strip()
            documento_link = documento['href'].strip()
            dis['archivos'][documento_nombre] = documento_link

        return dis

    def GetCarpetaContenidos(self, url):
        html = self.session.get(url)
        soup = BeautifulSoup(html.text, "lxml")
        archivos = soup.find_all(class_='fp-filename')
        contenidos = {}

        for archivo in archivos[1:]:
            nombre_archivo = archivo.text.strip()
            l = archivo.find('a')
            link_archivo = l['href'].strip()
            contenidos[nombre_archivo] = link_archivo

        return contenidos





# Ejemplo de uso
aula = AulaGet()
moodle_session = ""
aula.IniciarMoodle(moodle_session)

aula.GetCursos()
# print(aula.cursos)


# Cursos
for curso in aula.cursos:
    link = aula.cursos[curso]
    print(curso)
    print(link)

    print("Secciones")
    aula.GetSecciones(link)

    # Secciones
    for seccion in aula.secciones:
        link_seccion = aula.secciones[seccion]
        print(f'{seccion}: {link_seccion}')
        print()



    print()
    print()
