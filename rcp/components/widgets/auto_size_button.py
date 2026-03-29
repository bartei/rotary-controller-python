from kivy.core.text import Label as CoreLabel
from kivy.properties import NumericProperty
from kivy.uix.button import Button

from rcp.components.widgets.beep_mixin import BeepMixin


class AutoSizeButton(BeepMixin, Button):
    """Button that automatically scales font_size down to prevent text wrapping.

    Set max_font_size to the desired font size. The actual font_size will be
    clamped so the text fits on a single line within the available width.
    """
    max_font_size = NumericProperty(48)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(text=self._fit_text)
        self.bind(size=self._fit_text)
        self.bind(max_font_size=self._fit_text)
        self.bind(font_name=self._fit_text)

    def _fit_text(self, *args):
        if not self.text or self.width <= 0:
            self.font_size = self.max_font_size
            return

        available = self.width - self.padding[0] - self.padding[2]
        if available <= 0:
            return

        # Measure the natural (unconstrained) text width at max_font_size
        label = CoreLabel(
            text=self.text,
            font_size=self.max_font_size,
            font_name=self.font_name,
        )
        label.refresh()
        text_width = label.texture.size[0]

        if text_width > available * 0.95:
            scale = (available * 0.95) / text_width
            self.font_size = max(8, self.max_font_size * scale)
        else:
            self.font_size = self.max_font_size