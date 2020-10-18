#!/bin/bash
# Script to install the proxyplay

# Check sudo
if [ ! "$(id -u)" -eq 0 ]; then
  echo "You must be root to use this. Run with \"sudo $0\""
  exit 1
fi

echo "Cloning project"
mkdir /opt/proxyplay
git clone https://github.com/P1-Ro/proxyplay.git /opt/proxyplay  > /dev/null

echo "Installing dependencies"
pip install -r /opt/proxyplay/requirements.txt > /dev/null

read -r -p 'Please enter MAC address of source device: ' SOURCE_MAC
sed -i "s/MAC_ADDRESS =\"\"/MAC_ADDRESS =\"$SOURCE_MAC\"/g" /opt/proxyplay/config.py

echo "Installing service"
ln -s /opt/proxyplay/proxyplay.service /etc/systemd/system/
systemctl start proxyplay && systemctl enable proxyplay

echo "Installation complete"