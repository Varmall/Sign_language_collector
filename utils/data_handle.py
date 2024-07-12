from pathlib import Path


def get_path(data_path: Path | str, word: str, video_name: str):
    if isinstance(data_path, str):
        data_path = Path(data_path)
    Path.mkdir(data_path, exist_ok=True)
    Path.mkdir(data_path/word, exist_ok=True)
    save_path: Path = data_path / word / video_name
    if save_path.suffix.lower() != '.mp4':
        save_path = save_path.with_suffix('.mp4')
    exists = True if save_path.exists() else False
    return save_path, exists



