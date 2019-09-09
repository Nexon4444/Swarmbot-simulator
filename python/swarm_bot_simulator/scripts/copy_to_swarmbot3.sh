#!/bin/bash
scp Bot_controller/*.py root@192.168.0.102:~/praca_dyplomowa/git/Bot_controller
scp Bot_controller/controller/*.py root@192.168.0.102:~/praca_dyplomowa/git/Bot_controller/controller
scp Bot_controller/communication/*.py root@192.168.0.102:~/praca_dyplomowa/git/Bot_controller/communication
scp Bot_controller/model/*.py root@192.168.0.102:~/praca_dyplomowa/git/Bot_controller/model
scp Bot_controller/scripts/* root@192.168.0.102:~/praca_dyplomowa/git/Bot_controller/scripts
#rsync -avh -e ssh ../Bot_controller  root@192.168.0.113:~/praca_dyplomowa/git
