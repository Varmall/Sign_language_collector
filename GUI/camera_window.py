import platform
import subprocess
from pathlib import Path

import numpy as np
import yaml
from PyQt6 import QtCore, QtGui, QtWidgets
import cv2
from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThreadPool
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtMultimedia import QMediaPlayer
from threading import Thread

from GUI.control_panel import ControlPanel
from utils.data_handle import get_path, create_dir, zip_data


class UiMainWindow(QtWidgets.QMainWindow):

    def __init__(self, config: dict):
        super().__init__()
        self._current_video = None
        self._current_word_dir: Path | None = None
        self._video_frame = (0, 0)
        self._is_in_session = False
        self._is_recording = False
        self._frames_buffer = []
        self.loaded_example_videos = {}
        self.delay = 3
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

        self.save_worker = None

        self.frame = QtWidgets.QLabel(self)
        self.frame.setStyleSheet("border: 3px solid rgb(0, 255, 0); border-radius: 7px;")
        self.control_panel = ControlPanel(self.config, self)
        self.control_panel.session_record_button.clicked.connect(self.toggle_recording_session)
        self.control_panel.path_button.clicked.connect(self.change_path)
        self.control_panel.select_words_cbox.currentTextChanged.connect(self.reset_example)
        self.control_panel.compress_button.clicked.connect(self.handle_zip_data)

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

        self.video_example_display = QtWidgets.QLabel(parent=self.frame)
        self.video_example_display.setStyleSheet("background-color: rgb(200, 200, 0);")
        self.video_example_display.setFixedSize(480, 270)

        self.current_video_label = QtWidgets.QLabel(self.frame)
        self.current_video_label.setText(f"Recorded videos: {self.current_video} / {self.control_panel.num_vid_cbox.currentText()}")
        self.current_video_label.setStyleSheet("background-color: rgba(100, 100, 100, 0.55); color: white; border:0px; border-radius: 3px;")
        self.current_video_label.move(4, 4)
        self.current_video = 0
        self.current_video_label.adjustSize()

        self.counter_label.move(self.frame.x() + int(video_size[0]/2), self.frame.y() + 8)
        self.video_example_display.move(self.frame.x(), self.current_video_label.height() + 5)
        self.load_example_videos(Path("examples/yes"), "yes")

        self.example_timer = QtCore.QTimer()
        self.example_timer.setInterval(int(1000 / 30))
        self.example_timer.timeout.connect(self.handle_example_timer)
        self.example_timer.start()

    def toggle_recording_session(self) -> None:
        self.is_in_session = not self.is_in_session
        if self.is_in_session:
            self._current_word_dir = create_dir(self.config['data_path'],
                                                self.control_panel.select_words_cbox.currentText())
            self.current_video = 0

    def change_path(self) -> None:
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if not path:
            return
        path = Path(path)
        self.config.update({'data_path': str(path)})
        self.control_panel.set_path(path)
        with open("config.yml", "w") as f:
            yaml.safe_dump(self.config, f, sort_keys=False)

    def handle_timer(self) -> None:
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

    def handle_example_timer(self) -> None:
        current_word = self.control_panel.select_words_cbox.currentText()
        if current_word not in self.loaded_example_videos:
            self.load_example_videos(Path(f"examples/{current_word}"), current_word)
        if not self.loaded_example_videos[current_word]:
            self.video_example_display.setText("Video not found")
            return
        current_video = self.loaded_example_videos[current_word][self._video_frame[0]]
        frame = current_video[self._video_frame[1]]
        self.video_example_display.setPixmap(QPixmap(frame))
        self._video_frame = (self._video_frame[0], self._video_frame[1]+1)
        if self._video_frame[1] == len(current_video):
            self._video_frame = (self._video_frame[0]+1, 0)
        if self._video_frame[0] == len(self.loaded_example_videos[current_word]):
            self._video_frame = (0, 0)

    def reset_example(self) -> None:
        self._video_frame = (0, 0)

    def load_example_videos(self, dir_path: Path, word: str) -> None:
        if word in self.loaded_example_videos:
            return
        video_paths = dir_path.glob('*.mp4')
        self.loaded_example_videos[word] = {}
        for i, video_path in enumerate(video_paths):
            self.loaded_example_videos[word][i] = []
            cap = cv2.VideoCapture(str(video_path))
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    frame = cv2.resize(frame, (480, 270))
                    frame = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_BGR888)
                    self.loaded_example_videos[word][i].append(frame)
                else:
                    cap.release()

    def save_video(self) -> None:
        self._is_recording = False
        video_path, exists = get_path(self._current_word_dir, str(self.current_video))
        self.save_worker = Thread(target=lambda: worker_save_vid(self.config.copy(), str(video_path), self._frames_buffer))
        self.save_worker.start()

        self.current_video += 1
        if self.current_video <= int(self.control_panel.num_vid_cbox.currentText()) - 1:
            self.is_in_session = True
        else:
            self.is_in_session = False
            self.current_video = 0
        self._frames_buffer = []

    def handle_zip_data(self):
        archive_path = zip_data(self.config['data_path'], "data.zip")
        if not self.control_panel.open_zip_location_ck_box.isChecked():
            return
        if platform.system() == "Windows":
            subprocess.Popen(f'explorer /select,{archive_path}')
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", archive_path])
        else:
            subprocess.Popen(["xdg-open", archive_path])

    @property
    def is_in_session(self):
        return self._is_in_session

    @is_in_session.setter
    def is_in_session(self, nv: bool):
        self._is_in_session = nv

        if self.is_in_session:
            self.frame.setStyleSheet("border: 3px solid rgb(255, 255, 0); border-radius: 7px;")
            self.control_panel.session_record_button.setText('Stop\nRecord session')
            self.control_panel.compress_button.setEnabled(False)
            self.control_panel.select_words_cbox.setEnabled(False)
            self.control_panel.num_vid_cbox.setEnabled(False)
            self.control_panel.num_frames_cbox.setEnabled(False)
            self.control_panel.path_button.setEnabled(False)
            self.control_panel.open_zip_location_ck_box.setEnabled(False)
            self.counter_label.setVisible(True)
            self.timer.start()
        else:
            self.frame.setStyleSheet("border: 3px solid rgb(0, 255, 0); border-radius: 7px;")
            self.control_panel.session_record_button.setText('Start\nRecord session')
            self.control_panel.compress_button.setEnabled(True)
            self.control_panel.select_words_cbox.setEnabled(True)
            self.control_panel.num_vid_cbox.setEnabled(True)
            self.control_panel.num_frames_cbox.setEnabled(True)
            self.control_panel.path_button.setEnabled(True)
            self.control_panel.open_zip_location_ck_box.setEnabled(True)
            self.timer.stop()
            self.counter_label.setVisible(False)

    @property
    def current_video(self):
        return self._current_video

    @current_video.setter
    def current_video(self, nv: int):
        self._current_video = nv
        self.current_video_label.setText(f"Recorded videos: {self.current_video} / {self.control_panel.num_vid_cbox.currentText()}")
        self.current_video_label.adjustSize()

    @pyqtSlot(QImage, np.ndarray)
    def receive_frame(self, *args) -> None:
        image, frame = args[0], args[1]
        if self._is_recording:
            self.control_panel.session_record_button.setEnabled(False)
            self._frames_buffer.append(frame)
            if len(self._frames_buffer) >= int(self.control_panel.num_frames_cbox.currentText()):
                self.save_video()
                self.control_panel.session_record_button.setEnabled(True)
        self.frame.setPixmap(QtGui.QPixmap(image))

    def closeEvent(self, event):
        self.video_capture_thread.video_capture.release()
        self.video_capture_thread.running = False
        super().closeEvent(event)


def worker_save_vid(config: dict, video_path: str, frames_buffer: list) -> None:
    fourcc = cv2.VideoWriter.fourcc(*'mp4v')
    width, height = config.get('video_size', (640, 480))
    writer = cv2.VideoWriter(video_path, fourcc, config.get('fps', 30),
                             (width, height), isColor=True)

    for frame in frames_buffer:
        frame = cv2.resize(frame, (width, height))
        writer.write(frame)
    writer.release()


class CaptureThread(QtCore.QThread):
    send_frame = pyqtSignal(QImage, np.ndarray)

    def __init__(self, camera_id: int, video_size: tuple = (640, 480), fps: int = 30, **kwargs):
        super().__init__(**kwargs)
        self.running = True
        self.video_capture = cv2.VideoCapture(camera_id)
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
            frame = cv2.flip(frame, 1)
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format.Format_BGR888)
            self.send_frame.emit(image, frame)
            # self.msleep(20)

    def start_capture(self):
        return self.video_capture.isOpened()



