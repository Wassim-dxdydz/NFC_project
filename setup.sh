#!/bin/bash
chmod +x "$0"

OS_TYPE="$(uname -s)"
echo "Configuring environment for $OS_TYPE..."

if [[ "$OS_TYPE" == "Linux"* ]]; then
    sudo apt-get update
    sudo apt-get install -y python3-dev pcscd libpcsclite-dev swig pcsc-tools
    sudo systemctl enable pcscd
    sudo systemctl start pcscd
    PYTHON_CMD="python3"
else
    echo "Windows detected. Ensure Feitian/Cryptnox drivers are installed."
    PYTHON_CMD="python3"
fi

$PYTHON_CMD -m venv venv
source venv/bin/activate || source venv/Scripts/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete. Run 'python main.py' to begin."
