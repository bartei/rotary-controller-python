class BeepMixin:
    """Mixin for Kivy button widgets that plays the app beep sound on press."""

    def on_press(self):
        from rcp.app import MainApp
        MainApp.get_running_app().beep()
