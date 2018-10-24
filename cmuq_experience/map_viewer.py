#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 20:16:37 2018

@author: eduardo
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.cbook as cbook
import paho.mqtt.client as mqtt
import matplotlib.animation as animation
import matplotlib.transforms as transforms
robot_poses = {}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("cozmo/pose")


def on_message(client, userdata, message):
    global x, y, theta
    print("rcv msg %s %s" % (message.topic, message.payload))
    print(type(message.payload))
    try:
        s=message.payload.decode("utf-8")
        t = s.split()
        x = int(t[0])
        y = int(t[1])
        theta = float(t[2])
        print("new pose ", x, y, theta)
    except Exception as e:
        print("error")
        import traceback
        print(e)


client = None
def listen_poses():
    global client
    host = "192.168.100.94"
    client = mqtt.Client()
    client.connect(host)
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_start()

x=100
y=200
theta = 0
cx=0
cy=0
fig = None
ax = None
def updatefig(*args):
    global x, y
    im.set_extent((x-cx, x+cx, y-cy, y+cy))
    tr = transforms.Affine2D().translate(-x, -y).rotate(theta).translate(x, y)
    im.set_transform(tr + ax.transData)
    return im,


if __name__ == "__main__":
    with cbook.get_sample_data('/home/eduardo/Dropbox/cozmo/sdk/src/mindcraft-treasure-hunt-cozmo/cmuq_experience/cozmoworld2.png') as image_file:
        image = plt.imread(image_file)
    print(image.shape)

    h,w,_ = image.shape
    print(w,h)
    w=1560
    h = 1410

    fig, ax = plt.subplots(figsize=(20,20))
    im = ax.imshow(image, extent=(-w/2., w/2., -0.5, h- 0.5))


    with cbook.get_sample_data('/home/eduardo/Dropbox/cozmo/cozmo_top.png') as image_file:
        image = plt.imread(image_file)
    print(image.shape)

    h,w,_ = image.shape
    print("robot img shape", h, w)
    x=100
    y =200
    ar=1.0*h/w
    cx=50
    cy=int(cx*ar)
    im = ax.imshow(image,extent=(x-cx, x+cx, y-cy, y+cy), animated=True)
    ax.set_xlim(-800,800)
    ax.set_ylim(0, 1400)
    ani = animation.FuncAnimation(fig, updatefig, interval=50, blit=False)
    listen_poses()
    print("done")
    plt.show()


#%%
