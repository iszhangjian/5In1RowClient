# -*- encoding:utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from src.Networking import game_user_manager

class GameHallRankList(QListView):
    def __init__(self, parent=None):
        QListView.__init__(self, parent)
        self.setStyleSheet(
            '''
            border-image: url(:btn_bg);
            background-repeat: no-repeat;
            ''')

        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.setWordWrap(True)
        self.setUniformItemSizes(True)
        self.setGridSize(QSize(self.rect().width(), 30))
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAcceptDrops(True)

        self.connect(game_user_manager.GameUserManager(), SIGNAL("refreshRank"),
                     self.refresh)

    def refresh(self):
        self.model.clear()
        rank = 0
        for user in game_user_manager.GameUserManager().userScore:
            if 'uid' in user and 'score' in user:
                text = user['uid'] + ' : ' + str(user['score'])
                item = QStandardItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                item.setFont(QFont(50))
                if rank == 0:
                    item.setForeground(QBrush(QColor(255, 0, 0)))
                if rank == 1:
                    item.setForeground(QBrush(QColor(200, 0, 0)))
                if rank == 2:
                    item.setForeground(QBrush(QColor(150, 0, 0)))
                self.model.appendRow(item)
                rank += 1
