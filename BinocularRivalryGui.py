if __name__ == "__main__":

    from shared import Shared
    import time
    shared = Shared()
    shared.start_threads()
    # time.sleep(10)
    from PyQt5 import QtCore, QtGui, uic, QtWidgets
    import sys
    import os
    import pyqtgraph as pg
    import numpy as np
    import pickle

    sys._excepthook = sys.excepthook


    def exception_hook(exctype, value, traceback):
        sys._excepthook(exctype, value, traceback)
        sys.exit(1)


    sys.excepthook = exception_hook

    class Main_Window(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
            self.shared = shared
            self.initUI()
        def initUI(self):
            # self.show()
            path = os.path.dirname(__file__)
            uic.loadUi(os.path.join(path, "BinocularRivalryBehaviourGui.ui"), self)

            ### enter directory to save and file name
            self.filepath_pushButton.clicked.connect(self.filepath_pushButton_clicked)
            self.file_path_lineEdit.textChanged.connect(self.file_path_lineEdit_textChanged)

            ### stimulus/stim params selector
            self.stim_comboBox.activated[str].connect(self.stim_comboBox_activated)
            self.startStim_pushButton.clicked.connect(self.startStim_pushButton_clicked)
            self.numframes_spinBox.valueChanged[int].connect(self.numframes_spinBox_value_changed)
            self.num_cycles_Slider.valueChanged[int].connect(self.num_cycles_Slider_value_changed)
            self.temporal_freq_doubleSpinbox.valueChanged[float].connect(self.temporal_freq_doubleSpinbox_value_changed)
            self.mask_radius_doubleSpinBox.valueChanged[float].connect(self.mask_radius_doubleSpinBox_valueChanged)
            self.show_stim_checkBox.stateChanged.connect(self.show_stim_checkBox_state_changed)
            self.grating_brightness_doubleSpinBox.valueChanged[float].connect(self.grating_brightness_doubleSpinBox_value_changed)
            self.grating_angle_doubleSpinBox.valueChanged[float].connect(self.grating_angle_doubleSpinBox_valueChanged)
            self.contrast_frameflip_interval_spinBox.valueChanged[int].connect(self.contrast_frameflip_interval_spinBox_value_changed)
            self.percent_low_contrast_spinBox.valueChanged[int].connect(self.percent_low_contrast_spinBox_value_changed)
            self.percent_high_contrast_spinBox.valueChanged[int].connect(self.percent_high_contrast_spinBox_value_changed)
            self.phase_change_spinBox.valueChanged[int].connect(self.phase_change_spinbox_value_changed)

            ### change exposure and gain
            self.exposure_spinBox.valueChanged[int].connect(self.exposure_spinBox_value_changed)
            self.gain_doubleSpinBox.valueChanged[float].connect(self.gain_doubleSpinBox_value_changed)
            self.gain1_doubleSpinBox.valueChanged[float].connect(self.gain1_doubleSpinBox_value_changed)

            self.pyqtgraph_image_item = pg.ImageItem(image=np.random.randint(0,255,(250, 250)))
            self.pyqtgraph_image_item1 = pg.ImageItem(image=np.random.randint(0, 255, (250, 250)))
            # self.graphicsView.setAspectLocked(True)
            self.pyqtgraph_image_item.setAutoDownsample(True)
            self.pyqtgraph_image_item1.setAutoDownsample(True)
            # self.pyqtgraph_image_item.setScaledMode(2)
            self.viewRect = self.graphicsView.viewRect()
            self.viewRect1 = self.graphicsView1.viewRect()
            print(self.viewRect)
            # self.pyqtgraph_image_item.setRect(self.viewRect)
            self.graphicsView.addItem(self.pyqtgraph_image_item)
            self.graphicsView1.addItem(self.pyqtgraph_image_item1)
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.updateData)
            self.timer.start(50)
            self.stim_dict = {'LeftGrating': 0, 'RightGrating': 1, 'RivalrousLeftRightMovingGrating': 2,
                         'RivalrousUpDownMovingGrating': 3,
                         'ContrastCoherent': 4, 'ContrastRivalrousHighandLowFlicker': 5,
                         'ContrastRivalrousNoFlicker': 6,
                         'LowContrastFlicker': 7, 'HighContrastFlicker': 8, 'LowContrastCoherent': 9,
                         'HighContrastCoherent': 10, 'FlashSuppLowFlash': 11, 'FlashSuppHighFlash': 12,
                         'FlashSuppLeftGrating': 13, 'FlashSuppRightGrating': 14}  # for accessing trial number from shared variable
            # updateData()
            # self.ImageItem.setImage(np.random.randint(0,255,(200,200)), autoLevels=False, levels=(0, 255))
        def filepath_pushButton_clicked(self):
            # full_path_to_module = os.path.abspath(QtWidgets.QFileDialog.getOpenFileName()[0])
            full_path_to_directory = os.path.abspath(QtWidgets.QFileDialog.getExistingDirectory(directory='c:\\Users\\Abhinav Grama\\Documents\\Abhi')).encode()
            self.shared.save_path_len.value = len(full_path_to_directory)
            self.shared.save_path[:self.shared.save_path_len.value]=full_path_to_directory
            self.file_path_lineEdit.setText(full_path_to_directory.decode())
        def file_path_lineEdit_textChanged(self):
            full_path_to_file = self.file_path_lineEdit.text().encode()
            self.shared.save_path_len.value = len(full_path_to_file)
            self.shared.save_path[:self.shared.save_path_len.value] = full_path_to_file

        # stim related functions
        def stim_comboBox_activated(self,text):
            text = text.encode()
            self.shared.stim_type_len.value = len(text)
            self.shared.stim_type[:self.shared.stim_type_len.value] = text
            self.shared.stim_type_update_requested.value = 1
        def show_stim_checkBox_state_changed(self, state):
            if state == QtCore.Qt.Checked:
                self.shared.show_stim.value = 1
            else:
                self.shared.show_stim.value = 0
        def startStim_pushButton_clicked(self):
            self.shared.start_cam.value = 1
            self.shared.start_cam1.value = 1
            self.startStim_pushButton.setStyleSheet('QPushButton{background-color: rgb(255, 43, 39);}')
        def temporal_freq_doubleSpinbox_value_changed(self,value):
            self.shared.temporalfreq.value = value
            self.shared.temporalfreq_update_requested.value = 1
        def num_cycles_Slider_value_changed(self,value):
            self.shared.numcycles.value = value
            self.gratings_cycles_label.setText("#Cycles in grating: %d"%value)
            self.shared.numcycles_update_requested.value = 1
        def mask_radius_doubleSpinBox_valueChanged(self,value):
            self.shared.mask_radius.value = value
            self.shared.mask_radius_update_requested.value = 1
        def numframes_spinBox_value_changed(self,value):
            self.shared.numframes.value = value
            self.exp_duration_label.setText("Exp duration: %.2f sec"%(self.shared.numframes.value/self.shared.framerate.value))
            # print(self.shared.numframes.value/self.shared.framerate.value)
        def grating_brightness_doubleSpinBox_value_changed(self,value):
            self.shared.gratings_brightness.value = value
            self.shared.gratings_brightness_update_requested.value = 1
        def grating_angle_doubleSpinBox_valueChanged(self,value):
            self.shared.gratings_angle.value = value

            self.shared.gratings_angle_update_requested.value = 1
        def contrast_frameflip_interval_spinBox_value_changed(self,value):
            self.shared.contrast_frameflip_interval.value = value
            self.shared.contrast_frameflip_interval_update_requested.value = 1

        def percent_low_contrast_spinBox_value_changed(self,value):
            self.shared.low_contrast.value = value/100.0
            self.shared.low_contrast_update_requested.value = 1

        def percent_high_contrast_spinBox_value_changed(self,value):
            self.shared.high_contrast.value = value/100.0
            self.shared.high_contrast_update_requested.value = 1
        def phase_change_spinbox_value_changed(self,value):
            self.shared.phase_change.value = value
            self.shared.phase_change_update_requested.value = 1

        #camera property functions
        def exposure_spinBox_value_changed(self,value):
            self.framerate_label.setText('Frame rate = %.2f Hz'%self.shared.framerate.value)
            self.shared.camera_exposure.value = value
            self.shared.camera_exposure_update_requested.value = 1

        def gain_doubleSpinBox_value_changed(self,value):
            self.shared.camera_gain.value = value
            self.shared.camera_gain_update_requested.value = 1
        def gain1_doubleSpinBox_value_changed(self, value):
            self.shared.camera1_gain.value = value
            self.shared.camera1_gain_update_requested.value = 1

        # main GUI loop
        def updateData(self):
            stim_trial_count = np.ctypeslib.as_array(self.shared.stim_trial_count)
            # print(stim_trial_count)
            frame = np.ctypeslib.as_array(self.shared.frame)[:self.shared.frame_len.value]
            frame1 = np.ctypeslib.as_array(self.shared.frame1)[:self.shared.frame_len.value]
            self.numframes_label.setText("#Frames done: %d"%self.shared.framenum.value)
            stim_type = bytearray(self.shared.stim_type[:self.shared.stim_type_len.value]).decode()
            if len(frame)>0:
                frame = frame.reshape((self.shared.frame_height.value,self.shared.frame_width.value)).astype(np.uint8)
                frame1 = frame1.reshape((self.shared.frame_height.value, self.shared.frame_width.value)).astype(np.uint8)
                # frame=(255*(frame/4096.0)).astype(np.uint8)
                self.pyqtgraph_image_item.setImage(frame.T,autoLevels=False,autoDownsample=True)
                self.pyqtgraph_image_item.setRect(self.viewRect)
                self.pyqtgraph_image_item1.setImage(frame1.T, autoLevels=False, autoDownsample=True)
                self.pyqtgraph_image_item1.setRect(self.viewRect1)

            if len(stim_type)>0:
                self.stim_trial_label.setText(stim_type + ' ' + str(stim_trial_count[self.stim_dict[stim_type]]-1))
            if self.shared.start_cam.value ==0:
                self.startStim_pushButton.setStyleSheet('QPushButton{background-color: rgb(43, 255, 39);}')
        #close window
        def closeEvent(self, a0: QtGui.QCloseEvent):
            self.shared.main_program_still_running.value = 0
            self.close()
    app = QtWidgets.QApplication(sys.argv)

    try:
        main_window = Main_Window()
        main_window.show()
        app.exec_()
    except:
        shared.main_program_still_running.value = 0
        print("WTFFF")



