import os

from kivy.graphics import Color, Line
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.logger import Logger

import numpy as np

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class Grid(Widget):
    zoom = NumericProperty(1.0)

    def __init__(self, **kwargs):
        super(Grid, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)
        self.bind(zoom=self.update_canvas)

    def update_canvas(self, *args):
        small_step = 10.0
        big_step = 100.0

        while self.zoom > (10/small_step):
            small_step /= 10
            big_step /= 10

        while self.zoom < (10/small_step):
            small_step *= 10
            big_step *= 10

        self.canvas.clear()
        with self.canvas:
            color_value = 0.3 + (small_step * self.zoom) / 1000
            print(f"Small Step: {color_value}")
            Color(color_value, color_value, color_value, 1)

            for i in np.arange(0, self.width/2, small_step*self.zoom):
                Line(points=[i+self.width/2, 0, i+self.width/2, self.height], width=0.25)
            for i in np.arange(0, self.height/2, small_step*self.zoom):
                Line(points=[0, i+self.height/2, self.width,  i+self.height/2], width=0.25)
            for i in np.arange(0, -self.width/2, -small_step*self.zoom):
                Line(points=[i+self.width/2, 0, i+self.width/2, self.height], width=0.25)
            for i in np.arange(0, -self.height/2, -small_step*self.zoom):
                Line(points=[0, i+self.height/2, self.width,  i+self.height/2], width=0.25)

            color_value = 0.2 + (big_step * self.zoom) / 1000
            print(f"Big Step: {color_value}")
            Color(color_value, color_value, color_value, 1)
            for i in np.arange(0, self.width/2, big_step*self.zoom):
                Line(points=[i+self.width/2, 0, i+self.width/2, self.height], width=0.5)
            for i in np.arange(0, self.height/2, big_step*self.zoom):
                Line(points=[0, i+self.height/2, self.width,  i+self.height/2], width=0.5)
            for i in np.arange(0, -self.width/2, -big_step*self.zoom):
                Line(points=[i+self.width/2, 0, i+self.width/2, self.height], width=0.5)
            for i in np.arange(0, -self.height/2, -big_step*self.zoom):
                Line(points=[0, i+self.height/2, self.width,  i+self.height/2], width=0.5)

            Color(0.5, 1, 0.5, 1)
            Line(points=[self.width/2, 0, self.width/2, self.height], width=1)
            Line(points=[0, self.height/2, self.width,  self.height/2], width=1)
