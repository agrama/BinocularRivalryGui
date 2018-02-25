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
            self.show_stim_checkBox.stateChanged.connect(self.show_stim_checkBox_state_changed)



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
            # updateData()
            # self.ImageItem.setImage(np.random.randint(0,255,(200,200)), autoLevels=False, levels=(0, 255))
        def filepath_pushButton_clicked(self):
            # full_path_to_module = os.path.abspath(QtWidgets.QFileDialog.getOpenFileName()[0])
            full_path_to_directory = os.path.abspath(QtWidgets.QFileDialog.getExistingDirectory(directory='c:\\Users\\Cox-Resscope\\Desktop\\Abhi')).encode()
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
            self.shared.start_exp.value = 1
            self.startStim_pushButton.setStyleSheet('QPushButton{background-color: rgb(255, 43, 39);}')
        def temporal_freq_doubleSpinbox_value_changed(self,value):
            self.shared.temporalfreq.value = value
            self.shared.temporalfreq_update_requested.value = 1
        def num_cycles_Slider_value_changed(self,value):
            self.shared.numcycles.value = value
            self.gratings_cycles_label.setText("#Cycles in grating: %d"%value)
            self.shared.numcycles_update_requested.value = 1
        def numframes_spinBox_value_changed(self,value):
            self.shared.numframes.value = value
            self.exp_duration_label.setText("Exp duration: %.2f sec"%(self.shared.numframes.value/self.shared.framerate.value))
            # print(self.shared.numframes.value/self.shared.framerate.value)
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
            if len(frame)>0:
                frame = frame.reshape((self.shared.frame_height.value,self.shared.frame_width.value)).astype(np.uint8)
                frame1 = frame1.reshape((self.shared.frame_height.value, self.shared.frame_width.value)).astype(np.uint8)
                # frame=(255*(frame/4096.0)).astype(np.uint8)
                self.pyqtgraph_image_item.setImage(frame.T,autoLevels=False,autoDownsample=True)
                self.pyqtgraph_image_item.setRect(self.viewRect)
                self.pyqtgraph_image_item1.setImage(frame1.T, autoLevels=False, autoDownsample=True)
                self.pyqtgraph_image_item1.setRect(self.viewRect1)
            self.stim_trial_label.setText('LeftGrating: %d RightGrating: %d Rivalrous: %d'
                                          % (stim_trial_count[0], stim_trial_count[1]
                                             , stim_trial_count[2]))
            if self.shared.start_exp.value ==0:
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



