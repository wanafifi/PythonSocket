
from time import sleep
import os
import sys
def start():
    print("start")
    project_run_count = 0
    count = 0
    while count < 100:
        project_run_count += 1
        os.system('clear')
        print("project run count is :", project_run_count)
        print("argv was", sys.argv)
        print("sys.executable was", sys.executable)
        if project_run_count > 200:
            print("Restarting......")
            sleep(2)
            os.execv(sys.executable, ['python3'] + sys.argv)
        elif count < 100:
            count = 0
        else:
            count += 1
        sleep(0.05)

start()