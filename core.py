import random
from datetime import datetime

while True:
    cmd = input("Flolover OS> ")

    if cmd == "help":
        print("Available commands: help, exit, quit, about, joke, roll, flip, time.")

    elif cmd == "about":
        print("Flolover OS v1.0 (beta)")

    elif cmd == "roll":
        a = int(input("roll: "))
        num = random.randint(1, a)
        print(num)

    elif cmd == "joke":
        print(
            "Why are ducks so good at keeping secrets? — Because they always quack only to themselves.\n"
            "What does a cat do when it falls off the roof? — Meows, “Well, landed safely.”\n"
            "Why is a carrot always happy? — Because it’s the root of all joy.\n"
            "How do you call an elephant hiding in the fridge? — A small elephant.\n"
            "Why didn’t the book go to the party? — It was afraid it would be flipped through.\n"
            "What did one tooth say to the other? — “Hang in there, together we’re stronger!”\n"
            "Why doesn’t the moon go to school? — It already has full knowledge.\n"
            "Why do bees always buzz? — Because they don’t know the words to songs.\n"
            "What did the snowman say to the carrot? — “You’re the nose of my heart.”\n"
            "Why do clocks always rush? — Because time waits for no one."
        )

    elif cmd == "flip":
        text = input()
        flipped = text[::-1]
        print("🔄", flipped)

    elif cmd == "time":
        now = datetime.now()
        print(now.strftime("%H:%M:%S.%f")[:-3])

    elif cmd == "exit" or cmd == "quit":
        exit()

    elif cmd == " ":
        continue

    elif cmd == "":
        continue

    else:
        print("Command not found!!!")
