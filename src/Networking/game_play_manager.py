#-*- encoding: UTF-8 -*-

from PyQt4.QtCore import *
import json, logging
import game_room_manager
from login_manager import LoginManager
import network_client

def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton

#confirm type
CONFIRM_START   = 0
CONFIRM_REDO    = 1
CONFIRM_GIVE_UP = 2

#confirm side
CONFIRM_REQUEST  = 0
CONFIRM_RESPONSE = 1

#chess
NONE_CHESS  = 0
WHITE_CHESS = 1
BLACK_CHESS = 2

@singleton
class GamePlayManager(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.client = network_client.TcpClient()
        self.isStarting = False
        self.chessType = -1
        self.isYourTurn = False

        self.registConfirmCallback()
        self.registChessCallback()

    # 操作确认
    def confirm(self, side, type):
        if not LoginManager().isLogin or not game_room_manager.GameRoomManager().room:
            return 0

        reqData = {'sid': 1002,
                   'cid': 1000,
                   'uid': LoginManager().currentUser.uid,
                   'rid': game_room_manager.GameRoomManager().room.roomId,
                   'type': type,
                   'side': side}
        jsonReq = json.dumps(reqData)
        self.client.send(jsonReq)
        logging.debug('confirm send' + jsonReq)

    def registConfirmCallback(self):
        callbackKey = '1002_1000'
        self.client.callbacksDict[callbackKey] = self.confirmCallback

    def confirmCallback(self, response, data):
        allKeys = ['result', 'side', 'type']
        if [False for key in allKeys if key not in response.keys()]:
            logging.warning('confirm callback key error')
            return
        if not response['result']:
            return
        if response['side'] == CONFIRM_REQUEST:
            type = int(response['type'])
            self.emit(SIGNAL("requestWithType(int)"), type)
        elif response['side'] == CONFIRM_RESPONSE:
            type = int(response['type'])
            # 开始游戏确认
            if type == CONFIRM_START and response.has_key('chess'):
                self.isStarting = True
                self.emit(SIGNAL("start"))
                self.chessType = response['chess']
                if self.chessType == BLACK_CHESS:
                    self.isYourTurn = True

    #下棋
    def chess(self, x, y):
        if not LoginManager().isLogin or not game_room_manager.GameRoomManager().room:
            return 0
        if self.chessType == -1:
            return 0
        reqData = {'sid': 1002,
                   'cid': 1001,
                   'uid': LoginManager().currentUser.uid,
                   'rid': game_room_manager.GameRoomManager().room.roomId,
                   'type': self.chessType,
                   'x': x,
                   'y': y}

        jsonReq = json.dumps(reqData)
        self.client.send(jsonReq)
        logging.debug('chess send' + jsonReq)

    def registChessCallback(self):
        callbackKey = '1002_1001'
        self.client.callbacksDict[callbackKey] = self.chessCallback

    def chessCallback(self, response, data):
        allKeys = ['result', 'x', 'y', 'type']
        if [False for key in allKeys if key not in response.keys()]:
            logging.warning('chess callback key error')
            return
        if response['result']:
            self.emit(SIGNAL("chess(int,int,int)"), response['x'],
                      response['y'], response['type'])



