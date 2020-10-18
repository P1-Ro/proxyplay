mkdir /opt/proxyplay
git clone https://github.com/P1-Ro/proxyplay.git /opt/proxyplay
pip install -r /opt/proxyplay/requirements.txt
ln -s /opt/proxyplay/proxyplay.service /etc/systemd/system/

read -r -p 'Please enter MAC address of source device: ' SOURCE_MAC
sed -i "s/MAC_ADDRESS =\"\"/MAC_ADDRESS =\"$SOURCE_MAC\"/g" /opt/proxyplay/config.py

systemctl start proxyplay && systemctl enable proxyplay

echo "Installation complete"