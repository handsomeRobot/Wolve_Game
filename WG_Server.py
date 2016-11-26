import PodSixNet
import datetime
import random
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from time import sleep

class ClientChannel(Channel):
    def Network(self, data):
        print data
    def Network_reg(self, data):
        name = data['player_name']
        self._server.Add_player(name)
    def Network_Launch(self, data):
        name = data['player_name']
        self._server.Start_Game(name)
    def Network_Nominate(self, data): 
        print data
        name = data['player_name']
        self._server.Nominate(name)
        
class WolvesServer(Server):
    channelClass = ClientChannel
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = []
        self.start_time = 'NA'
        self.timer_last = 'NA'
        self.timer_channel = 'NA'
    def Connected(self, channel, addr):
        print "New Connection: ", channel
        self.channel = channel
    def Add_player(self, name):
        if len(Game.player_channel) == 0:
            self.game = Game(name, self.channel)
        else:
            self.game.add_player(name, self.channel)
        for channel in self.game.player_channel:
            channel.Send({'action': 'reg', 'player_names': self.game.player_name})
    def Start_Game(self, name):
        if (name == self.game.admin) and not self.game.start_game:
            self.game.start_game = True
            roles = self.game.roles[:]
            random.shuffle(roles)
            #create the countdown timer for compain
            self.start_time = datetime.datetime.now()
            self.timer_last = 15
            self.timer_channel = self.game.player_channel
            role_id = 0
            #send the roles to players
            for channel in self.game.player_channel:
                channel.Send({'action': 'Start_Game', 'role': roles[role_id], 'timer': self.timer_last})
                role_id += 1
    def Nominate(self, name):
        self.game.candidate[name] = 0
        for channel in self.game.player_channel:
            channel.Send({'action': 'Nominate', 'name': name})
    #a timer, deactivate the launch button in specified channels when time is up    
    def Timer(self): #last_time in secs #if self.start_time is NA, means the timer is not started
        if self.start_time != 'NA': 
            if (datetime.datetime.now() - self.start_time).seconds > self.timer_last:
                for channel in self.timer_channel:
                    channel.Send({'action': 'Deactivate'})
                    self.start_time = 'NA'
                   
class Game:
    admin = 'xukang'
    roles = ["Prophet", "Wolf", "Wolf", "Wolf_King", "Witch", "Civilian", "Civilian"]
    player_channel = []
    player_name = []
    candidate = {}
    start_game = False
    def __init__(self, name, channel):
        Game.player_name.append(name)
        Game.player_channel.append(channel)
        print "Players: ", Game.player_name, Game.player_channel
    def add_player(self, name, channel):
        Game.player_name.append(name)
        Game.player_channel.append(channel)
        print "Players: ", Game.player_name, Game.player_channel
        
print "STARTING SERVER ON LOCALHOST"
wolvesServer = WolvesServer()
while True:
    wolvesServer.Pump()
    wolvesServer.Timer()
    sleep(0.01)
    