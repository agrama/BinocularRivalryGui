from multiprocessing import Value, Array, Queue, sharedctypes
import ctypes
from CameraModule import CameraModule
from StimulusModule import StimulusModule


class Shared():
    def __init__(self):
        self.main_program_still_running = Value("b", 1)
        ###inputs from GUI
        #camera input
        self.camera_exposure = Value("i", 10000)
        self.camera_exposure_update_requested = Value("b", 0)
        self.camera_gain = Value('f', 1.0)
        self.camera_gain_update_requested = Value('b', 0)

        self.camera1_gain = Value('f', 1.0)
        self.camera1_gain_update_requested = Value('b', 0)
        #path input
        self.save_path = sharedctypes.RawArray(ctypes.c_ubyte, 2000)
        self.save_path_len = Value("i", 0)

        #stim input
        self.stim_type = sharedctypes.RawArray(ctypes.c_ubyte,500)
        self.stim_type_len = Value('i',0)
        self.stim_type_update_requested = Value('b',0)
        self.stim_trial_count = sharedctypes.RawArray(ctypes.c_ubyte,3)
        self.numframes = Value('i',50)
        self.inter_stim_frame_interval = Value('i', 100)
        self.numcycles = Value('i',4)
        self.numcycles_update_requested = Value('b',0)
        self.temporalfreq = Value('f',2.0)
        self.temporalfreq_update_requested = Value('b',0)

        ### camera capture
        self.frame = sharedctypes.RawArray(ctypes.c_int16, 500*500)
        self.frame1 = sharedctypes.RawArray(ctypes.c_int16, 500*500)
        self.frame_len = Value("i", 0)
        self.frame_width = Value("i", 200)
        self.frame_height = Value("i", 200)
        self.framerate = Value("f", 10)
        self.framenum = Value('i',0)

        ### start experiment and show stim
        self.start_exp = Value('b',0)
        self.stim_on = Value('b',0)
        self.show_stim = Value('b',0)

    def start_threads(self):
        cameramodule = CameraModule(self)
        cameramodule.start()
        stimulusmodule = StimulusModule(self)
        stimulusmodule.start()