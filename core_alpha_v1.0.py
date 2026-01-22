import random
from datetime import datetime

while True:
    cmd = input("Flolover> ")

    if cmd == "help":
        print("Available commands: help, exit, info, time.")

    elif cmd == "info":
        print("Flolover OS v1.0 (beta)")

    elif cmd == "time":
        now = datetime.now()
        print(now.strftime("%H:%M:%S.%f")[:-3])

    elif cmd == "exit":
        exit()

    elif cmd == " ":
        continue

    elif cmd == "":
        continue

    else:
        print("Command not found! Try 'help' for menu")
