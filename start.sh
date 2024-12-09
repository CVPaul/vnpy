# wget -c https://repo.anaconda.com/miniconda/Miniconda3-py310_24.9.2-0-Linux-x86_64.sh
# sh Miniconda3-py310_24.9.2-0-Linux-x86_64.sh
sudo apt install libgl1 libegl1 websockify libxkbcommon0
sudo bash install.sh
bash install.sh
pip install vnpy_ctp
pip install vnpy_sqlite
pip install vnpy_ctastrategy
pip install vnpy_ctabacktester
pip install vnpy_datamanager
pip install vnpy_binance
QT_QPA_PLATFORM=vnc python examples/veighna_trader/run.py &
# cd noVNC && ./utils/novnc_proxy --vnc localhost:5900

