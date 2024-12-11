#if [ $# -lt 1 ]; then
#    echo ">>> please input the port that want to kill(e.g: 5900)!"
#    exit 1
#fi

cat 5900.PID|xargs kill
