from multiprocessing import Process, Value, Pipe, Array, Queue
import socket
from warnings import warn
import time
import sys

#from ipdb import set_trace as bp

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
        self._shared['left_motor'] = Value('d',0.0)
        self._shared['right_motor'] = Value('d',0.0)
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
        self._shared['left_motor'].value = 0.0        
        self._shared['right_motor'].value = 0.0

    def forward(self, speed):
        self._shared['right_motor'].value = speed
        self._shared['left_motor'].value = speed

    def get_sensors(self):
        return list(self._shared['sensors'])

    def get_line_position(self):
        return self._shared['line_position'].value

    def set_left_motor(self, speed):
        self._shared['left_motor'].value = speed

    def set_right_motor(self, speed):
        self._shared['right_motor'].value = speed

    def set_mode(self, mode, wait_for_ack=True):
        last_time = self._shared['mode_ack_time'].value
        self.direct_send('c:{}\n'.format(mode))
        if wait_for_ack:
            while self._shared['mode_ack_time'].value <= last_time and self._shared['reported_mode'].value != mode:
                time.sleep(0.02)

    def turn(self, direction):
        last_time = self._shared['mode_ack_time'].value
        self.direct_send('t:{}\n'.format(direction))
        while self._shared['mode_ack_time'].value <= last_time and self._shared['reported_mode'].value != TURN_MODE:
            time.sleep(0.02)

    def nudge(self, duration):
        self.direct_send("n:{}\n".format(duration))
        time.sleep(duration+0.2)

    def wait_for_manual(self):
        while self._shared['reported_mode'].value != MANUAL_MODE:
            time.sleep(0.02)

    def set_gains(self, k_p, k_i, k_d):
        self.direct_send('g:p:{}\n'.format(k_p))
        self.direct_send('g:i:{}\n'.format(k_i))
        self.direct_send('g:d:{}\n'.format(k_d))


def scomm(id_num, shared):
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    # ip_addr = '192.168.1.1{:02d}'.format(id_num)
    # s.connect((ip_addr, 9750))
    # s.settimeout(0.01)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip_addr = '192.168.1.1{:02d}'.format(id_num)
    s.bind(('', 9700+id_num))
    s.settimeout(0.01)


    errors = []
    ticks_since_ctrl_c = 10
    leftovers = ''

    def send_commands():
        if shared['direct_pipe'].poll():
            s.sendto(shared['direct_pipe'].recv(), (ip_addr,9750))

        s.sendto('l:{}\n'.format(shared['left_motor'].value), (ip_addr,9750))
        s.sendto('r:{}\n'.format(shared['right_motor'].value), (ip_addr,9750))


    while True:

        try:
            if shared['kill_flag'].value != 0:
                break

            time.sleep(0.1)

            '''
            if shared['left_motor'].value != 0.0 or shared['right_motor'].value != 0.0:
                stopped_with_ctrl_c = 0
            '''
            ticks_since_ctrl_c += 1

            send_commands()

            data = None
            try:
                data = leftovers + s.recv(1024)
            except socket.timeout, e:
                pass

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
                        # errors.append(e)
                        # if len(errors) >= 5:
                        #     warn("{} communication errors:".format(len(errors)))
                        #     while errors:
                        #         print(str(errors.pop(0)))


        except KeyboardInterrupt as e:
            if ticks_since_ctrl_c > 10:
                s.sendto('c:{}\n'.format(MANUAL_MODE), (ip_addr,9750))
                shared['left_motor'].value = 0.0
                shared['right_motor'].value = 0.0
                send_commands()
                ticks_since_ctrl_c = 0
            else: # already stopped with ctrl-C
                send_commands()
                break

    send_commands()
    s.close()
    # sys.stdout.write('waiting for connection to close...')
    # # sys.stdout.flush()
    # time.sleep(2)
    # sys.stdout.write('done\n')
