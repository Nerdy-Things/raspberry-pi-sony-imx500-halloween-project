#!/bin/bash

# https://www.raspberrypi.com/documentation/accessories/ai-camera.html

# Required - installing dependencies
sudo apt update && sudo apt full-upgrade

sudo apt install -y imx500-all

sudo apt install -y python3-opencv python3-munkres

pip install model_compression_toolkit --break-system-packages
pip install imx500-converter[pt] --break-system-packages

# Download models
git submodule init
git submodule update

# Optional - Changing Locale
sudo sed -i 's/LANG=en_US.UTF-8/LANG=en_US.UTF-8/' /etc/default/locale
sudo sed -i 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
sudo locale-gen 
sudo update-locale LANG=en_US.UTF-8

# Optional - installing FTP
sudo apt install -y vsftpd
sudo sed -i 's/#write_enable=YES/write_enable=YES/' /etc/vsftpd.conf
sudo systemctl restart vsftpd.service

# Opional 
# in case if you need original repositories.
# git clone https://github.com/raspberrypi/picamera2.git
# git clone https://github.com/raspberrypi/imx500-models.git

sudo reboot now