from multiprocessing import Process, Value, Array, Queue, sharedctypes
from rivalrous_gratings_shader import MyApp
import time
import numpy as np
import random as rn
import pickle
import os


class StimulusModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        self.myapp = MyApp(self.shared)
        stim_trial_count = np.ones((13,1),dtype=np.uint)
        self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()

        while self.shared.main_program_still_running.value == 1:
            if self.shared.stim_type_update_requested.value ==1:
                self.stimcode = bytearray(self.shared.stim_type[:self.shared.stim_type_len.value]).decode()
                if self.stimcode == 'LeftGrating':
                    self.myapp.cardnode.setShaderInput("stimcode", 0)
                elif self.stimcode == 'RightGrating':
                    self.myapp.cardnode.setShaderInput("stimcode", 1)
                elif self.stimcode == 'RivalrousMovingGrating':
                    self.myapp.cardnode.setShaderInput("stimcode", 2)
                elif self.stimcode == 'Contrast':
                    self.myapp.cardnode.setShaderInput("stimcode",3)
                elif self.stimcode == 'ContrastRivlarous':
                    self.myapp.cardnode.setShaderInput("stimcode",5)
                elif self.stimcode == 'ContrastRivalrousNoFlicker':
                    self.myapp.cardnode.setShaderInput("stimcode",5)
                self.shared.stim_type_update_requested.value = 0
            if self.shared.temporalfreq_update_requested.value == 1:
                self.myapp.temporal_frequency = self.shared.temporalfreq.value
                self.shared.temporalfreq_update_requested.value = 0
            if self.shared.numcycles_update_requested.value == 1:
                self.myapp.cycles = self.shared.numcycles.value
                self.myapp.cardnode.setShaderInput("cycles", self.myapp.cycles)
                self.shared.numcycles_update_requested.value = 0
            if self.shared.gratings_brightness_update_requested.value == 1:
                self.myapp.cardnode.setShaderInput("gratings_brightness", self.shared.gratings_brightness.value)
                self.myapp.setBackgroundColor(self.shared.gratings_brightness.value, self.shared.gratings_brightness.value,
                                        self.shared.gratings_brightness.value)  # 05/09/18 making change here to put the background color as grating brightness
                self.shared.gratings_brightness_update_requested.value = 0
            if self.shared.gratings_angle_update_requested.value == 1:
                self.myapp.cardnode.setShaderInput("rot_angle_increment",np.deg2rad(self.shared.gratings_angle.value))
                print(self.shared.gratings_angle.value)
                self.shared.gratings_angle_update_requested.value = 0
            if self.shared.mask_radius_update_requested.value == 1:
                self.myapp.mask_radius = self.shared.mask_radius.value
                self.myapp.cardnode.setShaderInput("mask_radius",self.myapp.mask_radius)
                self.shared.mask_radius_update_requested.value = 0
            if self.shared.low_contrast_update_requested == 1:
                self.myapp.cardnode.setShaderInput("low_contrast", self.shared.low_contrast.value)
                self.shared.low_contrast_update_requested.value = 0
            if self.shared.high_contrast_update_requested.value == 1:
                self.myapp.cardnode.setShaderInput("high_contrast",self.shared.high_contrast.value)
                self.shared.high_contrast_update_requested.value = 0
            if self.shared.phase_change_update_requested.value == 1:
                self.myapp.phase_change = self.shared.phase_change.value
                self.shared.phase_change_update_requested.value = 0


            self.first_time = time.time()
            while self.shared.show_stim.value & self.shared.main_program_still_running.value:
                if self.shared.stim_type_update_requested.value == 1:
                    self.stimcode = bytearray(self.shared.stim_type[:self.shared.stim_type_len.value]).decode()
                    if self.stimcode == 'LeftGrating':
                        self.myapp.cardnode.setShaderInput("stimcode", 0)
                    elif self.stimcode == 'RightGrating':
                        self.myapp.cardnode.setShaderInput("stimcode", 1)
                    elif self.stimcode == 'RivalrousLeftRightMovingGrating':
                        self.myapp.cardnode.setShaderInput("stimcode", 2)
                    elif self.stimcode == 'RivalrousUpDownMovingGrating':
                        self.myapp.cardnode.setShaderInput("stimcode", 11)
                    self.shared.stim_type_update_requested.value = 0

                if self.shared.temporalfreq_update_requested.value == 1:
                    self.myapp.temporal_frequency = self.shared.temporalfreq.value
                    self.shared.temporalfreq_update_requested.value = 0

                if self.shared.numcycles_update_requested.value == 1:
                    self.myapp.cycles = self.shared.numcycles.value
                    self.myapp.cardnode.setShaderInput("cycles", self.myapp.cycles)
                    self.shared.numcycles_update_requested.value = 0
                if self.shared.gratings_brightness_update_requested.value == 1:
                    self.myapp.cardnode.setShaderInput("gratings_brightness", self.shared.gratings_brightness.value)
                    self.myapp.setBackgroundColor(self.shared.gratings_brightness.value,
                                            self.shared.gratings_brightness.value,
                                            self.shared.gratings_brightness.value)  # 05/09/18 making change here to put the background color as grating brightness
                    self.shared.gratings_brightness_update_requested.value = 0
                if self.shared.gratings_angle_update_requested.value == 1:
                    self.myapp.cardnode.setShaderInput("rot_angle_increment",
                                                       np.deg2rad(self.shared.gratings_angle.value))
                    self.shared.gratings_angle_update_requested.value = 0
                if self.shared.mask_radius_update_requested.value == 1:
                    self.myapp.mask_radius = self.shared.mask_radius.value
                    self.myapp.cardnode.setShaderInput("mask_radius", self.myapp.mask_radius)
                    self.shared.mask_radius_update_requested.value = 0
                self.second_time = time.time()
                self.myapp.cardnode.setShaderInput("phi",2*np.pi*self.myapp.temporal_frequency*(self.second_time-self.first_time))
                self.myapp.cardnode.show()
                self.myapp.taskMgr.step()

            if self.shared.stim_on.value == 1:


                if self.stimcode == 'LeftGrating':
                    self.myapp.cardnode.setShaderInput("stimcode", 0)
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value+5 < self.shared.numframes.value:
                        self.myapp.cardnode.setShaderInput("phi", 2 * np.pi * self.myapp.temporal_frequency * (
                        self.last_time - self.stim_start_time))
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()
                    stim_trial_count[0] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()
                elif self.stimcode == 'RightGrating':
                    self.myapp.cardnode.setShaderInput("stimcode", 1)
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value+5 < self.shared.numframes.value:
                        self.myapp.cardnode.setShaderInput("phi", 2 * np.pi * self.myapp.temporal_frequency * (
                            self.last_time - self.stim_start_time))
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()
                    stim_trial_count[1] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()
                elif self.stimcode == 'RivalrousLeftRightMovingGrating':
                    self.myapp.cardnode.setShaderInput("stimcode", 2)
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value+5 < self.shared.numframes.value:
                        self.myapp.cardnode.setShaderInput("phi", 2 * np.pi * self.myapp.temporal_frequency * (
                            self.last_time - self.stim_start_time))
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()
                    stim_trial_count[2] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()
                elif self.stimcode == 'RivalrousUpDownMovingGrating':
                    self.myapp.cardnode.setShaderInput("stimcode", 11)
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value + 5 < self.shared.numframes.value:
                        self.myapp.cardnode.setShaderInput("phi", 2 * np.pi * self.myapp.temporal_frequency * (
                                self.last_time - self.stim_start_time))
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()
                    stim_trial_count[3] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()

                elif self.stimcode == 'ContrastCoherent':
                    self.data_to_save = []
                    self.myapp.cardnode.setShaderInput("low_contrast", self.shared.low_contrast.value)
                    self.myapp.cardnode.setShaderInput("high_contrast", self.shared.high_contrast.value)
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value+5 <self.shared.numframes.value:

                        if (self.shared.framenum.value+2*self.shared.contrast_frameflip_interval.value)%(2*self.shared.contrast_frameflip_interval.value) <= 1:
                            print(self.shared.framenum.value, 'low contrast')
                            self.data_to_save.append({'framenum':self.shared.framenum.value,'grating_id':'low'})
                            self.myapp.cardnode.setShaderInput("stimcode",3)
                            self.myapp.taskMgr.step()
                        if (self.shared.framenum.value+self.shared.contrast_frameflip_interval.value)%(2*self.shared.contrast_frameflip_interval.value) <= 1:
                            print(self.shared.framenum.value, 'high contrast')
                            self.data_to_save.append({'framenum': self.shared.framenum.value, 'grating_id': 'high'})
                            self.myapp.cardnode.setShaderInput("stimcode",4)
                            self.myapp.taskMgr.step()
                        self.myapp.taskMgr.step()
                    path_to_file = os.path.join(
                        bytearray(self.shared.save_path[:self.shared.save_path_len.value]).decode(),
                        bytearray(self.shared.stim_type[:self.shared.stim_type_len.value]).decode() + '_trial_' + str(
                            stim_trial_count[4]) + '_cycles_' + str(
                            self.shared.numcycles.value) + '_freq_' + str(
                            self.shared.temporalfreq.value) + '_rot_' + str(
                            self.shared.gratings_angle.value) + '_brightness_' + str(
                            round(self.shared.gratings_brightness.value, 2)) + '_lowcontrast_' + str(
                            round(self.shared.low_contrast.value, 2)) + '_highcontrast_' + str(
                            round(self.shared.high_contrast.value, 2)) + '.p')
                    pickle.dump(self.data_to_save, open(path_to_file.encode("ISO-8859-1"), 'wb'))
                    stim_trial_count[4] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()

                elif self.stimcode == "ContrastRivalrousHighandLowFlicker":
                    left_right_dict = {'0': 'lefteye Low righteye High', '1': 'lefteye High righteye Low'}
                    left_right_flag = stim_trial_count[5] % 2
                    self.data_to_save = []
                    self.data_to_save.append(left_right_dict[str(int(left_right_flag))])
                    self.myapp.cardnode.setShaderInput("low_contrast", self.shared.low_contrast.value)
                    self.myapp.cardnode.setShaderInput("high_contrast", self.shared.high_contrast.value)
                    self.myapp.cardnode.setShaderInput("stimcode",5)
                    self.myapp.cardnode.setShaderInput("left_right_flag",left_right_flag)
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value + 5 < self.shared.numframes.value:
                        self.myapp.cardnode.setShaderInput("stimcode", 5)

                        if (self.shared.framenum.value + 2 * self.shared.contrast_frameflip_interval.value) % (
                                2 * self.shared.contrast_frameflip_interval.value) <= 1:
                            print(self.shared.framenum.value, 'low contrast flicker')
                            toss = rn.sample([-1, 1], 1)
                            self.data_to_save.append({'framenum': self.shared.framenum.value,'phase_change': toss[0]*self.myapp.phase_change,'grating_id': 'low'})
                            self.myapp.phase_low += np.deg2rad(toss[0]*self.myapp.phase_change)
                            self.myapp.phase_low = np.mod(self.myapp.phase_low, np.deg2rad(360))
                            self.myapp.cardnode.setShaderInput('phase_low', self.myapp.phase_low)
                            self.myapp.taskMgr.step()

                        if (self.shared.framenum.value + self.shared.contrast_frameflip_interval.value) % (
                                2 * self.shared.contrast_frameflip_interval.value) <= 1:
                            print(self.shared.framenum.value, 'high contrast flicker')
                            toss = rn.sample([-1, 1], 1)
                            self.data_to_save.append({'framenum': self.shared.framenum.value,
                                                      'phase_change': toss[0] * self.myapp.phase_change,
                                                      'grating_id': 'high'})
                            self.myapp.phase_high += np.deg2rad(toss[0]*self.myapp.phase_change)
                            self.myapp.phase_high = np.mod(self.myapp.phase_high, np.deg2rad(360))
                            self.myapp.cardnode.setShaderInput('phase_high', self.myapp.phase_high)
                            self.myapp.taskMgr.step()
                        self.myapp.cardnode.setShaderInput('phase_low', self.myapp.phase_low)
                        self.myapp.cardnode.setShaderInput('phase_high', self.myapp.phase_high)
                        self.myapp.taskMgr.step()
                    path_to_file = os.path.join(
                        bytearray(self.shared.save_path[:self.shared.save_path_len.value]).decode(),
                        bytearray(self.shared.stim_type[:self.shared.stim_type_len.value]).decode() + '_trial_' + str(stim_trial_count[5]) + '_cycles_' + str(
                            self.shared.numcycles.value) + '_freq_' + str(
                            self.shared.temporalfreq.value) + '_rot_' + str(
                            self.shared.gratings_angle.value) + '_brightness_' + str(
                            round(self.shared.gratings_brightness.value, 2)) + '_lowcontrast_' + str(
                            round(self.shared.low_contrast.value, 2)) + '_highcontrast_' + str(
                            round(self.shared.high_contrast.value, 2)) + '.p')
                    pickle.dump(self.data_to_save,open(path_to_file.encode("ISO-8859-1"),'wb'))
                    stim_trial_count[5] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()
                elif self.stimcode == "ContrastRivalrousNoFlicker":
                    self.myapp.cardnode.setShaderInput("low_contrast", self.shared.low_contrast.value)
                    self.myapp.cardnode.setShaderInput("high_contrast", self.shared.high_contrast.value)
                    self.myapp.cardnode.setShaderInput("stimcode", 5)
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value + 5 < self.shared.numframes.value:
                        self.myapp.taskMgr.step()
                    stim_trial_count[6] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()
                elif self.stimcode == "LowContrastFlicker":
                    self.data_to_save = []
                    self.myapp.cardnode.setShaderInput("low_contrast", self.shared.low_contrast.value)
                    self.myapp.cardnode.setShaderInput("stimcode", 7)
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value + 5 < self.shared.numframes.value:
                        if (self.shared.framenum.value % self.shared.contrast_frameflip_interval.value) <= 1:
                            toss = rn.sample([-1, 1], 1)
                            self.data_to_save.append({'framenum': self.shared.framenum.value,
                                                      'phase_change': toss[0] * self.myapp.phase_change})
                            self.myapp.phase_low += np.deg2rad(toss[0]*self.myapp.phase_change)
                            self.myapp.phase_low = np.mod(self.myapp.phase_low, np.deg2rad(360))
                            self.myapp.cardnode.setShaderInput('phase_low', self.myapp.phase_low)
                            self.myapp.taskMgr.step()
                        self.myapp.taskMgr.step()
                    path_to_file = os.path.join(
                        bytearray(self.shared.save_path[:self.shared.save_path_len.value]).decode(),
                        bytearray(self.shared.stim_type[:self.shared.stim_type_len.value]).decode() + '_trial_' + str(
                            stim_trial_count[7]) + '_cycles_' + str(
                            self.shared.numcycles.value) + '_freq_' + str(
                            self.shared.temporalfreq.value) + '_rot_' + str(
                            self.shared.gratings_angle.value) + '_brightness_' + str(
                            round(self.shared.gratings_brightness.value, 2)) + '_lowcontrast_' + str(
                            round(self.shared.low_contrast.value, 2)) + '_highcontrast_' + str(
                            round(self.shared.high_contrast.value, 2)) + '.p')
                    pickle.dump(self.data_to_save, open(path_to_file.encode("ISO-8859-1"), 'wb'))
                    stim_trial_count[7] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()
                elif self.stimcode == "HighContrastFlicker":
                    self.data_to_save = []
                    self.myapp.cardnode.setShaderInput("high_contrast", self.shared.high_contrast.value)
                    self.myapp.cardnode.setShaderInput("stimcode", 8)
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value + 5 < self.shared.numframes.value:
                        if (self.shared.framenum.value % self.shared.contrast_frameflip_interval.value) <= 1:
                            toss = rn.sample([-1, 1], 1)
                            self.data_to_save.append({'framenum': self.shared.framenum.value,
                                                      'phase_change': toss[0] * self.myapp.phase_change})
                            self.myapp.phase_high += np.deg2rad(toss[0]*self.myapp.phase_change)
                            self.myapp.phase_high = np.mod(self.myapp.phase_high, np.deg2rad(360))
                            self.myapp.cardnode.setShaderInput('phase_high', self.myapp.phase_high)
                            self.myapp.taskMgr.step()
                        self.myapp.taskMgr.step()
                    path_to_file = os.path.join(
                        bytearray(self.shared.save_path[:self.shared.save_path_len.value]).decode(),
                        bytearray(self.shared.stim_type[:self.shared.stim_type_len.value]).decode() + '_trial_' + str(
                            stim_trial_count[8]) + '_cycles_' + str(
                            self.shared.numcycles.value) + '_freq_' + str(
                            self.shared.temporalfreq.value) + '_rot_' + str(
                            self.shared.gratings_angle.value) + '_brightness_' + str(
                            round(self.shared.gratings_brightness.value, 2)) + '_lowcontrast_' + str(
                            round(self.shared.low_contrast.value, 2)) + '_highcontrast_' + str(
                            round(self.shared.high_contrast.value, 2)) + '.p')
                    pickle.dump(self.data_to_save, open(path_to_file.encode("ISO-8859-1"), 'wb'))
                    stim_trial_count[8] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()
                elif self.stimcode == "LowContrastCoherent":
                    self.myapp.cardnode.setShaderInput("low_contrast", self.shared.low_contrast.value)
                    self.myapp.cardnode.setShaderInput("stimcode", 3)
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value + 5 < self.shared.numframes.value:
                        self.myapp.taskMgr.step()
                    stim_trial_count[9] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()
                elif self.stimcode == 'HighContrastCoherent':
                    self.myapp.cardnode.setShaderInput("high_contrast", self.shared.high_contrast.value)
                    self.myapp.cardnode.setShaderInput("stimcode", 4)
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value + 5 < self.shared.numframes.value:
                        self.myapp.taskMgr.step()
                    stim_trial_count[10] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()
                elif self.stimcode == 'FlashSuppLowFlash':
                    # This will have a high contrast image in one eye, grey in the other, and then flash the low contrast image
                    self.myapp.cardnode.setShaderInput("stimcode", 9)
                    left_right_dict = {'1': 'lefteye High; righteye gray, then flash Low', '0': 'lefteye gray, then flash Low;_righteye High'}
                    left_right_flag = stim_trial_count[11] % 2
                    self.data_to_save = []
                    self.data_to_save.append(left_right_dict[str(int(left_right_flag))])
                    self.myapp.cardnode.setShaderInput("low_contrast", self.shared.low_contrast.value)
                    self.myapp.cardnode.setShaderInput("high_contrast", self.shared.high_contrast.value)
                    self.myapp.cardnode.setShaderInput("left_right_flag", left_right_flag)
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value + 5 < self.shared.numframes.value:
                        startframe = self.shared.framenum.value
                        if self.shared.framenum.value % self.shared.contrast_frameflip_interval.value <= 1:
                            print(self.shared.framenum.value, 'low contrast flash ON')
                            self.myapp.cardnode.setShaderInput("flash_flag",1)
                            self.data_to_save.append({'framenum': self.shared.framenum.value,'Flash': 'ON', 'grating_id': 'low'})
                            self.myapp.taskMgr.step()
                            while self.shared.framenum.value-startframe < self.shared.contrast_frameflip_interval.value/2:
                                self.myapp.cardnode.setShaderInput("flash_flag", 1)
                                self.myapp.taskMgr.step()
                            print(self.shared.framenum.value, 'low contrast flash OFF')
                            self.myapp.cardnode.setShaderInput("flash_flag", 0)
                            self.data_to_save.append(
                                {'framenum': self.shared.framenum.value, 'Flash': 'OFF', 'grating_id': 'low'})
                        self.myapp.cardnode.setShaderInput("flash_flag", 0)
                        self.myapp.taskMgr.step()
                    path_to_file = os.path.join(
                        bytearray(self.shared.save_path[:self.shared.save_path_len.value]).decode(),
                        bytearray(self.shared.stim_type[:self.shared.stim_type_len.value]).decode() + '_trial_' + str(stim_trial_count[11]) + '_cycles_' + str(
                            self.shared.numcycles.value) + '_freq_' + str(
                            self.shared.temporalfreq.value) + '_rot_' + str(
                            self.shared.gratings_angle.value) + '_brightness_' + str(
                            round(self.shared.gratings_brightness.value, 2)) + '_lowcontrast_' + str(
                            round(self.shared.low_contrast.value, 2)) + '_highcontrast_' + str(
                            round(self.shared.high_contrast.value, 2)) + '.p')
                    pickle.dump(self.data_to_save,open(path_to_file.encode("ISO-8859-1"),'wb'))
                    stim_trial_count[11] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()
                elif self.stimcode == 'FlashSuppHighFlash':
                    # This will have a low contrast image in one eye, grey in the other, and then flash the high contrast image
                    self.myapp.cardnode.setShaderInput("stimcode", 10)
                    left_right_dict = {'0': 'lefteye Low; righteye gray, then flash High',
                                       '1': 'lefteye gray, then flash High; righteye Low'}
                    left_right_flag = stim_trial_count[12] % 2
                    self.data_to_save = []
                    self.data_to_save.append(left_right_dict[str(int(left_right_flag))])
                    self.myapp.cardnode.setShaderInput("low_contrast", self.shared.low_contrast.value)
                    self.myapp.cardnode.setShaderInput("high_contrast", self.shared.high_contrast.value)
                    self.myapp.cardnode.setShaderInput("left_right_flag", left_right_flag)
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value + 5 < self.shared.numframes.value:
                        startframe = self.shared.framenum.value
                        if self.shared.framenum.value % self.shared.contrast_frameflip_interval.value <= 1:
                            print(self.shared.framenum.value, 'high contrast flash ON')
                            self.myapp.cardnode.setShaderInput("flash_flag",1)
                            self.data_to_save.append({'framenum': self.shared.framenum.value,'Flash': 'ON', 'grating_id': 'high'})
                            self.myapp.taskMgr.step()
                            while self.shared.framenum.value-startframe < self.shared.contrast_frameflip_interval.value/2:
                                self.myapp.cardnode.setShaderInput("flash_flag", 1)
                                self.myapp.taskMgr.step()
                            print(self.shared.framenum.value, 'high contrast flash OFF')
                            self.myapp.cardnode.setShaderInput("flash_flag", 0)
                            self.data_to_save.append(
                                {'framenum': self.shared.framenum.value, 'Flash': 'OFF', 'grating_id': 'high'})
                        self.myapp.taskMgr.step()
                    path_to_file = os.path.join(
                        bytearray(self.shared.save_path[:self.shared.save_path_len.value]).decode(),
                        bytearray(self.shared.stim_type[:self.shared.stim_type_len.value]).decode() + '_trial_' + str(
                            stim_trial_count[12]) + '_cycles_' + str(
                            self.shared.numcycles.value) + '_freq_' + str(
                            self.shared.temporalfreq.value) + '_rot_' + str(
                            self.shared.gratings_angle.value) + '_brightness_' + str(
                            round(self.shared.gratings_brightness.value, 2)) + '_lowcontrast_' + str(
                            round(self.shared.low_contrast.value, 2)) + '_highcontrast_' + str(
                            round(self.shared.high_contrast.value, 2)) + '.p')
                    pickle.dump(self.data_to_save, open(path_to_file.encode("ISO-8859-1"), 'wb'))
                    stim_trial_count[12] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()



                self.shared.stim_on.value = 0
                self.myapp.cardnode.hide()

            self.myapp.cardnode.hide()
            time.sleep(0.001)
            self.myapp.taskMgr.step()  # main panda loop, needed for redrawing, etc.

        self.myapp.destroy()
