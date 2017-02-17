import providers.globals as gvars
import telebot
import threading

from providers.config import get_config


def get_telebot():
    if not gvars.APP_TELEBOT:
        gvars.APP_TELEBOT = TeleBot()
    return gvars.APP_TELEBOT


class TeleBot(telebot.TeleBot):
    token = None
    quotation_chats = []

    def __init__(self):
        config = get_config()
        self.token = config.get_telegram_token()
        super(TeleBot, self).__init__(self.token)

        poll = threading.Thread(target=self.start_pool)
        poll.setDaemon(True)
        poll.start()

    def start_pool(self):
        self.set_update_listener(self.listener)
        self.polling(none_stop=True)

    def listener(self, messages):
        for m in messages:
            if m.content_type == 'text':
                if m.text == "Подключиться к котировкам":
                    self.send_message(m.chat.id, "Я подключил вас к котировкам")
                    self.quotation_chats.append(m.chat.id)
                if m.text == "Отключиться от котировок":
                    self.send_message(m.chat.id, "Я отключил вас от котировок")
                    self.quotation_chats.remove(m.chat.id)

    def new_quotation(self, text):
        for chat in self.quotation_chats:
            self.send_message(chat, text)
