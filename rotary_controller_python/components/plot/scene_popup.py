import math
import os

from kivy import Logger
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.vector import Vector

from rotary_controller_python.dispatchers.circle_pattern import CirclePatternDispatcher

log = Logger.getChild(__name__)
kv_file = os.path.join(os.path.dirname(__file__), __file__.replace(".py", ".kv"))
if os.path.exists(kv_file):
    log.info(f"Loading KV file: {kv_file}")
    Builder.load_file(kv_file)


class ScenePopup(Popup):
    zoom = NumericProperty(1.0)
    mouse_position = ListProperty([10, 20, 0])
    scene_canvas = ObjectProperty(None)
    circle_pattern = ObjectProperty(CirclePatternDispatcher())
    rect_pattern = ObjectProperty(CirclePatternDispatcher())

    def __init__(self, **kwargs):
        self._touches = []
        self._last_touch_pos = {}
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.window_mouse_pos)
        Window.bind(on_motion=self.on_motion)

        self.circle_pattern.recalculate()

    def connect_rect(self):
        self.rect_pattern.recalculate()
        self.scene_canvas.points = self.rect_pattern.points
        self.scene_canvas.bind(points=self.rect_pattern.setter('points'))
        pass

    def on_motion(self, window, etype, event):
        # will receive all motion events.
        if self.collide_point(window.mouse_pos[0], window.mouse_pos[1]):
            if event.device == 'mouse' and event.button in ('scrollup', 'scrolldown'):
                if event.button == 'scrollup':
                    self.zoom = self.zoom / 1.1
                if event.button == 'scrolldown':
                    self.zoom = self.zoom * 1.1

    def on_touch_down(self, touch):
        x, y = touch.x, touch.y

        # if the touch isn't on the widget we do nothing
        if not self.collide_point(x, y):
            return False

        if 'multitouch_sim' in touch.profile:
            touch.multitouch_sim = True

        # grab the touch so we get all it later move events for sure
        self._bring_to_front(touch)
        touch.grab(self)
        self._touches.append(touch)
        self._last_touch_pos[touch] = touch.pos
        return True

    def on_touch_move(self, touch):
        x, y = touch.x, touch.y

        # rotate/scale/translate
        if touch in self._touches and touch.grab_current == self:
            self.transform_with_touch(touch)
            self._last_touch_pos[touch] = touch.pos

        # stop propagating if its within our bounds
        if self.collide_point(x, y):
            return True

    def on_touch_up(self, touch):
        x, y = touch.x, touch.y

        # remove it from our saved touches
        if touch in self._touches and touch.grab_state:
            touch.ungrab(self)
            del self._last_touch_pos[touch]
            self._touches.remove(touch)

        # stop propagating if its within our bounds
        if self.collide_point(x, y):
            return True

    def transform_with_touch(self, touch):
        # just do a simple one finger drag
        changed = False
        # if len(self._touches) == self.translation_touches:
        #     # _last_touch_pos has last pos in correct parent space,
        #     # just like incoming touch
        #     dx = (touch.x - self._last_touch_pos[touch][0]) \
        #         * self.do_translation_x
        #     dy = (touch.y - self._last_touch_pos[touch][1]) \
        #         * self.do_translation_y
        #     dx = dx / self.translation_touches
        #     dy = dy / self.translation_touches
        #     # self.apply_transform(Matrix().translate(dx, dy, 0))
        #     changed = True

        if len(self._touches) == 1:
            return changed

        # we have more than one touch... list of last known pos
        points = [Vector(self._last_touch_pos[t]) for t in self._touches
                  if t is not touch]
        # add current touch last
        points.append(Vector(touch.pos))

        # we only want to transform if the touch is part of the two touches
        # farthest apart! So first we find anchor, the point to transform
        # around as another touch farthest away from current touch's pos
        anchor = max(points[:-1], key=lambda p: p.distance(touch.pos))

        # now we find the touch farthest away from anchor, if its not the
        # same as touch. Touch is not one of the two touches used to transform
        farthest = max(points, key=anchor.distance)
        if farthest is not points[-1]:
            return changed

        # ok, so we have touch, and anchor, so we can actually compute the
        # transformation
        old_line = Vector(*touch.ppos) - anchor
        new_line = Vector(*touch.pos) - anchor
        if not old_line.length():   # div by zero
            return changed

        scale = new_line.length() / old_line.length()
        self.zoom = scale * self.zoom

        changed = True
        return changed

    def window_mouse_pos(self, instance, value):
        global_pos = self.ids.scene_canvas.to_widget(value[0], value[1])
        delta_x = global_pos[0] - 5000
        delta_y = global_pos[1] - 5000
        degrees = math.degrees(math.atan2(delta_y, delta_x))
        self.mouse_position = [delta_x / self.zoom, delta_y / self.zoom, degrees]

    def cancel(self):
        self.dismiss()
