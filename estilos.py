from string import Template


COLORES = {
    "fondo": "#f4f5f7",
    "superficie": "#ffffff",
    "borde": "#d8dce3",
    "borde_fuerte": "#9aa3af",
    "texto": "#1f2933",
    "texto_suave": "#6b7280",
    "primario": "#2563eb",
    "primario_hover": "#1d4ed8",
    "primario_presionado": "#1e40af",
    "resalte": "#eef4ff",
    "deshabilitado": "#c7ccd4",
}

COLORES_TIPO = {
    "archivo": "#2563eb",
    "folder": "#d97706",
    "forum": "#059669",
    "quiz": "#7c3aed",
    "discusion": "#0891b2",
}


BASE = Template("""
QWidget {
    background-color: $fondo;
    color: $texto;
    font-size: 10pt;
}

QLabel#estado {
    color: $texto_suave;
}

QLineEdit, QComboBox {
    background-color: $superficie;
    border: 1px solid $borde;
    border-radius: 6px;
    padding: 6px 8px;
}

QLineEdit:focus, QComboBox:focus {
    border-color: $primario;
}

QComboBox QAbstractItemView {
    background-color: $superficie;
    selection-background-color: $resalte;
    selection-color: $texto;
}

QTabWidget::pane {
    background-color: $superficie;
    border: 1px solid $borde;
    border-radius: 6px;
    top: -1px;
}

QTabBar::tab {
    background-color: $fondo;
    border: 1px solid $borde;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 6px 12px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: $superficie;
    color: $primario;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: $resalte;
}

QScrollArea {
    border: none;
    background-color: transparent;
}

QLabel#contenido {
    background-color: $superficie;
    border: 1px solid $borde;
    border-radius: 6px;
    padding: 10px;
}

QCheckBox {
    background-color: transparent;
    spacing: 6px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    background-color: $superficie;
    border: 1px solid $borde_fuerte;
    border-radius: 4px;
}

QCheckBox::indicator:hover {
    border-color: $primario;
}

QCheckBox::indicator:checked {
    background-color: $primario;
    border-color: $primario;
}

QCheckBox::indicator:disabled {
    background-color: $fondo;
    border-color: $borde;
}

/* Botones principales (Iniciar sesión, Descargar seleccionados) */
QPushButton {
    background-color: $primario;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 7px 14px;
}

QPushButton:hover {
    background-color: $primario_hover;
}

QPushButton:pressed {
    background-color: $primario_presionado;
}

QPushButton:disabled {
    background-color: $deshabilitado;
    color: $superficie;
}

/* Botón con el nombre de cada elemento */
QPushButton#elemento {
    background-color: $superficie;
    color: $texto;
    text-align: left;
    padding: 8px 12px;
    border: 1px solid $borde;
    border-radius: 6px;
}

QPushButton#elemento:hover {
    background-color: $resalte;
    border-color: $primario;
}

/* Flecha para expandir carpetas, foros y discusiones */
QPushButton#toggle {
    background-color: transparent;
    color: $texto_suave;
    min-width: 26px;
    max-width: 26px;
    padding: 7px 0;
}

QPushButton#toggle:hover {
    background-color: $resalte;
    color: $primario;
}

/* Botón de descarga de cada elemento */
QPushButton#descarga {
    background-color: $superficie;
    color: $primario;
    border: 1px solid $primario;
    min-width: 80px;
    padding: 7px 12px;
}

QPushButton#descarga:hover {
    background-color: $primario;
    color: white;
}

QPushButton#descarga:disabled {
    background-color: $fondo;
    color: $deshabilitado;
    border-color: $borde;
}
""")


def EstiloTipos():
    reglas = ""
    for tipo, color in COLORES_TIPO.items():
        reglas += f'QPushButton#elemento[tipo="{tipo}"] {{ border-left: 4px solid {color}; }}\n'
    return reglas


# Se aplica una sola vez con app.setStyleSheet(ESTILOS)
ESTILOS = BASE.substitute(COLORES) + EstiloTipos()
