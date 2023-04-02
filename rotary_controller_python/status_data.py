from kivy.event import EventDispatcher
from kivy.properties import BooleanProperty
from rotary_controller_python.utils import communication


class StatusData(EventDispatcher):
    ready = BooleanProperty(False)
    forward = BooleanProperty(False)
    reverse = BooleanProperty(False)
    error_bad_ratio = BooleanProperty(False)
    ack_set_encoder = BooleanProperty(False)
    ack_synchro_mode = BooleanProperty(False)
    ack_index_mode = BooleanProperty(False)
    ack_jog_mode = BooleanProperty(False)
    index_mode = BooleanProperty(False)
    synchro_mode = BooleanProperty(False)

    def update(self, status_word: int):
        self.ready = communication.get_bit(status_word, communication.STATUS_BIT_READY)
        self.forward = communication.get_bit(status_word, communication.STATUS_BIT_FORWARD)
        self.reverse = communication.get_bit(status_word, communication.STATUS_BIT_REVERSE)
        self.error_bad_ratio = communication.get_bit(status_word, communication.STATUS_BIT_ERROR_BAD_RATIO)
        self.ack_set_encoder = communication.get_bit(status_word, communication.STATUS_BIT_ACK_SET_ENCODER)
        self.ack_synchro_mode = communication.get_bit(status_word, communication.STATUS_BIT_ACK_SYNCHRO_MODE)
        self.ack_index_mode = communication.get_bit(status_word, communication.STATUS_BIT_ACK_INDEX_MODE)
        self.ack_jog_mode = communication.get_bit(status_word, communication.STATUS_BIT_ACK_JOG_MODE)
        self.index_mode = communication.get_bit(status_word, communication.STATUS_BIT_INDEX_MODE)
        self.synchro_mode = communication.get_bit(status_word, communication.STATUS_BIT_SYNCHRO_MODE)
