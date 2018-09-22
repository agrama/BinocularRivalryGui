import pypylon as pp
from multiprocessing import Process
import os
import numpy as np
import time
import tifffile as tiff

class CameraModule1(Process):
    def __init__(self,shared):
        Process.__init__(self)
        self.shared = shared
    def run(self):
        camera_list = pp.factory.find_devices()
        print(camera_list)
        camera1 = pp.factory.create_device(camera_list[1])
        try:
            camera1.open()
            print("Camera 1 is opened")
        except:
            camera1.close()
            print('could not open cameras')
            self.shared.main_program_still_running.value = 0
        # camera.properties['BinningHorizontalMode'] = 'Average'
        # camera.properties['BinningVerticalMode'] = 'Average'
        camera1.properties['Gain'] = 1
        camera1.properties['BinningVertical'] = 4
        camera1.properties['BinningHorizontal'] = 4
        camera1.properties['ExposureTime'] = 20000

        stim_dict = {'LeftGrating': 0, 'RightGrating': 1, 'RivalrousLeftRightMovingGrating': 2,
                     'RivalrousUpDownMovingGrating': 3,
                     'ContrastCoherent': 4, 'ContrastRivalrousHighandLowFlicker': 5, 'ContrastRivalrousNoFlicker': 6,
                     'LowContrastFlicker': 7, 'HighContrastFlicker': 8, 'LowContrastCoherent': 9,
                     'HighContrastCoherent': 10, 'FlashSuppLowFlash': 11,
                     'FlashSuppHighFlash': 12}  # for accessing trial number from shared variable
        camera1_generator = camera1.grab_images(-1)
        # first_time = time.time()
        while self.shared.main_program_still_running.value == 1:
            # print('wtf1')
            if self.shared.camera_exposure_update_requested.value == 1:
                camera1.properties['ExposureTime'] = self.shared.camera_exposure.value

            if self.shared.camera1_gain_update_requested.value == 1:
                camera1.properties['Gain'] = self.shared.camera1_gain.value
                self.shared.camera1_gain_update_requested.value = 0
            img1 = camera1_generator.__next__()
            data1 = img1.flatten()

            self.shared.frame1[:len(data1)] = data1
            # second_time = time.time()
            # print(1 / (second_time - first_time))
            # first_time = second_time
            if self.shared.start_cam1.value == 1:
                stim_type = bytearray(self.shared.stim_type[:self.shared.stim_type_len.value]).decode()
                stim_trial_count = np.ctypeslib.as_array(self.shared.stim_trial_count)

                path_to_file1 = os.path.join(bytearray(self.shared.save_path[:self.shared.save_path_len.value]).decode(),
                           stim_type+ '_trial_' + str(stim_trial_count[stim_dict[stim_type]]) +'_cycles_'+ str(self.shared.numcycles.value)+ '_freq_'+str(self.shared.temporalfreq.value)+'_rot_'+str(self.shared.gratings_angle.value)+'_brightness_' + str(
                                                round(self.shared.gratings_brightness.value,2))+'_lowcontrast_' + str(
                                                round(self.shared.low_contrast.value,2)) + '_highcontrast_' + str(round(self.shared.high_contrast.value,2)) + '_maskrad_' + str(round(self.shared.mask_radius.value,2)) +'_lefteye.tif')
                print(path_to_file1)
                tif1 = tiff.TiffWriter(path_to_file1, append=True, imagej=True)
                # first_time=time.time()
                for i in range(0,int(self.shared.numframes.value)):
                    img1 = camera1_generator.__next__()
                    # second_time = time.time()
                    tif1.save(img1, metadata={'Framerate': self.shared.framerate.value,'Cycles': self.shared.numcycles.value, 'Freq': self.shared.temporalfreq.value, 'RotAng': self.shared.gratings_angle.value, 'Brightness': self.shared.gratings_brightness.value})
                    data1 = img1.flatten()
                    self.shared.frame1[:len(data1)] = data1
                    # print(1/(second_time-first_time))
                    # first_time = second_time
                tif1.close()
                print(path_to_file1 + ' tif1 closed')
                self.shared.start_cam1.value = 0
        camera1.close()
        print('Camera1 is closed')



