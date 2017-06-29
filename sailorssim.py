from matplotlib import pyplot as plt
from math import *
from numpy.random import randn

def simulate(f, speed=0.3,
                dt=1/20.,
                numsteps=20*2,
                state=(0.0, -0.02, 0.0),
                sensor_lag=1/20.,
                plot=True):

    assert sensor_lag <= dt

    states = [state]
    line_positions = []
    line_position = measure(state)
    prev_line_position = measure(state)

    for i in range(numsteps):
        # measure and adjust for lag
        prev_line_position = line_position
        clp = measure(state)
        lp = prev_line_position
        tb = dt+sensor_lag
        line_position = (clp-lp)*dt/tb + lp

        speeds = f(speed, line_position, prev_line_position)

        state = step(state, speeds, dt)

        line_positions.append(line_position)
        states.append(state)

    if plot:
        plt.clf()
        plt.plot([s[0] for s in states], [s[1] for s in states])
        plt.axis('equal')
        return plt.show()
    else:
        return {"states":states, "times":times, "line_positions":line_positions}

# state = x, y, angle (radians)
def step(state, speeds, dt):
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
