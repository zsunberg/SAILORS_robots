from matplotlib import pyplot as plt
from multiprocessing import Process
import time

class RealTimePlot(object):
    def __init__(self, sbot, varname, window):
        self.p = Process(target=plot_proc, args=(sbot._shared, varname, window))        
        self.p.start()

    def kill(self):
        self.p.terminate()
        self.p.join()

def plot_proc(shared, varname, window):
    plt.ion()
    fig = plt.figure()
    print 'started'
    plt.show()
    plt.pause(0.1)
    print 'show'
    times = []
    values = []

    last_tick = 0

    while True:
        if shared['data_tick'].value > last_tick:
            last_tick = shared['data_tick'].value
            current = time.time()
            times.append(current)
            val = shared[varname].value
            values.append(val)

            # print 'plotting {} {}'.format(current, val)

            # indices_in_window = [i for i, t in enumerate(times) if t >= current-window]
            min_index = next((i for i,t in enumerate(times) if t >= current-window), None)

            plt.cla()
            plt.plot([t-current for t in times[min_index:]], values[min_index:])
            plt.grid()
            plt.pause(0.01)

            if times[0] < current-2*window:
                times = times[min_index:]
                values = values[min_index:]
        else:
            time.sleep(0.01)

        if not plt.fignum_exists(fig.number):
            break
