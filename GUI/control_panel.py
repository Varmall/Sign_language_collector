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
        self.path_button = QtWidgets.QPushButton('Change save path')
        self.select_words_label = QtWidgets.QLabel('Select Word:')
        self.select_words_cbox = QtWidgets.QComboBox()
        self.select_words_cbox.addItems(config['words'])

        # Layout stuff
        self.v_layout = QtWidgets.QVBoxLayout()
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setSpacing(1)

        self.v_layout.addWidget(self.current_path_label)
        self.v_layout.addWidget(self.path_button)
        self.v_layout.addWidget(self.select_words_label)
        self.v_layout.addWidget(self.select_words_cbox)
        self.v_layout.addWidget(self.session_record_button)
        self.v_layout.addStretch(1)
        self.setLayout(self.v_layout)

    def set_path(self, path: Path):
        self.current_path_label.setText(f"Save Path: {path}")
        self.current_path_label.setToolTip(f"{path.absolute()}")

