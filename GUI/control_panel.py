from PyQt6 import QtWidgets
from pathlib import Path


class ControlPanel(QtWidgets.QFrame):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent=parent)
        self.config = config
        self.setFixedWidth(150)
        self.session_record_button = QtWidgets.QPushButton('Start\nRecord session')

        self.current_path_label = QtWidgets.QLabel()
        self.set_path(Path(config['data_path']))
        self.current_path_label.setWordWrap(True)
        self.current_path_label.setStyleSheet("QLabel:hover{background-color:rgb(210, 210, 210);}")
        self.path_button = QtWidgets.QPushButton('Change save path')
        self.select_words_label = QtWidgets.QLabel('Select Word:')
        self.select_words_cbox = QtWidgets.QComboBox()
        self.select_words_cbox.addItems(config['words'])

        self.num_vid_layout = QtWidgets.QHBoxLayout()
        self.num_vid_label = QtWidgets.QLabel("Number of Videos:")
        self.num_vid_cbox = QtWidgets.QComboBox()
        self.num_vid_cbox.addItems([str(x) for x in range(10, 51)])
        self.num_vid_cbox.setCurrentText(str(config.get("videos_per_word", 10)))
        self.num_vid_layout.addWidget(self.num_vid_label)
        self.num_vid_layout.addStretch(1)
        self.num_vid_layout.addWidget(self.num_vid_cbox)

        self.num_frames_layout = QtWidgets.QHBoxLayout()
        self.num_frames_label = QtWidgets.QLabel("Frames per video:")
        self.num_frames_cbox = QtWidgets.QComboBox()
        self.num_frames_cbox.addItems([str(x) for x in range(30, 400, 5)])
        self.num_frames_cbox.setCurrentText(str(config.get("frames_per_vid", 40)))
        self.num_frames_layout.addWidget(self.num_frames_label)
        self.num_frames_layout.addStretch(1)
        self.num_frames_layout.addWidget(self.num_frames_cbox)

        self.open_zip_location_ck_box = QtWidgets.QCheckBox("Open Zip Location", self)
        self.open_zip_location_ck_box.setChecked(True)
        self.compress_button = QtWidgets.QPushButton('Zip Data', self)

        # Layout stuff
        self.v_layout = QtWidgets.QVBoxLayout()
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(1)

        self.v_layout.addWidget(self.current_path_label)
        self.v_layout.addWidget(self.path_button)
        self.v_layout.addWidget(self.select_words_label)
        self.v_layout.addWidget(self.select_words_cbox)
        self.v_layout.addLayout(self.num_vid_layout)
        self.v_layout.addLayout(self.num_frames_layout)
        self.v_layout.addWidget(self.session_record_button)
        self.v_layout.addStretch(1)
        self.v_layout.addWidget(self.open_zip_location_ck_box)
        self.v_layout.addWidget(self.compress_button)
        self.v_layout.addStretch(19)
        self.setLayout(self.v_layout)

    def set_path(self, path: Path):
        self.current_path_label.setText(f"Save Path: {path.relative_to(Path.cwd())}")
        self.current_path_label.setToolTip(f"{path.absolute()}")

