import sys
from pathlib import Path

import yaml
from PyQt6.QtWidgets import QApplication
from GUI.camera_window import UiMainWindow
from utils.config_gen import generate_config


def main():
    config_path = Path('config.yml')
    if not config_path.exists():
        cfg = generate_config(Path(Path.cwd(), 'data'))
        cfg = yaml.safe_load(cfg)
        with open('config.yml', 'w', encoding="UTF-8") as outfile:
            yaml.dump(cfg, outfile, sort_keys=False)
    else:
        with open(config_path, 'r', encoding="UTF-8") as f:
            cfg = yaml.safe_load(f)
    if not cfg['data_path'] or not Path(cfg['data_path']).is_dir() or str(Path(cfg['data_path'])) == ".":
        data_path = Path.cwd() / "data"
        data_path.mkdir(exist_ok=True)
        cfg['data_path'] = str(data_path)
        with open(config_path, 'w', encoding="UTF-8") as f:
            yaml.safe_dump(cfg, f, sort_keys=False)
    app = QApplication(sys.argv)
    main_window = UiMainWindow(cfg)
    main_window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()


