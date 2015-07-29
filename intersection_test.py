from sailorsbot import SBot
import time

with SBot(4) as bot:
    bot.set_mode(1)
    print "still line following"
    bot.wait_for_manual()
    print "@ intersection"
    bot.set_left_motor(0.17)
    time.sleep(1)
    #bot.stop()




