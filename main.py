import pygame
from pygame.locals import *
import time
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

vertices = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
    )

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )

class Clock:
    def __init__(self):
        self.dt = 0.1
        self.prev = time.time()
    
    def endFrame(self):
        now = time.time()
        self.dt = now - self.prev
        self.prev = now

MODE_3D_PERSPECTIVE = 0
MODE_3D_ORTHO = 1
MODE_2D_TOP = 2
MODE_COUNT = 3

def sgn(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0

class Display:
    def __init__(self):
        display = pygame.display.get_desktop_sizes()[0]
        display = (display[0] - 100, display[1] - 150)
        pygame.display.set_mode(display, RESIZABLE | DOUBLEBUF | OPENGL)
        self.font = pygame.font.Font(None, 30)
        self.mode = MODE_3D_PERSPECTIVE
        self.setupGL()
        self.resize(display)
        self.clock = Clock()
        self.overlayTextureID = glGenTextures(1)
        self.tpt = 0
        self.x = 0
        self.dx = 1

    def setupGL(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
    def surfaceToTexture(self, pygame_surface, texID):
        rgb_surface = pygame.image.tostring( pygame_surface, 'RGBA')
        glBindTexture(GL_TEXTURE_2D, texID)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        surface_rect = pygame_surface.get_rect()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, surface_rect.width, surface_rect.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, rgb_surface)

    def renderOverlay(self):
        self.surfaceToTexture(self.bgsurface, self.overlayTextureID)
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.overlayTextureID)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(-1, 1)
        glTexCoord2f(0, 1); glVertex2f(-1, -1)
        glTexCoord2f(1, 1); glVertex2f(1, -1)
        glTexCoord2f(1, 0); glVertex2f(1, 1)
        glEnd()
        glPopMatrix()

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def beginFrame(self):
        self.bgsurface.fill((0, 0, 0, 0))
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        glDisable(GL_TEXTURE_2D)
        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_DEPTH_TEST)
        # glEnable(GL_CULL_FACE)
    
    def endFrame(self):
        pygame.display.flip()
        self.clock.endFrame()
        self.tpt = 0.99 * self.tpt + 0.01 * self.clock.dt

    def drawString(self, str, coord):
        text = self.font.render(str, True, (255, 255, 255))
        self.bgsurface.blit(text, coord)

    def drawCube(self, x, y, z):
        glPushMatrix()
        glTranslate(x, y, z)
        glScale(0.1, 0.1, 0.1)
        glBegin(GL_LINES)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()
        glPopMatrix()

    def render(self):
        self.beginFrame()
        self.drawCube(0, 0, 0)
        self.drawCube(0, 1, 0)
        glPushMatrix()
        glTranslate(self.x, 0, 0)
        # self.drawLines()
        if self.tpt != 0:
            self.drawString(str(int(1 / self.tpt)), (0, 0))
        self.renderOverlay()
        self.endFrame()
        glPopMatrix()
    
    def drawLines(self):
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)
        glVertex3f(0.5,  1, 0.5)
        glVertex3f(-0.5, 1,  0.5)
        glVertex3f(-0.5, 1,  -0.5)
        glVertex3f(0.5,  1, -0.5)
        glEnd()
        glColor3f(1, 0, 0)
        glBegin(GL_QUADS)
        glVertex3f( 0.7,  1.2,  0.7)
        glVertex3f(-0.7,  1.2,  0.7)
        glVertex3f(-0.7,  1.2, -0.7)
        glVertex3f( 0.7,  1.2, -0.7)
        glEnd()

    def update(self):
        dt = self.clock.dt
        self.x += 0.5 * dt * self.dx
        if abs(self.x) > 0.3:
            self.dx = - sgn(self.x)

        # glTranslate(0.1 * dt, 0, 0)
        glRotatef(100 * dt, 0, 0, 1)
    def resize(self, size):
        glViewport(0, 0, size[0], size[1])
        self.bgsurface = pygame.Surface(size, SRCALPHA)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        zn = 0.01
        zf = 10
        fovy = 80
        aspect = size[0] / size[1]
        # aspect = 1
        if self.mode == MODE_3D_PERSPECTIVE:
            # Create a perspective matrix such that:
            # positive x is to the right
            # positive z is up
            # positive y is outward of the camera (i.e. the direction you are looking at)

            gluPerspective(fovy, aspect, zn, zf)
            m = [1, 0, 0, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 0, 0, 1]
            glMultMatrixf(m)
        elif self.mode == MODE_3D_ORTHO:
            # Create a orthographic matrix such that:
            # positive x is to the right
            # positive z is up
            # positive y is outward of the camera (i.e. the direction you are looking at)
            # Objects at y = 1 appear the same size as with the MODE_3D_PERSPECTIVE
            f = math.tan(math.radians(fovy / 2))
            glOrtho(-f * aspect, f * aspect, -f, f, zn, zf)
            m = [1, 0, 0, 0, 0, 0, -1, 0, 0, 1, 0, 0, 0, 0, 0, 1]
            glMultMatrixf(m)
        elif self.mode == MODE_2D_TOP:
            # Create a orthographic matrix such that:
            # positive x is to the right
            # positive y is up
            # positive z is the direction you are looking at
            # Objects at z = 1 appear the same size as with the MODE_3D_PERSPECTIVE
            # f = math.tan(math.radians(fovy / 2))
            f = 
            glOrtho(-f * aspect, f * aspect, -f, f, zn, zf)
            m = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1]
            glMultMatrixf(m)
        
        
        m = glGetFloatv(GL_PROJECTION_MATRIX).transpose()
        print(m)
        vec = [0.5,  -1, -0.5, 1]
        v = np.dot(m, vec)
        print(f"{v} -> {v/v[3]}")

        glMatrixMode(GL_MODELVIEW)
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.VIDEORESIZE:
                self.resize(event.size)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_p:
                    self.mode += 1
                    self.mode %= MODE_COUNT
                    self.resize(pygame.display.get_window_size())
        

def main():
    pygame.init()

    display = Display()
    # glTranslatef(0.0,0.0, -5)
    while True:
        display.events()
        display.update()
        display.render()
        

if __name__ == "__main__":
    main()