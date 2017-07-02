from matplotlib import pyplot as plt
from matplotlib import animation
from math import *
from numpy.random import randn
from IPython.display import HTML

# f should return leftspeed, rightspeed
def simulate(f, loop_dt=0.02,
                end=2.0,
                state=(0.0, -0.02, -0.01),
                sensor_lag=0.023,
                left_wheel_bias=0.0,
                output='animate'):

    assert sensor_lag < 2*loop_dt # tricky to have larger sensor lag - don't want to support

    spool = SensorSpool(loop_dt, sensor_lag, measure(state))
    states = [state]
    line_positions = [measure(state)]
    time = 0.0
    times = [time]
    next_ctrl = time + loop_dt
    next_sense = min(0.0, next_ctrl - sensor_lag)
    speeds = f(measure(state), measure(state))

    while time < end:

        dt = min(next_ctrl, next_sense) - time
        if dt > 0.0:
            state = step(state, speeds, dt)
        
        time = min(next_ctrl, next_sense)

        if time == next_sense:
            spool.put(time, measure(state))
            if next_sense > 0.0:
                next_sense += loop_dt
            else:
                next_sense = next_ctrl - sensor_lag
                while next_sense <= 0.0:
                    next_sense += loop_dt


        if time == next_ctrl:
            line_position, prev_line_position = spool.get(time)
            speeds = f(line_position, prev_line_position)
            speeds = (speeds[0]+left_wheel_bias, speeds[1])
            states.append(state)
            line_positions.append(line_position)
            times.append(time)
            next_ctrl += loop_dt
            next_sense = next_ctrl - sensor_lag

    if output == 'animate' or output == 'plot':
        f, ax = plt.subplots(2, sharex=True)

        def plotstep(i):
            ss = states[0:i] 
            pp = line_positions[0:i]

            maxx = 0.5

            xs = [s[0] for s in ss]
            ys = [s[1] for s in ss]
            ax[0].plot(xs, ys, color='blue', label='robot position')
            ax[0].plot([0.0, maxx], [0.0, 0.0], color='black', label='line')
            ax[0].set_xlim(0.0, maxx)
            ax[0].axis('equal')
            ax[0].set_ylim(-0.06, 0.06)
            ax[0].set_xlabel('x (m)')
            ax[0].set_ylabel('y (m)')

            ax[1].plot(xs, pp, color='red')
            ax[1].set_xlim(0.0, 0.5)
            ax[1].set_ylim(-1.0, 1.0)
            ax[1].set_xlabel('x (m)')
            ax[1].set_ylabel('line_position')
            return ax

        if output == 'animate':
            print('Done simulating; Creating animation...')
            anim = animation.FuncAnimation(f, plotstep, interval=20, frames=len(times))
            return HTML(anim.to_html5_video())
        
        if output == 'plot':
            plotstep(len(times))
            plt.show()
            return None
    else:
        return {"states":states, "times":times, "line_positions":line_positions}

# state = x, y, angle (radians)
def step(state, speeds, dt):
    if dt == 0.0:
        return state

    x = state[0]
    y = state[1]
    theta = state[2]
    ls = speeds[0]
    rs = speeds[1]

    if rs == ls:
        speed = rs
        thetap = theta
        xp = x + speed*dt*cos(theta)
        yp = y + speed*dt*sin(theta)
    else:
        dtheta = (rs-ls)*dt/0.082
        r = ls*dt/dtheta + 0.041
        xc = x-r*sin(theta)
        yc = y+r*cos(theta)
        thetap = theta+dtheta
        xp = xc+r*sin(thetap)
        yp = yc-r*cos(thetap)

    return (xp, yp, thetap)

def measure(state):
    y = state[1]
    theta = state[2]
    rs = 0.043
    ys = y+rs*sin(theta)
    limit = rs*0.5
    lp = ys/limit
    lp = max(-1.0, min(1.0, lp))
    return lp

class SensorSpool(object):
    def __init__(self, loop_dt, sensor_lag, init_meas=0.0, eps=0.0001):
        self.eps = eps
        self.sensor_lag = sensor_lag
        mem_len = int(floor(sensor_lag/loop_dt)) + 2
        self.times = [0.0 for i in range(mem_len)]
        self.memory = [init_meas for i in range(mem_len)]
        self.current = 0

    def put(self, time, meas):
        self.current += 1
        if self.current == len(self.times):
            self.current = 0
        self.times[self.current] = time
        self.memory[self.current] = meas

    def get(self, time):
        toget = self.current+2
        if toget >= len(self.times):
            toget -= len(self.times)
        gettime = time - self.sensor_lag
        if gettime > 0.0:
            assert abs(self.times[toget] - gettime) < self.eps
        return self.memory[toget], self.memory[toget-1]

if __name__ == '__main__':
    def control(lp, plp):
        return 0.3, 0.3

    simulate(control, output=None)
    simulate(control, sensor_lag=0.0, output=None)
    simulate(control, sensor_lag=0.01, output=None)
    simulate(control, sensor_lag=0.035, output=None)
