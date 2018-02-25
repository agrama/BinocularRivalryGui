import pypylon as pp
from multiprocessing import Process
import os
import numpy as np
import time
import tifffile as tiff

class CameraModule(Process):
    def __init__(self,shared):
        Process.__init__(self)
        self.shared = shared
    def run(self):
        camera_list = pp.factory.find_devices()
        print(camera_list)
        camera = pp.factory.create_device(camera_list[0])
        camera1 = pp.factory.create_device(camera_list[1])
        try:
            camera.open()
            camera1.open()
            print("Cameras are opened")
        except:
            camera.close()
            camera1.close()
            print('could not open cameras')
            self.shared.main_program_still_running.value = 0
        # camera.properties['BinningHorizontalMode'] = 'Average'
        # camera.properties['BinningVerticalMode'] = 'Average'
        camera.properties['Gain'] = 1
        camera.properties['BinningVertical'] = 4
        camera.properties['BinningHorizontal'] = 4
        camera.properties['ExposureTime'] = 1000
        camera1.properties['Gain'] = 1
        camera1.properties['BinningVertical'] = 4
        camera1.properties['BinningHorizontal'] = 4
        camera1.properties['ExposureTime'] = 1000

        self.shared.frame_width.value = camera.properties['Width']
        self.shared.frame_height.value = camera.properties['Height']

        self.shared.framerate.value = camera.properties['ResultingFrameRate']
        stim_dict = {'LeftGrating':0,'RightGrating':1,'Rivalrous':2} # for accessing trial number from shared variable
        camera_generator = camera.grab_images(-1)
        camera1_generator = camera1.grab_images(-1)
        # first_time = time.time()
        while self.shared.main_program_still_running.value == 1:
            # print('wtf')
            if self.shared.camera_exposure_update_requested.value == 1:
                camera.properties['ExposureTime'] = self.shared.camera_exposure.value
                camera1.properties['ExposureTime'] = self.shared.camera_exposure.value
                self.shared.framerate.value = camera.properties['ResultingFrameRate']
                self.shared.camera_exposure_update_requested.value = 0
            if self.shared.camera_gain_update_requested.value == 1:
                camera.properties['Gain'] = self.shared.camera_gain.value
                self.shared.camera_gain_update_requested.value = 0

            if self.shared.camera1_gain_update_requested.value == 1:
                camera1.properties['Gain'] = self.shared.camera1_gain.value
                self.shared.camera1_gain_update_requested.value = 0
            img = camera_generator.__next__()
            img1 = camera1_generator.__next__()
            data = img.flatten()
            data1 = img1.flatten()
            self.shared.frame_len.value = len(data)
            self.shared.frame[:len(data)] = data
            self.shared.frame1[:len(data)] = data1
            # second_time = time.time()
            # print(1 / (second_time - first_time))
            # first_time = second_time
            if self.shared.start_exp.value == 1:
                stim_type = bytearray(self.shared.stim_type[:self.shared.stim_type_len.value]).decode()
                stim_trial_count = np.ctypeslib.as_array(self.shared.stim_trial_count)
                path_to_file = os.path.join(bytearray(self.shared.save_path[:self.shared.save_path_len.value]).decode(),
                           stim_type+ '_trial_' + str(stim_trial_count[stim_dict[stim_type]]+1) +'_righteye.tif')
                path_to_file1 = os.path.join(bytearray(self.shared.save_path[:self.shared.save_path_len.value]).decode(),
                                            stim_type + '_trial_' + str(
                                                stim_trial_count[stim_dict[stim_type]] + 1) + '_lefteye.tif')
                tif = tiff.TiffWriter(path_to_file, append=True,imagej=True)
                tif1 = tiff.TiffWriter(path_to_file1, append=True, imagej=True)
                self.shared.stim_on.value = 1
                first_time=time.time()
                for i in range(0,int(self.shared.numframes.value)):
                    img = camera_generator.__next__()
                    img1 = camera1_generator.__next__()
                    self.shared.framenum.value += 1
                    second_time = time.time()
                    tif.save(img,metadata={'Framerate':self.shared.framerate.value,'Cycles': self.shared.numcycles.value, 'Freq': self.shared.temporalfreq.value})
                    tif1.save(img1, metadata={'Framerate': self.shared.framerate.value,'Cycles': self.shared.numcycles.value, 'Freq': self.shared.temporalfreq.value})
                    data = img.flatten()
                    data1 = img1.flatten()
                    self.shared.frame_len.value = len(data)
                    self.shared.frame[:len(data)] = data
                    self.shared.frame1[:len(data1)] = data1
                    # print(1/(second_time-first_time))
                    first_time = second_time
                self.shared.start_exp.value = 0
                self.shared.framenum.value = 0
                tif.close()
                tif1.close()
        camera.close()
        camera1.close()
        print('Camera is closed')



