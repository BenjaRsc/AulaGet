from string import Template


COLORES = {
    "fondo": "#faf9f6",
    "superficie": "#ffffff",
    "borde": "#e5e2d9",
    "texto": "#18181b",
    "texto_suave": "#64646b",
    "primario": "#d99b00",
    "primario_hover": "#b88200",
    "primario_presionado": "#966900",
    "resalte": "#fef7e0",
    "deshabilitado": "#e4e4e7",
}

COLORES_TIPO = {
    "archivo": "#d99b00",
    "folder": "#3f3f46",
    "forum": "#0d9488",
    "quiz": "#4f46e5",
}


BASE = Template("""
QWidget {
    background-color: $fondo;
    color: $texto;
    font-size: 13px;
}

QLabel#footer, QLabel#estado {
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
    color: $primario_presionado;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: $resalte;
}

QCheckBox {
    background-color: transparent;
    color: $texto;
    spacing: 6px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1.5px solid $texto_suave;
    border-radius: 4px;
    background-color: $superficie;
}

QCheckBox::indicator:hover {
    border-color: $primario_presionado;
    background-color: $resalte;
}

QCheckBox::indicator:checked {
    border-color: $primario_presionado;
    background-color: $primario;
}

QCheckBox::indicator:disabled {
    border-color: $borde;
    background-color: $deshabilitado;
}

QPushButton {
    background-color: $primario;
    color: $texto;
    font-weight: 600;
    border: none;
    border-radius: 6px;
    padding: 7px 14px;
}

QPushButton:hover {
    background-color: $primario_hover;
}

QPushButton:pressed {
    background-color: $primario_presionado;
    color: white;
}

QPushButton:disabled {
    background-color: $deshabilitado;
    color: $texto_suave;
}

QPushButton#elemento {
    background-color: $superficie;
    color: $texto;
    font-weight: normal;
    text-align: left;
    padding: 8px 12px;
    border: 1px solid $borde;
    border-radius: 6px;
}

QPushButton#elemento:hover {
    background-color: $resalte;
    border-color: $primario;
}

QPushButton#descarga {
    background-color: $superficie;
    color: $primario_presionado;
    font-weight: 600;
    border: 1px solid $primario;
    border-radius: 6px;
    min-width: 80px;
    padding: 7px 12px;
}

QPushButton#descarga:hover {
    background-color: $primario;
    color: $texto;
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


ESTILOS = BASE.substitute(COLORES) + EstiloTipos()
