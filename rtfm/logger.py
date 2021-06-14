# encoding: utf-8
import logging
from .rtfm import os, telegram_bot

class Logger():

    def __init__(self, dir):
        self.dir = dir
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        self.notify_telegram = [ "ERROR", "EXCEPTION", "CALENDARIO", "GASTO", "FARMACIA" ]

    def send(self, message, status='INFO'):
        logging.basicConfig(
            filename=os.path.join(self.dir, 'rtfm.log'), 
            filemode='a', 
            format='%(asctime)s - %(message)s',
            level=logging.INFO
        )
        logging.info( '[{status}] - {m}'.format(status=str(status).upper(), m=message) )
        if status in self.notify_telegram:
            telegram_bot.sendMessage( '[{status}] - {m}'.format(status=str(status).upper(), m=message) )