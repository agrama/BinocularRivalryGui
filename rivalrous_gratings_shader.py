from math import pi, sin, cos

from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.DirectGui import *
import numpy as np
import sys
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
        uniform sampler2D p3d_Texture2;
        in vec2 texcoord;
        out vec4 gl_FragColor;
        uniform float rot_angle;
        uniform float phi;
        uniform float x_scale;
        uniform float y_scale;
        uniform float rot_angle_increment;
        uniform float stimcode;
        uniform float x_pos;
        uniform float y_pos;
        uniform float aspect_ratio;
        uniform float cycles;
        uniform float gratings_brightness;
        uniform float low_contrast;
        uniform float high_contrast;

        void main() {

        mat2 rotation1 = mat2( cos(rot_angle-rot_angle_increment), sin(rot_angle-rot_angle_increment),
                      -sin(rot_angle-rot_angle_increment), cos(rot_angle-rot_angle_increment));
          mat2 rotation2 = mat2( cos(rot_angle+rot_angle_increment), sin(rot_angle+rot_angle_increment),
                      -sin(rot_angle+rot_angle_increment), cos(rot_angle+rot_angle_increment));


          vec2 texcoord_scaled = vec2(texcoord.x * x_scale, texcoord.y * y_scale);
          vec2 texcoord_rotated1 = rotation1*texcoord_scaled.xy;
          vec2 texcoord_rotated2 = rotation2*texcoord_scaled.xy;
          
          //vec4 color1 = texture(p3d_Texture1, texcoord);
          //vec4 color2 = texture(p3d_Texture2, texcoord);
          
          if(stimcode == 0){
            vec4 color0 = vec4(gratings_brightness*(sign(sin(texcoord_rotated2.x*2*3.14*cycles - phi))+1)/2, gratings_brightness*(sign(sin(texcoord_rotated2.x*2*3.14*cycles - phi+ (3.14/10)))+1)/2, 0, 1);
            gl_FragColor = color0;
            }
          if(stimcode == 1){
            vec4 color0 = vec4(gratings_brightness*(sign(sin(texcoord_rotated1.x*2*3.14*cycles + phi))+1)/2, gratings_brightness*(sign(sin(texcoord_rotated1.x*2*3.14*cycles + phi+ (3.14/10)))+1)/2, 0, 1);
            gl_FragColor = color0;
          }
          if(stimcode == 2){
            vec4 color0 = vec4(gratings_brightness*(sign(sin(texcoord_rotated1.x*2*3.14*cycles + phi))+1)/2, gratings_brightness*(sign(sin(texcoord_rotated2.x*2*3.14*cycles - phi+ (3.14/10)))+1)/2, 0, 1);
            gl_FragColor = color0;
            }
          if(stimcode == 3){
            gl_FragColor = vec4((low_contrast*gratings_brightness*2*(sign(sin(texcoord_rotated1.x * 2 * 3.14 * cycles )) + 1)/2) + gratings_brightness,(low_contrast*gratings_brightness*2*(sign(sin(texcoord_rotated1.x * 2 * 3.14 * cycles )) + 1)/2) + gratings_brightness,0,1);
            //gl_FragColor = 0.5*color1;
            }
          if(stimcode == 4){
            gl_FragColor = vec4((high_contrast*gratings_brightness*2*(sign(sin(texcoord_rotated1.x * 2 * 3.14 * cycles )) + 1)/2) + gratings_brightness,(high_contrast*gratings_brightness*2*(sign(sin(texcoord_rotated1.x * 2 * 3.14 * cycles )) + 1)/2) + gratings_brightness,0,1);
            //gl_FragColor = 0.5*color2;
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
    def __init__(self, shared):
        ShowBase.__init__(self)
        self.shared = shared
        self.disableMouse()
        self.accept('escape', self.escapeAction)
        x = np.linspace(0, 2 * np.pi, 100)
        y = (np.sign(np.sin(x)) + 1) / 2 * 255

        self.tex = Texture("texture")
        self.tex.setMagfilter(Texture.FTLinear)

        self.tex.setup2dTexture(100, 1, Texture.TUnsignedByte, Texture.FLuminance)
        memoryview(self.tex.modify_ram_image())[:] = y.astype(np.uint8).tobytes()

        # changing things to add images
        path_to_file_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), 'aperture images'))
        onlyfiles = [os.path.join(path_to_file_dir, str(f) + ".tif") for f in range(1, 3)]  # load 1 and 2 images
        self.tex1 = loader.loadTexture(Filename.from_os_specific(onlyfiles[0]))
        self.tex2 = loader.loadTexture(Filename.from_os_specific(onlyfiles[1]))

        ts0 = TextureStage("mapping texture stage0")       # will use this texture stage for gratings
        ts0.setSort(0)
        ts1 = TextureStage("mapping texture stage1")        # will use this texture stage for image 1
        ts1.setSort(1)
        ts2 = TextureStage("mapping texture stage2")        # will use this texture stage for image 2
        ts2.setSort(2)

        cm = CardMaker('card')

        self.cardnode = self.render.attachNewNode(cm.generate())

        self.lens1 = PerspectiveLens()
        self.lens1.setNearFar(0.01, 100)
        self.lens1.setFov(90, 90)
        self.cam.node().setLens(self.lens1)

        self.cardnode.setPos(-0.5, 0.5, -0.5)
        # making changes here to add textures to different texture stages
        self.cardnode.setTexture(ts0,self.tex)
        self.cardnode.setTexture(ts1, self.tex1)
        self.cardnode.setTexture(ts2, self.tex2)

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
        self.cardnode.setShaderInput("rot_angle_increment", 0)
        self.cardnode.setShaderInput("stimcode",0)
        self.cardnode.setShaderInput("gratings_brightness",0.1)
        self.cardnode.setShaderInput("low_contrast", 0.1)
        self.cardnode.setShaderInput("high_contrast",0.5)

        self.setBackgroundColor(self.shared.gratings_brightness.value, self.shared.gratings_brightness.value, self.shared.gratings_brightness.value) # 05/09/18 making change here to put the background color as grating brightness
        self.cardnode.hide()

    def escapeAction(self):
        self.shared.main_program_still_running.value = 0


