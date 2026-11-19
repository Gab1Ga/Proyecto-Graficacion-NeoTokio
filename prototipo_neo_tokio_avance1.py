"""
Proyecto Final de Graficación - Primer Avance (Prototipo Inicial)
Tema: Neo-Tokio Cyberpunk 3D (Escena Urbana Nocturna Interactiva)
Tecnologías: Python 3 + Pygame + PyOpenGL (GLU / GLUT)

Controles del Prototipo Inicial:
- Flechas Izquierda / Derecha: Rotar cámara alrededor de la escena
- Flechas Arriba / Abajo: Elevar o bajar altura de la cámara
- Teclas W / S: Acercar o alejar zoom
- Tecla R: Reiniciar vista de cámara
- ESC: Salir
"""

import sys
import math
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


# Configuración de ventana
ANCHO_VENTANA = 1280
ALTO_VENTANA = 720
TITULO_VENTANA = "Primer Avance - Neo-Tokio Cyberpunk 3D | Graficación IT Celaya"


class CamaraOrbital:
    def __init__(self):
        self.angulo_y = 35.0
        self.angulo_x = 22.0
        self.distancia = 28.0

    def aplicar(self):
        glLoadIdentity()
        rad_y = math.radians(self.angulo_y)
        rad_x = math.radians(self.angulo_x)

        cam_x = self.distancia * math.cos(rad_x) * math.sin(rad_y)
        cam_y = max(1.5, self.distancia * math.sin(rad_x))
        cam_z = self.distancia * math.cos(rad_x) * math.cos(rad_y)

        gluLookAt(
            cam_x, cam_y, cam_z,  # Posición de la cámara
            0.0, 4.0, 0.0,        # Punto al que mira (centro de la calle)
            0.0, 1.0, 0.0         # Vector arriba
        )


def inicializar_opengl():
    glClearColor(0.03, 0.02, 0.08, 1.0)  # Cielo nocturno cyberpunk azul-violeta oscuro
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glShadeModel(GL_SMOOTH)

    # Niebla atmosférica base (se expandirá en el segundo avance)
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.04, 0.02, 0.10, 1.0))
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogf(GL_FOG_DENSITY, 0.018)

    # Iluminación base (direccional fría de luna + ambiental)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat * 4)(15.0, 25.0, 15.0, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (GLfloat * 4)(0.18, 0.15, 0.28, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (GLfloat * 4)(0.55, 0.65, 0.90, 1.0))


def configurar_proyeccion(ancho, alto):
    if alto == 0:
        alto = 1
    glViewport(0, 0, ancho, alto)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(ancho) / float(alto), 0.1, 150.0)
    glMatrixMode(GL_MODELVIEW)


def dibujar_prisma(ancho, alto, profundo, color_rgb):
    """Dibuja un prisma rectangular centrado en X y Z, apoyado en Y=0."""
    hx = ancho / 2.0
    hz = profundo / 2.0
    glColor3f(*color_rgb)

    glBegin(GL_QUADS)
    # Cara frontal (+Z)
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(-hx, 0.0, hz)
    glVertex3f(hx, 0.0, hz)
    glVertex3f(hx, alto, hz)
    glVertex3f(-hx, alto, hz)

    # Cara trasera (-Z)
    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(hx, 0.0, -hz)
    glVertex3f(-hx, 0.0, -hz)
    glVertex3f(-hx, alto, -hz)
    glVertex3f(hx, alto, -hz)

    # Cara izquierda (-X)
    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(-hx, 0.0, -hz)
    glVertex3f(-hx, 0.0, hz)
    glVertex3f(-hx, alto, hz)
    glVertex3f(-hx, alto, -hz)

    # Cara derecha (+X)
    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f(hx, 0.0, hz)
    glVertex3f(hx, 0.0, -hz)
    glVertex3f(hx, alto, -hz)
    glVertex3f(hx, alto, hz)

    # Techo (+Y)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-hx, alto, hz)
    glVertex3f(hx, alto, hz)
    glVertex3f(hx, alto, -hz)
    glVertex3f(-hx, alto, -hz)
    glEnd()


def dibujar_letrero_neon(ancho, alto, color_neon):
    """Dibuja un letrero luminoso emisivo tipo anuncio japonés vertical/horizontal."""
    glDisable(GL_LIGHTING)  # El neón brilla por sí mismo sin depender de sombra
    glColor3f(*color_neon)
    hx = ancho / 2.0
    hy = alto / 2.0

    glBegin(GL_QUADS)
    glVertex3f(-hx, -hy, 0.0)
    glVertex3f(hx, -hy, 0.0)
    glVertex3f(hx, hy, 0.0)
    glVertex3f(-hx, hy, 0.0)
    glEnd()

    # Marco exterior de contraste
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex3f(-hx, -hy, 0.02)
    glVertex3f(hx, -hy, 0.02)
    glVertex3f(hx, hy, 0.02)
    glVertex3f(-hx, hy, 0.02)
    glEnd()
    glEnable(GL_LIGHTING)


