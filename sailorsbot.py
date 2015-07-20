from multiprocessing import Process, Value, Pipe, Array
import socket
from warnings import warn
import time

class SBot(object):

    def __init__(self, id_num):
        self.id_num = id_num
        self._shared = dict()
        # self._shared['direct_pipe'], self.direct_pipe = Pipe(False)
        self._shared['direct_pipe'], self.direct_pipe = Pipe(False)
        self._shared['left_motor'] = Value('d',0.0)
        self._shared['right_motor'] = Value('d',0.0)
        self._shared['sensors'] = Array('i', 5*[0])
        self._shared['line_position'] = Value('d',0.0)
        self._shared['kill_flag'] = Value('i', 0)
        self._comm = Process(target=scomm, args=(id_num, self._shared))
        self._comm.start()

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
        self._shared['left_motor'].value = 0.0        
        self._shared['right_motor'].value = 0.0
        self.direct_send('l:0.0\n')
        self.direct_send('r:0.0\n')

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

    # def __del__(self):
    #     self.kill_comm()

def scomm(id_num, shared):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    ip_addr = '192.168.1.1{:02d}'.format(id_num)
    s.connect((ip_addr, 9750))
    s.settimeout(0.01)

    errors = []
    stopped_with_ctrl_c = False

    def send_commands():
        if shared['direct_pipe'].poll():
            s.send(shared['direct_pipe'].recv())

        s.send('l:{}\n'.format(shared['left_motor'].value))
        s.send('r:{}\n'.format(shared['right_motor'].value))


    while True:

        try:
            if shared['kill_flag'].value != 0:
                break

            time.sleep(0.2)

            if shared['left_motor'].value != 0.0 or shared['right_motor'].value != 0.0:
                stopped_with_ctrl_c = False

            send_commands()

            data = None
            try:
                data = s.recv(1024)
            except socket.timeout, e:
                pass
            
            if data is not None:
                for d in data.split('\n'):
                    try:
                        if d[1] == ':': # this is data that has a specific meaning
                            if d[0] == 'p': # line position
                                shared['line_position'].value = float(d[2:])
                            elif d[0] == 's': # sensors
                                vals = [int(v) for v in d[2:].split(',')]
                                for i in range(len(vals)):
                                    shared['sensors'][i] = vals[i]
                            else:
                                print(d)
                        else:
                            print(d)
                    except (IndexError, ValueError) as e:
                        # warn(str(e))
                        # errors.append(e)
                        if len(errors) >= 5:
                            warn("5 communication errors:")
                            while errors:
                                print(str(errors.pop(0)))


        except KeyboardInterrupt as e:
            if not stopped_with_ctrl_c:
                shared['left_motor'].value = 0.0
                shared['right_motor'].value = 0.0
                send_commands()
                stopped_with_ctrl_c = True
            else: # already stopped with ctrl-C
                send_commands()
                break

    send_commands()
    s.close()
