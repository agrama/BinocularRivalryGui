from multiprocessing import Process, Value, Array, Queue, sharedctypes
from rivalrous_gratings_shader import MyApp
import time
import numpy as np



class StimulusModule(Process):
    def __init__(self, shared):
        Process.__init__(self)

        self.shared = shared

    def run(self):

        self.myapp = MyApp(self.shared)
        stim_trial_count = np.zeros((3,1),dtype=np.uint)
        self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()
        self.thetas = np.arange(0,3*np.pi/4+0.1, np.pi/4) # orientations to flash the flicker stim
        while self.shared.main_program_still_running.value == 1:
            if self.shared.stim_type_update_requested.value ==1:
                self.stimcode = bytearray(self.shared.stim_type[:self.shared.stim_type_len.value]).decode()
                self.shared.stim_type_update_requested.value = 0
            if self.shared.temporalfreq_update_requested.value == 1:
                self.myapp.temporal_frequency = self.shared.temporalfreq.value
                self.shared.temporalfreq_update_requested.value = 0
            if self.shared.numcycles_update_requested.value == 1:
                self.myapp.cycles = self.shared.numcycles.value
                self.myapp.cardnode.setShaderInput("cycles", self.myapp.cycles)
                self.shared.numcycles_update_requested.value = 0
            self.first_time = time.time()
            while self.shared.show_stim.value & self.shared.main_program_still_running.value:
                if self.shared.stim_type_update_requested.value == 1:
                    self.stimcode = bytearray(self.shared.stim_type[:self.shared.stim_type_len.value]).decode()
                    if self.stimcode == 'LeftGrating':
                        self.myapp.cardnode.setShaderInput("stimcode", 0)
                    elif self.stimcode == 'RightGrating':
                        self.myapp.cardnode.setShaderInput("stimcode", 1)
                    elif self.stimcode == 'Rivalrous':
                        self.myapp.cardnode.setShaderInput("stimcode", 2)
                    self.shared.stim_type_update_requested.value = 0

                if self.shared.temporalfreq_update_requested.value == 1:
                    self.myapp.temporal_frequency = self.shared.temporalfreq.value
                    self.shared.temporalfreq_update_requested.value = 0

                if self.shared.numcycles_update_requested.value == 1:
                    self.myapp.cycles = self.shared.numcycles.value
                    self.myapp.cardnode.setShaderInput("cycles", self.myapp.cycles)
                    self.shared.numcycles_update_requested.value = 0
                self.second_time = time.time()
                self.myapp.cardnode.setShaderInput("phi",2*np.pi*self.myapp.temporal_frequency*(self.second_time-self.first_time))
                self.myapp.cardnode.show()
                self.myapp.taskMgr.step()

            if self.shared.stim_on.value == 1:


                if self.stimcode == 'LeftGrating':
                    self.myapp.cardnode.setShaderInput("stimcode", 0)
                    stim_trial_count[0] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value+1 < self.shared.numframes.value:
                        self.myapp.cardnode.setShaderInput("phi", 2 * np.pi * self.myapp.temporal_frequency * (
                        self.last_time - self.stim_start_time))
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()
                elif self.stimcode == 'RightGrating':
                    self.myapp.cardnode.setShaderInput("stimcode", 1)
                    stim_trial_count[1] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value+1 < self.shared.numframes.value:
                        self.myapp.cardnode.setShaderInput("phi", 2 * np.pi * self.myapp.temporal_frequency * (
                            self.last_time - self.stim_start_time))
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()
                elif self.stimcode == 'Rivalrous':
                    self.myapp.cardnode.setShaderInput("stimcode", 2)
                    stim_trial_count[2] += 1
                    self.shared.stim_trial_count[:len(stim_trial_count)] = stim_trial_count.flatten()
                    self.stim_start_time = time.time()
                    self.last_time = time.time()
                    self.myapp.cardnode.show()
                    while self.shared.framenum.value+1 < self.shared.numframes.value:
                        self.myapp.cardnode.setShaderInput("phi", 2 * np.pi * self.myapp.temporal_frequency * (
                            self.last_time - self.stim_start_time))
                        self.myapp.taskMgr.step()
                        self.last_time = time.time()
                self.shared.stim_on.value = 0
                self.myapp.cardnode.hide()
            self.myapp.cardnode.hide()
            time.sleep(0.001)
            self.myapp.taskMgr.step()  # main panda loop, needed for redrawing, etc.

        self.myapp.destroy()
