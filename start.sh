if [ $# -lt 1 ]; then
    port=5900
else
    port=$1
fi
cat ${port}.PID|xargs kill
# sudo apt-get update
# sudo apt-get install build-essential
# sudo apt-get install fonts-wqy-zenhei fonts-wqy-microhei xfonts-intl-chinese
# sudo fc-cache -fv
# wget -c https://repo.anaconda.com/miniconda/Miniconda3-py310_24.9.2-0-Linux-x86_64.sh
# sh Miniconda3-py310_24.9.2-0-Linux-x86_64.sh
# sudo apt install libgl1 libegl1 websockify libxkbcommon0
# sudo bash install.sh
# bash install.sh
LANG=zh_CN.UTF8 QT_QPA_PLATFORM="vnc:port=${port}" python examples/binance/run.py >> ${port}.log 2>&1 &
echo $! > ${port}.PID
# cd noVNC && ./utils/novnc_proxy --vnc localhost:5900

