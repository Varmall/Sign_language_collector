import os
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED


def get_path(dir_path: Path | str, video_name: str) -> tuple[Path, bool]:
    if isinstance(dir_path, str):
        dir_path = Path(dir_path)
    save_path: Path = dir_path / video_name
    if save_path.suffix.lower() != '.mp4':
        save_path = save_path.with_suffix('.mp4')
    exists = True if save_path.exists() else False
    return save_path, exists


def create_dir(data_path: Path | str, word: str) -> Path:
    """Creates a directory for both data_path if it does not exist, and for word with the timestamp in the word dir
    name.
    :param data_path: Path to the data directory
    :param word: Folder name (should be a word)
    :return: Path to the created directory"""
    if isinstance(data_path, str):
        data_path = Path(data_path)
    Path.mkdir(data_path, exist_ok=True)
    date_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    dir_path = data_path / f"{word}_{date_time}"
    dir_path.mkdir(exist_ok=True)
    return data_path / f"{word}_{date_time}"


def zip_data(data_path: Path | str, zip_name: str) -> Path:
    archive_path = Path(data_path, zip_name)
    with ZipFile(archive_path, 'w', ZIP_DEFLATED) as zip_file:
        dirs_to_compress = [my_dir for my_dir in os.listdir(str(data_path))
                            if os.path.isdir(os.path.join(data_path, my_dir))]
        for my_dir in dirs_to_compress:
            zip_file.write(os.path.join(data_path, my_dir), my_dir)
            videos_list = os.listdir(os.path.join(data_path, my_dir))
            for video in videos_list:
                zip_file.write(os.path.join(data_path, my_dir, video), arcname=os.path.join(my_dir, video))
    return archive_path
