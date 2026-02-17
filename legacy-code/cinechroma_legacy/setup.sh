#! /bin/bash

#install ffmpeg
sudo apt update
sudo apt install ffmpeg
ffmpeg -version

#make a separate workspace directory
mkdir cinechroma
mkdir cinechroma/frames
mkdir cinechroma/videos

#copy the python files to the cinechroma directory
mv get_frames.py
mv get_color_palette.py
mv main.py

#font installation
sudo apt install ttf-mscorefonts-installer
sudo fc-cache -f
fc-match Arial

#install required python packages
pip3 install -U scikit-learn scipy matplotlib PIL numpy

