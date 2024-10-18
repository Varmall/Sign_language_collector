from pathlib import Path


def generate_config(data_path: str | Path) -> str:
    config: str = ""
    words = ["'yes'", "'no'", 'like', 'finish', 'happy', 'nice', 'eat', 'teacher', 'sit', 'deaf']
    words_conf = f"words:\n"
    for word in words:
        words_conf += f"- {word}\n"
    data_path = f"data_path: {data_path}\n"
    camera_id = "camera_id: 0\n"
    video_size = "video_size:\n- 1600\n- 900\n"
    fps = "fps: 30\n"
    frames_per_vid = "frames_per_vid: 40\n"
    videos_per_word = "videos_per_word: 10\n"

    config += words_conf
    config += data_path
    config += camera_id
    config += video_size
    config += fps
    config += frames_per_vid
    config += videos_per_word

    return config

