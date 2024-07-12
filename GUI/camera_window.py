from pathlib import Path

import numpy as np
import yaml
from PyQt6 import QtCore, QtGui, QtWidgets
import cv2
from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage

from GUI.control_panel import ControlPanel
from utils.data_handle import get_path


class UiMainWindow(QtWidgets.QMainWindow):

    def __init__(self, config: dict):
        super().__init__()
        self._is_in_session = False
        self._is_recording = False
        self._frames_buffer = []
        self.delay = 3
        self.current_video = 0
        self.config = config
        self.central_widget = QtWidgets.QFrame(self)
        self._timer_counter = self.delay
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.handle_timer)
        self.timer.setInterval(1000)
        self.setWindowTitle("Sign Language Collector")
        self.setMinimumSize(800, 600)
        video_size = self.config.get('video_size', (640, 480))
        camera_id = self.config.get('camera_id', 0)
        fps = self.config.get('fps', 30)
        self.video_capture_thread = CaptureThread(camera_id=camera_id, video_size=video_size, fps=fps)
        self.video_capture_thread.send_frame.connect(self.receive_frame)

        self.frame = QtWidgets.QLabel(self)
        self.frame.setStyleSheet("border: 3px solid rgb(0, 255, 0); border-radius: 7px;")
        self.control_panel = ControlPanel(self.config, self)
        self.control_panel.session_record_button.clicked.connect(self.toggle_recording_session)
        self.control_panel.path_button.clicked.connect(self.change_path)

        self.central_v_layout = QtWidgets.QVBoxLayout()
        self.central_v_layout.addWidget(self.frame)
        self.central_v_layout.addStretch(1)

        self.central_h_layout = QtWidgets.QHBoxLayout()
        self.central_h_layout.addWidget(self.control_panel)
        self.central_h_layout.addLayout(self.central_v_layout)
        self.central_h_layout.addStretch(1)

        self.central_widget.setLayout(self.central_h_layout)
        self.setCentralWidget(self.central_widget)

        self.counter_label = QtWidgets.QLabel(self)
        self.counter_label.setStyleSheet("background-color: rgba(255, 255, 255, 0.05); color: red; font-size: 70px; border-radius: 5px")
        self.counter_label.setText("3")
        self.counter_label.adjustSize()
        self.counter_label.setVisible(False)

        self.resize(video_size[0] + self.control_panel.width() + 30, video_size[1])
        self.video_capture_thread.start()

        self.show()
        print(self.frame.width(), self.frame.height())
        self.counter_label.move(self.frame.x() + int(video_size[0]/2), self.frame.y())

    def toggle_recording_session(self):
        self.is_in_session = not self.is_in_session

    def change_path(self):
        path = Path(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.config.update({'data_path': str(path)})
        self.control_panel.set_path(path)
        with open("config.yml", "w") as f:
            yaml.safe_dump(self.config, f, sort_keys=False)

    def handle_timer(self):
        self._timer_counter -= 1
        self.counter_label.setText(f"{self._timer_counter}")
        if self._timer_counter == 0:
            self._timer_counter = self.delay
            self.timer.stop()
            self.frame.setStyleSheet("border: 3px solid rgb(255, 0, 0); border-radius: 7px;")
            self.counter_label.setVisible(False)
            self.counter_label.setText("3")
            self._timer_counter = self.delay
            self._is_recording = True

    def save_video(self):
        self._is_recording = False
        video_path, exists = get_path(self.config['data_path'], self.control_panel.select_words_cbox.currentText(),
                                      str(self.current_video))

        fourcc = cv2.VideoWriter.fourcc(*'mp4v')
        width, height = self.config.get('video_size', (640, 480))
        writer = cv2.VideoWriter(video_path, fourcc, self.config.get('fps', 30),
                                 (width, height), isColor=True)

        for frame in self._frames_buffer:
            writer.write(frame)
        writer.release()
        self.current_video += 1
        if self.current_video <= self.config.get('videos_per_word') - 1:
            self.is_in_session = True
        else:
            self.is_in_session = False
            self.current_video = 0
        self._frames_buffer = []






    @property
    def is_in_session(self):
        return self._is_in_session

    @is_in_session.setter
    def is_in_session(self, nv: bool):
        self._is_in_session = nv

        if self.is_in_session:
            self.frame.setStyleSheet("border: 3px solid rgb(255, 255, 0); border-radius: 7px;")
            self.control_panel.session_record_button.setText('Stop\nRecord session')
            self.counter_label.setVisible(True)
            self.timer.start()
        else:
            self.frame.setStyleSheet("border: 3px solid rgb(0, 255, 0); border-radius: 7px;")
            self.control_panel.session_record_button.setText('Start\nRecord session')
            self.timer.stop()
            self.counter_label.setVisible(False)

    @pyqtSlot(np.ndarray)
    def receive_frame(self, *args):
        frame = args[0]
        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_BGR888)
        if self._is_recording:
            self._frames_buffer.append(frame)
            if len(self._frames_buffer) >= self.config['frames_per_vid']:
                self.save_video()
        self.frame.setPixmap(QtGui.QPixmap(image))

    def closeEvent(self, event):
        self.video_capture_thread.video_capture.release()
        self.video_capture_thread.running = False
        super().closeEvent(event)


class CaptureThread(QtCore.QThread):
    send_frame = pyqtSignal(np.ndarray)

    def __init__(self, camera_id: int, video_size: tuple = (640, 480), fps: int = 30, **kwargs):
        super().__init__(**kwargs)
        self.running = True
        self.video_capture = cv2.VideoCapture(camera_id)
        print(self.video_capture.get(cv2.CAP_PROP_FPS))
        self.video_capture.set(cv2.CAP_PROP_FPS, fps)
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, video_size[0])
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, video_size[1])

    def run(self) -> None:
        while self.running:
            if not self.video_capture.isOpened():
                break
            ret, frame = self.video_capture.read()
            if not ret:
                print("Video capture failed")
                break
            self.send_frame.emit(frame)


    def start_capture(self):
        return self.video_capture.isOpened()