def dibujar_suelo_y_calle():
    """Dibuja la avenida principal, banquetas y líneas de carril."""
    # Asfalto principal
    glColor3f(0.08, 0.09, 0.13)
    glBegin(GL_QUADS)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(-30.0, 0.0, -30.0)
    glVertex3f(30.0, 0.0, -30.0)
    glVertex3f(30.0, 0.0, 30.0)
    glVertex3f(-30.0, 0.0, 30.0)
    glEnd()

    # Banquetas laterales elevadas
    glPushMatrix()
    glTranslatef(-8.5, 0.0, 0.0)
    dibujar_prisma(9.0, 0.25, 55.0, (0.14, 0.14, 0.20))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(8.5, 0.0, 0.0)
    dibujar_prisma(9.0, 0.25, 55.0, (0.14, 0.14, 0.20))
    glPopMatrix()

    # Líneas viales neón en la avenida central (primitivas GL_LINES / GL_QUADS)
    glDisable(GL_LIGHTING)
    glColor3f(0.0, 0.95, 1.0)  # Cian neón
    for z in range(-24, 25, 4):
        glBegin(GL_QUADS)
        glVertex3f(-0.12, 0.02, z - 1.0)
        glVertex3f(0.12, 0.02, z - 1.0)
        glVertex3f(0.12, 0.02, z + 1.0)
        glVertex3f(-0.12, 0.02, z + 1.0)
        glEnd()
    glEnable(GL_LIGHTING)


def dibujar_arco_torii_cyberpunk(x, y, z):
    """Estructura icónica japonesa reinterpretada con luces neón."""
    glPushMatrix()
    glTranslatef(x, y, z)

    # Columnas verticales
    glPushMatrix()
    glTranslatef(-3.2, 0.0, 0.0)
    dibujar_prisma(0.45, 5.2, 0.45, (0.15, 0.05, 0.08))
    glPopMatrix()

    glPushMatrix()
    glTranslatef(3.2, 0.0, 0.0)
    dibujar_prisma(0.45, 5.2, 0.45, (0.15, 0.05, 0.08))
    glPopMatrix()

    # Travesaño superior (Kasagi)
    glPushMatrix()
    glTranslatef(0.0, 4.9, 0.0)
    dibujar_prisma(8.2, 0.45, 0.65, (0.85, 0.10, 0.25))
    glPopMatrix()

    # Travesaño secundario (Nuki) con tubo neón magenta
    glPushMatrix()
    glTranslatef(0.0, 3.8, 0.0)
    dibujar_prisma(7.0, 0.30, 0.35, (0.20, 0.05, 0.12))
    glTranslatef(0.0, 0.15, 0.20)
    dibujar_letrero_neon(6.6, 0.12, (1.0, 0.08, 0.55))
    glPopMatrix()

    glPopMatrix()


def dibujar_escena():
    dibujar_suelo_y_calle()

    # Arco Torii Cyberpunk sobre la avenida principal
    dibujar_arco_torii_cyberpunk(0.0, 0.0, 4.0)

    # Bloques base de rascacielos (estructura geométrica inicial)
    edificios = [
        # (x, z, ancho, alto, profundo, color_edificio, color_neon, alto_letrero)
        (-7.5, -10.0, 4.5, 16.0, 4.5, (0.10, 0.11, 0.18), (1.0, 0.05, 0.55), 5.0),
        (-7.5, -2.0,  4.2, 11.5, 4.5, (0.12, 0.10, 0.20), (0.0, 0.90, 1.0),  3.8),
        (-7.5, 7.0,   4.8, 14.0, 4.8, (0.09, 0.12, 0.17), (0.75, 0.15, 1.0), 4.5),
        (7.5,  -9.0,  4.6, 18.0, 4.6, (0.09, 0.10, 0.16), (0.0, 0.95, 0.85), 6.0),
        (7.5,  -1.0,  4.2, 12.5, 4.2, (0.13, 0.10, 0.19), (1.0, 0.35, 0.05), 3.5),
        (7.5,  8.0,   4.5, 15.0, 4.5, (0.10, 0.12, 0.20), (1.0, 0.05, 0.55), 4.8),
    ]

    for x, z, w, h, d, col_edif, col_neon, h_let in edificios:
        glPushMatrix()
        glTranslatef(x, 0.25, z)
        dibujar_prisma(w, h, d, col_edif)

        # Letrero neón vertical adosado hacia la avenida
        lado = 1.0 if x < 0 else -1.0
        glPushMatrix()
        glTranslatef(lado * (w / 2.0 + 0.05), h * 0.55, 0.0)
        glRotatef(90.0 * lado, 0.0, 1.0, 0.0)
        dibujar_letrero_neon(0.9, h_let, col_neon)
        glPopMatrix()

        glPopMatrix()


def main():
    pygame.init()
    pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), DOUBLEBUF | OPENGL)
    pygame.display.set_caption(TITULO_VENTANA)

    inicializar_opengl()
    configurar_proyeccion(ANCHO_VENTANA, ALTO_VENTANA)

    camara = CamaraOrbital()
    reloj = pygame.time.Clock()
    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == QUIT:
                ejecutando = False
            elif evento.type == KEYDOWN:
                if evento.key == K_ESCAPE:
                    ejecutando = False
                elif evento.key == K_r:
                    camara = CamaraOrbital()

        # Controles continuos de cámara
        teclas = pygame.key.get_pressed()
        if teclas[K_LEFT]:
            camara.angulo_y -= 1.2
        if teclas[K_RIGHT]:
            camara.angulo_y += 1.2
        if teclas[K_UP]:
            camara.angulo_x = min(80.0, camara.angulo_x + 1.0)
        if teclas[K_DOWN]:
            camara.angulo_x = max(5.0, camara.angulo_x - 1.0)
        if teclas[K_w]:
            camara.distancia = max(8.0, camara.distancia - 0.35)
        if teclas[K_s]:
            camara.distancia = min(60.0, camara.distancia + 0.35)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        camara.aplicar()
        dibujar_escena()

        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
