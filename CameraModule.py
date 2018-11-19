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
        try:
            camera.open()
            print("Camera is opened")
        except:
            camera.close()
            print('could not open cameras')
            self.shared.main_program_still_running.value = 0
        # camera.properties['BinningHorizontalMode'] = 'Average'
        # camera.properties['BinningVerticalMode'] = 'Average'
        camera.properties['Gain'] = 1
        camera.properties['BinningVertical'] = 4
        camera.properties['BinningHorizontal'] = 4
        camera.properties['ExposureTime'] = 20000


        self.shared.frame_width.value = camera.properties['Width']
        self.shared.frame_height.value = camera.properties['Height']

        self.shared.framerate.value = camera.properties['ResultingFrameRate']
        stim_dict = {'LeftGrating':0,'RightGrating':1,'RivalrousLeftRightMovingGrating': 2, 'RivalrousUpDownMovingGrating': 3,
                     'ContrastCoherent': 4, 'ContrastRivalrousHighandLowFlicker': 5, 'ContrastRivalrousNoFlicker': 6,
                     'LowContrastFlicker': 7, 'HighContrastFlicker': 8, 'LowContrastCoherent': 9,
                     'HighContrastCoherent': 10, 'FlashSuppLowFlash': 11, 'FlashSuppHighFlash': 12,
                     'FlashSuppLeftGrating':13, 'FlashSuppRightGrating': 14}  # for accessing trial number from shared variable
        camera_generator = camera.grab_images(-1)
        # first_time = time.time()
        while self.shared.main_program_still_running.value == 1:
            # print('wtf')
            if self.shared.camera_exposure_update_requested.value == 1:
                camera.properties['ExposureTime'] = self.shared.camera_exposure.value
                self.shared.framerate.value = camera.properties['ResultingFrameRate']
                self.shared.camera_exposure_update_requested.value = 0
            if self.shared.camera_gain_update_requested.value == 1:
                camera.properties['Gain'] = self.shared.camera_gain.value
                self.shared.camera_gain_update_requested.value = 0


            img = camera_generator.__next__()
            data = img.flatten()
            self.shared.frame_len.value = len(data)
            self.shared.frame[:len(data)] = data
            # second_time = time.time()
            # print(1 / (second_time - first_time))
            # first_time = second_time
            if self.shared.start_cam.value == 1:
                stim_type = bytearray(self.shared.stim_type[:self.shared.stim_type_len.value]).decode()
                stim_trial_count = np.ctypeslib.as_array(self.shared.stim_trial_count)
                path_to_file = os.path.join(bytearray(self.shared.save_path[:self.shared.save_path_len.value]).decode(),
                           stim_type+ '_trial_' + str(stim_trial_count[stim_dict[stim_type]]) +'_cycles_'+ str(self.shared.numcycles.value)+ '_freq_'+str(self.shared.temporalfreq.value)+'_rot_'+str(self.shared.gratings_angle.value)+'_brightness_' + str(
                                                round(self.shared.gratings_brightness.value,2))+'_lowcontrast_' + str(
                                                round(self.shared.low_contrast.value,2))+ '_highcontrast_' + str(round(self.shared.high_contrast.value,2)) + '_maskrad_' + str(round(self.shared.mask_radius.value,2)) + '_phase_' + str(round(self.shared.phase_change.value,2)) +'_righteye.tif')
                print(path_to_file)

                tif = tiff.TiffWriter(path_to_file, append=True,imagej=True)
                self.shared.stim_on.value = 1
                # first_time=time.time()
                for i in range(0,int(self.shared.numframes.value)):
                    img = camera_generator.__next__()
                    self.shared.framenum.value += 1
                    # second_time = time.time()
                    tif.save(img,metadata={'Framerate':self.shared.framerate.value,'Cycles': self.shared.numcycles.value, 'Freq': self.shared.temporalfreq.value, 'RotAng': self.shared.gratings_angle.value, 'Brightness': self.shared.gratings_brightness.value})
                    data = img.flatten()
                    self.shared.frame_len.value = len(data)
                    self.shared.frame[:len(data)] = data
                    # print(1/(second_time-first_time))
                    # first_time = second_time
                tif.close()
                print(path_to_file + ' tif closed')
                self.shared.start_cam.value = 0


            self.shared.framenum.value = 0
        camera.close()
        print('Camera is closed')



