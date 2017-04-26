#-*- encoding: UTF-8 -*-

import threading
import netstream
import time
import logging
import json

class TcpClient(netstream.netstream):
    def __init__(self):
        netstream.netstream.__init__(self)
        self.isConnnecting = False
        self.shutdown = False
        self.callbacksDict = {}
        self.loopThread = threading.Thread(target=self.processing)

    def connect(self, address='127.0.0.1', port=7890,
                head=-1, block=False, timeout=0):
        suc = netstream.netstream.connect(self, address, port,
                                          head, block, timeout)
        if suc == 0:
            self.isConnnecting = True
            self.loopThread.start()
            return 0
        return -1

    def processing(self):
        while not self.shutdown:
            time.sleep(0.05)
            self.process()
            if self.status() == netstream.NET_STATE_ESTABLISHED:
                while True:
                    data = self.recv()
                    if data:
                        logging.debug(data)
                        response = json.loads(data)
                        if response.has_key('sid') and response.has_key('cid'):
                            sid = response['sid']
                            cid = response['cid']
                            callbackKey = '%d_%d' % (sid, cid)
                            callback = self.callbacksDict[callbackKey]
                            callback(response)

            elif self.status() == netstream.NET_STATE_STOP:
                break
