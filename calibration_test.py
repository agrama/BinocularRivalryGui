from math import pi, sin, cos

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import *
import numpy as np
import sys
import random as rn
import os

my_shader = [
    """#version 140

            uniform mat4 p3d_ModelViewProjectionMatrix;
            in vec4 p3d_Vertex;
            in vec2 p3d_MultiTexCoord;
            out vec2 texcoord;

            void main() {
              gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
              texcoord = p3d_MultiTexCoord;
            }
    """,

    """#version 140

        uniform sampler2D p3d_Texture0;
        in vec2 texcoord;
        out vec4 gl_FragColor;
        uniform float brightness;

        void main() {
          gl_FragColor = vec4(brightness,0,0,1);
          
           
       }
    """
]

loadPrcFileData("",
                """sync-video #t
                fullscreen #f
                win-origin 1920 0
                undecorated #t
                cursor-hidden #t
                win-size %d %d
                show-frame-rate-meter #f
                """ % (912, 1140))


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.accept('escape', sys.exit)
        self.accept('a', self.IncreaseBrightness)
        self.accept('s', self.DecreaseBrightness)

        # self.accept('arrow_down', self.Pulser)
        x = np.linspace(0, 2 * np.pi, 100)
        y = (np.sign(np.sin(x)) + 1) / 2 * 255

        self.tex = Texture("texture")
        self.tex.setMagfilter(Texture.FTLinear)

        self.tex.setup2dTexture(100, 1, Texture.TUnsignedByte, Texture.FLuminance)
        memoryview(self.tex.modify_ram_image())[:] = y.astype(np.uint8).tobytes()
        ts0 = TextureStage("mapping texture stage0")
        ts0.setSort(0)

        cm = CardMaker('card')

        self.cardnode = self.render.attachNewNode(cm.generate())

        self.lens1 = PerspectiveLens()
        self.lens1.setNearFar(0.01, 100)
        self.lens1.setFov(90, 90)
        self.cam.node().setLens(self.lens1)

        self.cardnode.setPos(-0.5, 0.5, -0.5)

        self.cardnode.setTexture(ts0, self.tex)

        self.my_shader = Shader.make(Shader.SLGLSL, my_shader[0], my_shader[1])

        self.cardnode.setShader(self.my_shader)
        self.brightness = 0.0
        self.cardnode.setShaderInput("brightness", self.brightness)

    def IncreaseBrightness(self):
        self.brightness += 0.1
        self.cardnode.setShaderInput("brightness", self.brightness)
        print(self.brightness)

    def DecreaseBrightness(self):
        self.brightness -= 0.1
        self.cardnode.setShaderInput("brightness", self.brightness)
        print(self.brightness)


if __name__ == "__main__":
    app = MyApp()
    app.run()