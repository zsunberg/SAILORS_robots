from sailorsbot import SBot
import time

with SBot(9) as bot:
    bot.set_gains(0.3,0,0)
    bot.set_mode(1)
    time.sleep(10)
    print "still line following"
    bot.wait_for_manual()
    print "@ intersection"
    bot.set_left_motor(0.2)
    time.sleep(0.85)
    print "@ curve"
    #bot.set_mode(1)
    #bot.wait_for_manual()
    #bot.stop()




