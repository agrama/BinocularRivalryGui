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
        uniform sampler2D p3d_Texture1;
        in vec2 texcoord;
        out vec4 gl_FragColor;
        uniform float pulse;
        float aspect_ratio = 1.56;
        uniform float cycles;

        void main() {
          vec4 color0 = texture(p3d_Texture0, texcoord);
          vec4 color1 = texture(p3d_Texture1, texcoord);
          if (pulse == 1){
                     gl_FragColor = vec4(color0.x, color1.y, 0, 1);
           }
          else{
                gl_FragColor = vec4(color0.x, 0.5, 0, 1);
               }
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

        self.accept('arrow_down', self.Pulser)
        path_to_file_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), 'aperture images\original matched images'))
        onlyfiles = [os.path.join(path_to_file_dir, str(f) + ".tif") for f in range(1, 3)] # load 1 and 2 images
        self.tex0 = loader.loadTexture(Filename.from_os_specific(onlyfiles[0]))
        self.tex1 = loader.loadTexture(Filename.from_os_specific(onlyfiles[1]))
        ts0 = TextureStage("mapping texture stage0")
        ts0.setSort(0)
        ts1 = TextureStage("mapping texture stage1")
        ts1.setSort(1)
        cm = CardMaker('card')

        self.cardnode = self.render.attachNewNode(cm.generate())

        self.lens1 = PerspectiveLens()
        self.lens1.setNearFar(0.01, 100)
        self.lens1.setFov(90, 90)
        self.cam.node().setLens(self.lens1)

        self.cardnode.setPos(-0.5, 0.5, -0.5)

        self.cardnode.setTexture(ts0, self.tex0)
        self.cardnode.setTexture(ts1, self.tex1)

        self.my_shader = Shader.make(Shader.SLGLSL, my_shader[0], my_shader[1])

        self.cardnode.setShader(self.my_shader)
        # self.cardnode.hide()

        self.pulse = 0
        self.pulsetimer = 0
        self.cardnode.setShaderInput("pulse", self.pulse)
        self.setBackgroundColor(0.5, 0.5, 0.5)
        self.taskMgr.add(self.frameFlipper, "frameFlipper")
    def Pulser(self):
        self.pulse = 1
        self.pulsetimer += 0.0167# time in ms of a frame
        self.cardnode.setShaderInput("pulse",self.pulse)
    def frameFlipper(self, task):
        if self.pulsetimer > 3:
            self.pulsetimer = 0
            self.pulse = 0
            self.cardnode.setShaderInput("pulse", self.pulse)
        if self.pulsetimer > 0:
            self.pulsetimer += 0.0167

        return task.cont


if __name__ == "__main__":
    app = MyApp()
    app.run()