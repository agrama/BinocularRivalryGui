from math import pi, sin, cos

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import *
import numpy as np
import sys

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
        uniform float rot_angle;
        uniform float phi;
        uniform float x_scale;
        uniform float y_scale;
        uniform float rot_angle_increment;

        uniform float x_pos;
        uniform float y_pos;
        uniform float aspect_ratio;
        uniform float cycles;

        void main() {

        mat2 rotation1 = mat2( cos(rot_angle-rot_angle_increment), sin(rot_angle-rot_angle_increment),
                      -sin(rot_angle-rot_angle_increment), cos(rot_angle-rot_angle_increment));
          mat2 rotation2 = mat2( cos(rot_angle+rot_angle_increment), sin(rot_angle+rot_angle_increment),
                      -sin(rot_angle+rot_angle_increment), cos(rot_angle+rot_angle_increment));


          vec2 texcoord_scaled = vec2(texcoord.x * x_scale, texcoord.y * y_scale);
          vec2 texcoord_rotated1 = rotation1*texcoord_scaled.xy;
          vec2 texcoord_rotated2 = rotation2*texcoord_scaled.xy;
          //vec2 color1 = vec2((sign(sin(texcoord_rotated1.x*2*3.14*cycles - phi))+1)/2, (sign(sin(texcoord_rotated2.x*2*3.14*cycles + phi))+1)/2)

          //color0 = (color0-0.5) * exp(-1* ( pow((texcoord.x - x_pos)*aspect_ratio,2) + pow((texcoord.y - y_pos),2) )/(2*pow(gauss_sigma,2)) ) + 0.5;
          //if (pow((texcoord.x - x_pos)*aspect_ratio,2) + pow((texcoord.y - y_pos),2) > gabor_radius ){
            //            color0 = vec4(0.5,0.5,0.5,1);
              //          }
          vec4 color0 = vec4(0.2*(sign(sin(texcoord_rotated1.x*2*3.14*(cycles+3) + phi))+1)/2, 0.2*(sign(sin(texcoord_rotated2.x*2*3.14*cycles - phi+ (3.14/10)))+1)/2, 0, 1);
          gl_FragColor = color0;
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
        self.accept('arrow_right', self.SpatialfrequencyIncrease)
        self.accept('arrow_left', self.SpatialfrequencyDecrease)
        self.accept('arrow_up', self.TemporalfrequencyIncrease)
        self.accept('arrow_down', self.TemporalfrequencyDecrease)

        x = np.linspace(0, 2 * np.pi, 100)
        y = (np.sign(np.sin(x)) + 1) / 2 * 255

        self.tex = Texture("texture")
        self.tex.setMagfilter(Texture.FTLinear)

        self.tex.setup2dTexture(100, 1, Texture.TUnsignedByte, Texture.FLuminance)
        memoryview(self.tex.modify_ram_image())[:] = y.astype(np.uint8).tobytes()

        cm = CardMaker('card')

        self.cardnode = self.render.attachNewNode(cm.generate())

        self.lens1 = PerspectiveLens()
        self.lens1.setNearFar(0.01, 100)
        self.lens1.setFov(90, 90)
        self.cam.node().setLens(self.lens1)

        self.cardnode.setPos(-0.5, 0.5, -0.5)

        self.cardnode.setTexture(self.tex)

        self.my_shader = Shader.make(Shader.SLGLSL, my_shader[0], my_shader[1])

        self.cardnode.setShader(self.my_shader)
        # self.cardnode.hide()
        self.scale = 1
        self.cycles = 5
        self.temporal_frequency = 4
        self.cardnode.setShaderInput("x_scale", self.scale * 1.56)  # this is the measured aspect ratio of the projector
        self.cardnode.setShaderInput("aspect_ratio", 1.56)
        self.cardnode.setShaderInput("y_scale", self.scale)
        self.cardnode.setShaderInput("cycles", self.cycles)
        self.cardnode.setShaderInput("x_pos", 0.5)
        self.cardnode.setShaderInput("y_pos", 0.5)
        self.cardnode.setShaderInput("phi", 0)
        self.cardnode.setShaderInput("rot_angle", 0)
        self.cardnode.setShaderInput("rot_angle_increment", np.pi/100)
        self.setBackgroundColor(0.5, 0.5, 0.5)
        self.taskMgr.add(self.frameFlipper, "frameFlipper")

    def SpatialfrequencyIncrease(self):
        self.cycles += 1
        self.cardnode.setShaderInput("cycles", self.cycles)
        print(self.cycles)

    def SpatialfrequencyDecrease(self):
        self.cycles -= 1
        self.cardnode.setShaderInput("cycles", self.cycles)
        print(self.cycles)

    def TemporalfrequencyIncrease(self):
        self.temporal_frequency += 0.05
        print(self.temporal_frequency)

    def TemporalfrequencyDecrease(self):
        self.temporal_frequency -= 0.05
        print(self.temporal_frequency)

    def frameFlipper(self, task):
        # self.cardnode.setShaderInput("cycles",self.cycles)
        self.cardnode.setShaderInput("phi", task.time * 2 * np.pi * self.temporal_frequency)
        # self.cardnode.show()
        return task.cont


if __name__ == "__main__":
    app = MyApp()
    app.run()