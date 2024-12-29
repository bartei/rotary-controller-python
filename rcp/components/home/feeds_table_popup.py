from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem

from rcp import feeds

log = Logger.getChild(__name__)


class FeedButton(Button):
    text_halign = "center"
    font_style = "bold"
    font_name = StringProperty("fonts/Manrope-Bold.ttf")
    halign = "center"
    background_color = [1, 1, 1, 1]
    return_value = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_height(self, instance, value):
        self.font_size = value / 3


class FeedsTablePopup(Popup):
    def __init__(self, **kwargs):
        from rcp.app import MainApp
        self.app: MainApp = MainApp.get_running_app()
        super().__init__(**kwargs)
        self.title = f"Select Feed"
        self.title_size = "20sp"
        self.size_hint = (0.8, 0.8)
        self.auto_dismiss = False

        panel = TabbedPanel(
            do_default_tab=False,
            tab_width=150,
        )

        for name, table in feeds.table.items():
            layout = GridLayout(cols=5)
            for idx, pitch in enumerate(table):
                layout.add_widget(
                    FeedButton(text=pitch.name, return_value=(name, idx), on_release=self.confirm)
                )
            tab = TabbedPanelItem(text=name)
            tab.add_widget(layout)
            panel.add_widget(tab)

        self.add_widget(panel)
        self.callback_fn = None
        self.current_value = None

    def on_touch_down(self, touch):
        self.app.beep()
        return super().on_touch_down(touch)

    def show_with_callback(self, callback_fn, current_value=None):
        if current_value is not None:
            # Use the specified current value if passed
            self.current_value = float(current_value)

        self.callback_fn = callback_fn
        self.open()

    def confirm(self, instance: FeedButton):
        try:
            value = instance.return_value
            self.callback_fn(table_name=value[0], index=value[1])
            self.dismiss()
        except Exception as e:
            log.error(e.__str__())
            return

    def cancel(self, *args, **kwargs):
        self.dismiss()
