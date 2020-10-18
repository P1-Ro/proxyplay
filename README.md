# ![ProxyPlay](https://raw.githubusercontent.com/P1-Ro/proxyplay/master/logo.png) <a href="https://codeclimate.com/github/P1-Ro/proxyplay/maintainability"><img src="https://api.codeclimate.com/v1/badges/6b867450360436b378e9/maintainability" /></a> [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Service to automatically turn CEC enabled devices on and off when Bluetooth device starts/stops playback.

## Installation
### Automatic
    
    curl https://raw.githubusercontent.com/P1-Ro/proxyplay/master/install.sh | sudo bash

### Manual

1. Clone this repo 
    ```
    mkdir /opt/proxyplay
    git clone https://github.com/P1-Ro/proxyplay.git /opt/proxyplay
    ```

2. Install dependencies
    ```
   pip install -r /opt/proxyplay/requirements.txt
   ```

3. Install service 
    ```
    sudo ln -s /opt/proxyplay/proxyplay.service /etc/systemd/system/
    ```
   :warning: **If you cloned it to different location you also need to change paths in `proxyplay.service`**

4. Start service and enable it on boot
    ```
   systemctl start proxyplay && systemctl enable proxyplay
   ```

## Configuration
* `MAC_ADDRESS`: Address of BT source device, currently only single device is supported and you must specify it.
* `SHUTDOWN_TIMEOUT`: Timeout after which CEC device is turned off. Tweak this iff CEC device is turned off when skipping songs.

## Usage
1. On startup of service tries to connect to BT address.
2. When connected you can start media playback and CEC device will be turned on
3. When playback stops CEC device will be turned off