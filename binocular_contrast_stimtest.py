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
        uniform float rot_angle;
        uniform float phi;
        uniform float x_scale;
        uniform float y_scale;
        uniform float rot_angle_increment;
        uniform float cycles;
        uniform float gratings_brightness;
        uniform float low_contrast;
        uniform float high_contrast;
        uniform float stimcode;

        void main() {
          
          mat2 rotation1 = mat2( cos(rot_angle-rot_angle_increment), sin(rot_angle-rot_angle_increment),
                      -sin(rot_angle-rot_angle_increment), cos(rot_angle-rot_angle_increment));
          mat2 rotation2 = mat2( cos(rot_angle+rot_angle_increment), sin(rot_angle+rot_angle_increment),
                      -sin(rot_angle+rot_angle_increment), cos(rot_angle+rot_angle_increment));
          vec2 texcoord_scaled = vec2(texcoord.x * x_scale, texcoord.y * y_scale);
          vec2 texcoord_rotated1 = rotation1*texcoord_scaled.xy;
          vec2 texcoord_rotated2 = rotation2*texcoord_scaled.xy;
          vec4 color0 = texture(p3d_Texture0, texcoord);
          vec4 color1 = texture(p3d_Texture1, texcoord);
          if (pulse == 1){
            //if (pow((texcoord.x - 0.5)*aspect_ratio,2) + pow((texcoord.y - 0.5),2) < 0.3 ){
                if (stimcode == 1){
                gl_FragColor = vec4(high_contrast*gratings_brightness*0.5*sign(sin(texcoord_rotated1.x * 2 * 3.14 *  cycles )) + gratings_brightness,  gratings_brightness, 0, 1);
                }
                else if (stimcode ==2)
                {
                    gl_FragColor = vec4( high_contrast*gratings_brightness*0.5*sign(sin(texcoord_rotated1.x * 2 * 3.14 *  cycles ))*0.7 + gratings_brightness, low_contrast*gratings_brightness*0.5*sign(sin(texcoord_rotated2.x * 2 * 3.14 * cycles )) + gratings_brightness, 0, 1);  
                }
              //          }
            //else{
              //  gl_FragColor = vec4(color0.x, color1.y, 0, 1);
                //}
                  }
          
          else{
                gl_FragColor = vec4(high_contrast*gratings_brightness*0.5*sign(sin(texcoord_rotated1.x * 2 * 3.14 *  cycles )) + gratings_brightness, low_contrast*gratings_brightness*0.5*sign(sin(texcoord_rotated2.x * 2 * 3.14 * cycles )) + gratings_brightness, 0, 1);
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
        self.scale = 1
        self.cycles = 10
        self.gratings_brightness = 0.3
        # self.cardnode.hide()
        self.cardnode.setShaderInput("x_scale", self.scale * 1.56)  # this is the measured aspect ratio of the projector
        self.cardnode.setShaderInput("y_scale", self.scale)
        self.cardnode.setShaderInput("cycles", self.cycles)
        self.cardnode.setShaderInput("rot_angle", 0)
        self.cardnode.setShaderInput("rot_angle_increment", np.deg2rad(20))
        self.cardnode.setShaderInput("gratings_brightness", self.gratings_brightness)
        self.cardnode.setShaderInput("low_contrast", 0.2)
        self.cardnode.setShaderInput("high_contrast", 0.9)
        self.cardnode.setShaderInput("stimcode", 1)
        self.pulse = 0
        self.pulsetimer = 0
        self.cardnode.setShaderInput("pulse", self.pulse)
        self.setBackgroundColor(self.gratings_brightness, self.gratings_brightness, 0)
        self.taskMgr.add(self.frameFlipper, "frameFlipper")
    def Pulser(self):
        print("pulse")
        self.pulse = 1
        self.pulsetimer += 0.0167# time in ms of a frame
        self.cardnode.setShaderInput("pulse",self.pulse)
    def frameFlipper(self, task):
        #### FAIZA change this:
        self.interflickerinterval = 3 # this flickers the image every 4 secs
        if task.time%self.interflickerinterval < 0.1:
            self.pulse = 1
            self.pulsetimer += 0.0167
            self.cardnode.setShaderInput("pulse",self.pulse)
            self.cardnode.setShaderInput("stimcode",1)
        if (task.time+self.interflickerinterval/2)%self.interflickerinterval < 0.1:
            self.pulse = 1
            self.pulsetimer += 0.0167
            self.cardnode.setShaderInput("pulse",self.pulse)
            self.cardnode.setShaderInput("stimcode", 2)
        if self.pulsetimer > 0.3:
            self.pulsetimer = 0
            self.pulse = 0
            self.cardnode.setShaderInput("pulse", self.pulse)
        if self.pulsetimer > 0:
            self.pulsetimer += 0.0167
            self.pulse = abs(self.pulse -1)
            self.cardnode.setShaderInput("pulse",self.pulse)
        return task.cont


if __name__ == "__main__":
    app = MyApp()
    app.run()