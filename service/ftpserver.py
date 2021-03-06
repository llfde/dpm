#      ftpserver.py
#      
#      Copyright (C) 2015 Xiao-Fang Huang <huangxfbnu@163.com>
#      
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation; either version 2 of the License, or
#      (at your option) any later version.
#      
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#      
#      You should have received a copy of the GNU General Public License
#      along with this program; if not, write to the Free Software
#      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#      MA 02110-1301, USA.


import os

from twisted.internet import reactor
from twisted.cred.portal import Portal, IRealm
from zope.interface import implements
from twisted.python.filepath import FilePath
from twisted.protocols.ftp import FTPFactory, IFTPShell, FTPShell, FTPAnonymousShell
from twisted.cred.checkers import AllowAnonymousAccess, FilePasswordDB, ANONYMOUS

from conf.config import PATH_FTPSERVER_ON_REPO

class DPMFTPRealm():
    implements(IRealm)
    def __init__(self, anonymousRoot):
        self.anonymousRoot = FilePath(anonymousRoot)
        self.dir = PATH_FTPSERVER_ON_REPO
        if not os.path.isdir(PATH_FTPSERVER_ON_REPO):
            os.makedirs(PATH_FTPSERVER_ON_REPO)
        
    def requestAvatar(self, avatarId, mind, *interfaces):
        for iface in interfaces:
            if iface is IFTPShell:
                if avatarId is ANONYMOUS:
                    avatar = FTPAnonymousShell(self.anonymousRoot)
                else:
                    user_dir = self.dir
                    avatar = FTPShell(FilePath(user_dir))
                return  IFTPShell, avatar, \
                       getattr(avatar, 'logout', lambda: None)
        raise NotImplementedError(\
            "Only IFTPShell interface is supported by this realm")       


class FTPServer():
    def __init__(self, port=21):
        #!!!!!!!!!!!!!!!!!!!path of user.db
        self.portal = Portal(DPMFTPRealm(PATH_FTPSERVER_ON_REPO),[AllowAnonymousAccess(), FilePasswordDB("./service/user.db")])        
        self.factory = FTPFactory(self.portal)
        self._port = port
     
    def run(self):    
        reactor.listenTCP(self._port, self.factory)
        reactor.run()