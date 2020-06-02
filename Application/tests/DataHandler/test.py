#!/usr/bin/python
from websocket import create_connection
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig, ax = plt.subplots(nrows=2, ncols=3)
fr1 = []
fr2 = []
fr3 = []
fl1 = []
fl2 = []
fl3 = []
ws = create_connection("ws://192.168.1.76/ws")


def animate(i):
    data = ws.recv()
    _, _, fsr1, fsr2, fsr3, fsl1, fsl2, fsl3 = data.split(',')
    fr1.append(float(fsr1))
    fr2.append(float(fsr2))
    fr3.append(float(fsr3))
    fl1.append(float(fsl1))
    fl2.append(float(fsl2))
    fl3.append(float(fsl3))
    ax[0, 0].clear()
    ax[0, 1].clear()
    ax[0, 2].clear()
    ax[1, 0].clear()
    ax[1, 1].clear()
    ax[1, 2].clear()
    ax[0, 0].plot(fr1[-100:])
    ax[0, 1].plot(fr2[-100:])
    ax[0, 2].plot(fr3[-100:])
    ax[1, 0].plot(fl1[-100:])
    ax[1, 1].plot(fl2[-100:])
    ax[1, 2].plot(fl3[-100:])


ani = animation.FuncAnimation(fig, animate, interval=100)
plt.show()

ws.close()
