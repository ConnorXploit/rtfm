# encoding: utf-8
from .rtfm import APIS, MultipartEncoder, requests, os, get_db, app, json, global_conf, time, log, DIR_ACTUAL, datetime

import threading, socket, ipaddress, platform, subprocess, shlex, zipfile
from queue import Queue

def schedule(executionTime, functionName, args=(), onlyOne=False):
    if onlyOne:
        executed = False
        while not executed:
            actualTime = datetime.now().strftime("%H:%M")
            if executionTime == actualTime:
                executed = True
                log.send('Comenzamos el schedule : {f}'.format(f=functionName.__name__))
                if args:
                    functionName(args)
                else:
                    functionName()
            time.sleep(1)
    else:
        while not onlyOne:
            actualTime = datetime.now().strftime("%H:%M")
            if executionTime == actualTime:
                log.send('Comenzamos el schedule : {f}'.format(f=functionName.__name__))
                if args:
                    functionName(args)
                else:
                    functionName()
            time.sleep(60)
