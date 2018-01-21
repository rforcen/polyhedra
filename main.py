'''
polyhedra from netlib
'''

import struct
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow)

from read_poly import all_dict_in_path, get_geometry
from rendererGL import RendererGL


class PolyWidget(RendererGL):
    point_color, line_color = [1, 0, 0], [1, 1, 1]
    # from color picker for data
    color_set = [0xF0A39C, 0xDCA9BA, 0xB6B5C8, 0x93BFBD, 0x90C2A0, 0xAABE81, 0xCDB573, 0xE8A97E]

    def __init__(self, dct):
        super(PolyWidget, self).__init__()
        self.set_dict(dct)
        self.setFocusPolicy(Qt.StrongFocus)  # accepts key events

    def init(self, gl):
        def color2arbg(col: int) -> list:  # list of a,r,g,b
            return list(struct.pack('>i', int(col)))

        self.face_color = [color2arbg(c) for c in self.color_set]
        gl.glPointSize(12)
        gl.glLineWidth(6)
        gl.glEnable(gl.GL_POINT_SMOOTH)  # round points
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glEnable(gl.GL_NORMALIZE)
        self.sceneInit(gl)
        self.zoom = -3.5

        gl.glCullFace(gl.GL_BACK)
        gl.glEnable(gl.GL_BLEND)  # enable alpha transparency
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def set_dict(self, vfn):
        self.verts, self.faces, self.normals = vfn
        self.repaint()

    def draw(self, gl):
        def draw_line():
            gl.glColor3fv(self.line_color)
            for face in self.faces:
                gl.glBegin(gl.GL_LINE_LOOP)
                for ci in face:
                    gl.glVertex3fv(self.verts[ci])
                gl.glEnd()

        def draw_point():
            gl.glColor3fv(self.point_color)
            gl.glBegin(gl.GL_POINTS)
            for v in self.verts:
                gl.glVertex3fv(v)
            gl.glEnd()

        def draw_solid():
            for fix, face in enumerate(self.faces):
                gl.glColor3ubv(self.face_color[(len(face) - 3) % len(self.face_color)][1:4])
                gl.glNormal3fv(self.normals[fix])

                gl.glBegin(gl.GL_TRIANGLE_FAN)
                for ci in face:
                    gl.glVertex3fv(self.verts[ci])
                gl.glEnd()

        draw_solid()
        draw_line()
        draw_point()


class Main(QMainWindow):
    def __init__(self, alld, *args):
        super(Main, self).__init__(*args)

        self.alld, self.di = alld, 0
        self.cc = PolyWidget(get_geometry(self.alld[self.di]))

        self.setGeometry(100, 100, 800, 800)
        self.setWindowTitle(self.alld[self.di]['name'][0])

        self.setCentralWidget(self.cc)
        self.show()

    def keyPressEvent(self, event):
        if event.key() < 256:
            ch = chr(event.key()).lower()
            if ch == 'q':
                exit(0)
            elif ch in '+ ':
                self.di += 1 if self.di < len(self.alld) - 1 else 0
            elif ch == '-':
                self.di -= 1 if self.di > 0 else 0

            self.cc.set_dict(get_geometry(self.alld[self.di]))
            self.setWindowTitle(self.alld[self.di]['name'][0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = Main(all_dict_in_path('polyhedra'))

    exit(app.exec_())
