import sys
from pathlib import Path

import yaml
from PyQt6.QtWidgets import QApplication
from GUI.camera_window import UiMainWindow


def main():
    config_path = Path('config.yml')
    with open(config_path, 'r') as f:
        cfg = yaml.safe_load(f)
    if not cfg['data_path'] or not Path(cfg['data_path']).is_dir() or str(Path(cfg['data_path'])) == ".":
        data_path = Path.cwd() / "data"
        data_path.mkdir(exist_ok=True)
        cfg['data_path'] = str(data_path)
        with open(config_path, 'w') as f:
            yaml.safe_dump(cfg, f, sort_keys=False)
    app = QApplication(sys.argv)
    main_window = UiMainWindow(cfg)
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()


