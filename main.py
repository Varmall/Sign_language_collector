import sys
from pathlib import Path

import yaml
from PyQt6.QtWidgets import QApplication
from GUI.camera_window import UiMainWindow


def main():
    config_path = Path('config.yml')
    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f)
        print(cfg)
    app = QApplication(sys.argv)
    main_window = UiMainWindow(cfg)
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()


