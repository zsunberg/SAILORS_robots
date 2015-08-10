from multiprocessing import Process, Value, Pipe, Array, Queue
import socket
from warnings import warn
import time
import sys

# from ipdb import set_trace as bp

MANUAL_MODE = 0;
LINE_FOLLOWING_MODE = 1;
TURN_MODE = 2;

class SBot(object):

    def __init__(self, id_num):
        self.id_num = id_num
        self._shared = dict()
        # self._shared['direct_pipe'], self.direct_pipe = Pipe(False)
        self._shared['direct_pipe'], self.direct_pipe = Pipe(False)
        self._shared['data_tick'] = Value('l',-1) # incremented every time data is received
        # self._shared['left_motor'] = Value('d',0.0)
        # self._shared['right_motor'] = Value('d',0.0)
        self._shared['sensors'] = Array('i', 5*[0])
        self._shared['line_position'] = Value('d',0.0)
        self._shared['kill_flag'] = Value('i', 0)
        self._shared['reported_mode'] = Value('i',-1)
        self._shared['mode_ack_time'] = Value('d', 0.0)
        # self._shared['acknowledged'] = self._manager.dict()
        # self._shared['commanded_mode'] = Value('i',MANUAL_MODE)
        self._comm = Process(target=scomm, args=(id_num, self._shared))
        self._comm.start()
        time.sleep(1)

    def direct_send(self, string):
        self.direct_pipe.send(string)

    def kill_comm(self):
        self._shared['kill_flag'].value = 1
        self._comm.join()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print exc_type, exc_value, traceback
        self.stop()
        self.kill_comm()

    def stop(self):
        self.set_mode(MANUAL_MODE, wait_for_ack=False)
        self.direct_send('l:0.0\n')
        self.direct_send('r:0.0\n')
        # self._shared['left_motor'].value = 0.0        
        # self._shared['right_motor'].value = 0.0

    def forward(self, speed):
        self.direct_send('l:{}\n'.format(speed))
        self.direct_send('r:{}\n'.format(speed))
        # self._shared['right_motor'].value = speed
        # self._shared['left_motor'].value = speed

    def get_sensors(self):
        return list(self._shared['sensors'])

    def get_line_position(self):
        return self._shared['line_position'].value

    def set_left_motor(self, speed):
        self.direct_send('l:{}\n'.format(speed))

    def set_right_motor(self, speed):
        self.direct_send('r:{}\n'.format(speed))

    def set_mode(self, mode, wait_for_ack=True):
        last_time = self._shared['mode_ack_time'].value
        self.direct_send('c:{}\n'.format(mode))
        if wait_for_ack:
            while self._shared['mode_ack_time'].value <= last_time:
                time.sleep(0.02)

    def turn(self, direction):
        last_time = self._shared['mode_ack_time'].value
        self.direct_send('t:{}\n'.format(direction))
        while self._shared['mode_ack_time'].value <= last_time:
            time.sleep(0.02)
        self.wait_for_manual()

    def nudge(self, duration):
        last_time = self._shared['mode_ack_time'].value
        self.direct_send("n:{}\n".format(duration))
        time.sleep(duration+0.2)
        while self._shared['mode_ack_time'].value <= last_time:
            time.sleep(0.02)
        self.wait_for_manual()


    def wait_for_manual(self):
        while self._shared['reported_mode'].value != MANUAL_MODE:
            time.sleep(0.02)

    def set_gains(self, k_p, k_i, k_d):
        self.direct_send('g:p:{}\n'.format(k_p))
        self.direct_send('g:i:{}\n'.format(k_i))
        self.direct_send('g:d:{}\n'.format(k_d))


def scomm(id_num, shared):

    def setup_connection():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
            ip_addr = '192.168.1.1{:02d}'.format(id_num)
            s.connect((ip_addr, 9750))
            s.settimeout(0.01)
        except socket.error as e:
            print e
            if e[0]==111: # connection refused
                print
                print 'if in ipython: press Ctrl-C twice quickly and try again'
                print 'otherwise: press Ctrl-C, run `pkill python` and try again'
                print
                sys.exit()
            else:
                raise e
        return s

    def reset_connection(s):
        print
        print 'automatically resetting connection. please wait...'
        s.close()
        s = setup_connection()
        print 'done.'
        print
        return s

    s = setup_connection()

    errors = []
    ticks_since_ctrl_c = 20
    leftovers = ''
    reset_flag = False

    def send_commands(s):
        while shared['direct_pipe'].poll():
            s.send(shared['direct_pipe'].recv())

    while True:

        try:
            if shared['kill_flag'].value != 0:
                break


            time.sleep(0.05)

            ticks_since_ctrl_c += 1

            try:
                send_commands(s)
            except socket.error as e:
                print e
                if e[0]==104: # connection reset
                    s = reset_connection(s)
                else:
                    raise e


            data = None
            try:
                data = leftovers + s.recv(1024)
            except socket.timeout, e:
                pass
            except socket.error as e:
                print e
                if e[0]==104: # connection reset
                    s = reset_connection(s)
                else:
                    raise e

            if data is not None:
                with shared['data_tick'].get_lock():
                    shared['data_tick'].value += 1

                leftover_begin = data.rfind('\n')+1
                leftovers = data[leftover_begin:]
                data = data[:leftover_begin]
                for d in data.split('\n'):
                    try:
                        if d[1] == ':': # this is data that has a specific meaning
                            if d[0] == 'p': # line position
                                shared['line_position'].value = float(d[2:])
                                # print(shared['line_position'].value)
                            elif d[0] == 's': # sensors
                                vals = [int(v) for v in d[2:].split(',')]
                                for i in range(len(vals)):
                                    shared['sensors'][i] = vals[i]
                            elif d[0] == 'm': # mode
                                shared['reported_mode'].value = int(d[2:])
                            elif d[0] == 'a': # acknowledgement
                                if d[2] == 'c':
                                    shared['reported_mode'].value = int(d[4:])
                                    shared['mode_ack_time'].value = time.time()
                            else:
                                print(d)
                        else:
                            print(d)
                    except (IndexError, ValueError) as e:
                        if len(d) > 0:
                            warn(str(e)+'\ndata was "{}"'.format(d))

        except KeyboardInterrupt as e:
            if ticks_since_ctrl_c > 20:
                s.send('c:{}\n'.format(MANUAL_MODE))
                s.send('l:0.0\n')
                s.send('r:0.0\n')
                send_commands(s)
                ticks_since_ctrl_c = 0
            else: # already stopped with ctrl-C
                send_commands(s)
                break

    send_commands(s)
    s.close()


# for udp
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# ip_addr = '192.168.1.1{:02d}'.format(id_num)
# s.bind(('', 9700+id_num))
# s.settimeout(0.01)

