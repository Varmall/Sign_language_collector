The app to record word videos for sign language (ASL).

Written in Python 3.11<br>
Recommended IDE: Pycharm<br>
Requires a camera for obvious reason<br>
Recommended OS: Windows 10/11. Might work on Linux or MacOs but not tested.<br>

After cloning, make venv with Python 3.11, install all packages from requirements.txt. Run main.py or build binary with main.py and run it.<br>

The app works on the session basis that is started with the Start Record Session button. The session means that the given number of videos will be recorded sequentially for a selected word.<br>
The videos will be saved in the "{Save Path}/{word_timestamp}/" directory. Between each video will be 3 second countdown. The session can be stopped during the countdown or will stop automatically when all videos are recorded.

"Change save path" button: With this button you can choose base directory for video savings. All word directories will be saved there.<br>
"Select word" let's you select word to record in record session.<br>
"Number of videos": Number of videos to record in a next session.<br>
"Frames per video": Number of frames to record for each video. (Ex. 30 frames will result in a 1 second video, 45 results in 1.5s, 60 is 2 second video, etc. The default framerate (fps) is 30, you can change that in config file.)<br>
"Start Record Session" Button: Starts the record session. Changes to "Stop Record Session" if in session.<br>

The app displays example videos when you select word to record. It will automatically load relevant videos when you change word.<br>
