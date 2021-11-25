백그라운드 실행(서버)
패키지 목록 업데이트: sudo apt update
pip3 설치: sudo apt install python3-pip
서버시간 설정 : sudo ln -sf /usr/share/zoneinfo/Asia/Seoul /etc/localtime
백그라운드 실행 : nohup python -u cryptoAutoTrade_v3.py > output.log &
실시간 로그 확인 : tail -f output.log
프로세스 확인 : ps -ef | grep .py
프로세스 종료 : kill -9 PID (PID 는 ps 명령의 출력값에서 해당 프로세스의 맨 앞의 숫자)
