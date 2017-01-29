import PodSixNet
import datetime
import random
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from time import sleep

class Client_Channel(Channel):
    def Network(self, data):
        print data
    def Network_Register(self, data):
        print data
        name = data['player_name']
        self._server.Add_Player(name)
    def Network_Start(self, data):
        print data
        name = data["sender"]
        self._server.Start(name)
    def Wolf_Collect(self, data):
        print data
        name = data['sender']
        self._server.Wolf_Collect(name)
    def Network_Sheriff(self, data): 
        print data
        name = data['player_name']
        sender = data['sender']
        self._server.Sheriff(name, sender)
    def Network_Night_Action(self, data):
        print data  
        name = data['player_name']
        sender = data['sender']
        sender_role = data["role"]
        weapon = data["weapon"]
        self._server.Night_Action(name, sender_role, weapon, sender)
        
class Wolves_Server(Server):
    channelClass = ClientChannel
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.players = []
        self.start_time = 'NA'
        self.timer_last = 'NA'
        self.timer_channel = 'NA'
        self.channels = []
    def Connected(self, channel, addr):
        print "New Connection: ", channel
        if channel not in self.channels:
            self.channels.append(channel)
        print "self.channels: ", self.channels
    def Add_Player(self, name):
        if len(Game.player_channel_ls) == 0:
            self.game = Game(name, self.channels)
            print "\n============================================================================================"
            print "Open a game."
            print "channels in the game: ", self.game.player_channel_ls
            print "=============================================================================================\n"
        else:
            self.game.player_name_ls.append(name)
            self.game.not_vote_ls = self.game.player_name_ls[:]
            print "\n============================================================================================="
            print "Add new player: " + name 
            print "Players in the game now: ", self.game.player_name_ls
        for channel in self.game.player_channel_ls:
            channel.Send({'action': 'reg', 'player_names': self.game.player_name_ls})
    def Start(self, name):
        #collect the votes from all the players
        if name in self.game.not_vote_ls:
            self.game.not_vote_ls.remove(name)
        if (len(self.game.not_vote_ls) == 0) and not self.game.start_game:
            self.game.not_vote_ls = self.game.player_name_ls[:]
            self.game.start_game = True
            role_ls = self.game.role_ls[:]
            random.shuffle(role_ls)
            role_id = 0
            #send the roles to players
            for channel in self.game.player_channel_ls:
                channel.Send({'action': 'Start', 'role': role_ls[role_id]})
                role_id += 1
            #start night
            self.Night_Kindle()
    def Wolf_Collect(self, name): #record the wolve_player based on info from distributed players
        self.game.wolf_collect_ls.append(name)
        for channel in self.game.player_channel_ls:
            channel.Send({'action': "Wolf_Collect", 'wolf': self.game.wolf_collect_ls})
    def Sheriff(self, name, sender):
        #for sheriff
        if self.game.nominate_sheriff:
            if name == "give_up" and (sender in self.game.not_vote_ls):
                self.game.not_vote_ls.remove(sender)
            elif name != "give_up" and (sender in self.game.not_vote_ls):
                self.game.not_vote_ls.remove(sender)
                self.game.candidate_dict[name] = 0
            if len(self.game.not_vote_ls) == 0:
                self.game.not_vote_ls = self.game.player_name_ls[:]
                for channel in self.game.player_channel_ls:
                    channel.Send({"action": "Sheriff", "status": "vote", "name": self.game.candidate_dict.keys(), "again": "NA"})
                self.game.nominate_sheriff = False
        elif not self.game.nominate_sheriff:
            if name == "give_up" and (sender in self.game.not_vote_ls):
                self.game.not_vote_ls.remove(sender)
            elif name != "give_up" and (sender in self.game.not_vote_ls):
                self.game.not_vote_ls.remove(sender)
                self.game.candidate_dict[name] += 1
            if len(self.game.not_vote_ls) == 0:
                self.game.not_vote_ls = self.game.player_name_ls[:]
                winners = []
                for name, value in self.game.candidate_dict.items():
                    if value == max(self.game.candidate_dict.values()):
                        winners.append(name)
                if len(winners) == 1:
                    for channel in self.game.player_channel_ls:
                        channel.Send({"action": "Sheriff", "status": "over", "name": winners[0], "again": False})
                        print "\n==============================================================================="
                        print "Send to " + str(channel), {"action": "Sheriff", "status": "vote", "name": winners[0], "again": False}
                        print datetime.datetime.now()
                        print "=================================================================================\n"
                    self.game.sheriff = winners[0]
                    self.Night_Kindle() 
                elif len(winners) > 1:
                    print "F"
                    self.game.candidate_dict = {}
                    for winner in winners:
                        self.game.candidate_dict[winner] = 0
                    for channel in self.game.player_channel_ls:
                        channel.Send({"action": "Sheriff", "status": "vote", "name": winners, "again": True}) 
    def Night_Action(self, target, role, weapon, sender): #enter the night/distribute tasks/collect responses
        if self.game.day_time != 'night': #enter the night if not night
            print "\n============================================================="
            print "Start Night_Action."
            print datetime.datetime.now()
            print "===============================================================\n"
            self.game.day_time = 'night'
            for channel in self.game.player_channel_ls:
                channel.send({'action': 'Night_Action', 'detail': 'enter_night'})
        while True: #wake up individuals and collect their responses
            role = self.game.role_base_ls[self.game.role_base_ls_Index]
            target_restrict = self.game.target_restrict_dict
            weapon_restrict = self.game.weapon_restrict_dict
            if role in self.game.role_ls:
                for channel in self.game.player_channel_ls:
                    channel.Send({"action": "Night_Action", 'detail': 'wake_up', "role": role, "target_restrict": target_restrict, "weapon_restrict": weapon_restrict})
        if name in self.game.player_name_ls and sender in self.game.player_name_ls:
            if role == "Wolf":
                self.game.player_id_dict[sender] = "Wolf"
                self.game.night_event_dict[name] = "attacked"
                print "\n==================================================================================="
                print name + " is attacked by Wolf " + sender
                print datetime.datetime.now()
                print "====================================================================================\n"
            elif role == "Witch":
                self.game.player_id_dict[sender] = "Witch"
                if weapon == "Med":
                    if name in self.game.night_event_dict.keys() and self.game.night_event_dict[name] == "attacked":
                        del self.game.night_event_dict[name]
                        print "\n==================================================================================="
                        print name + " is cured by Witch " + sender
                        print datetime.datetime.now()
                        print "====================================================================================\n"
                    elif name not in self.game.night_event_dict.keys() or self.game.night_event_dict[name] != "attacked":
                        pass
                    self.game.weapon_restrict_dict[role] = ["Med"]
                elif weapon == "Toc":
                    self.game.night_event_dict[name] == "killed"
                    print "\n==================================================================================="
                    print name + " is tocxided by Witch " + sender
                    print datetime.datetime.now()
                    print "====================================================================================\n"
                    self.game.weapon_restrict_dict[role] == ["Toc"]
            elif role == "Prophet":
                self.game.player_id_dict[sender] = "Prophet"
                for channel in self.game.player_channel_ls:
                    channel.Send({"action": "Night_Kindle", "name": name, "id": self.game.player_id_dict[name] == "Wolf", \
                    "role": "Prophet"})
                print "\n========================================================================================="
                print self.game.player_id_dict[name] + " " + name + " is checked by Prophet " + sender
                print datetime.datetime.now()
                print "===========================================================================================\n"
        if self.game.role_base_ls_Index + 1 < len(self.game.role_base_ls):
            self.game.role_base_ls_Index += 1
            self.Night_Kindle()
        elif self.game.role_base_ls_Index + 1 == len(self.game.role_base_ls):
            self.game.role_base_ls_Index = 0
            self.Day_Action()
    def Day_Action(self):
        print "\n====================================================================="
        print "Day Light"
        print "night_event: ", self.game.night_event_dict
        print datetime.datetime.now()
        print "======================================================================\n"
        if self.game.nominate_sheriff != "already":
            for channel in self.game.player_channel_ls:
                channel.Send({"action": "Sheriff", "status": "start", "name": "NA", "again": "NA"})
                self.game.nominate_sheriff = True
        death_list = []
        for player, event in self.game.night_event_dict.items():
            if event == "attacked" or event == "killed":
                death_list.append(player)
        for channel in self.game.player_channel_ls:
            channel.Send({"action": "Day_Action", "name": death_list})
        death_list = []
    def Exile(self, name, sender):
        #for exile
        if name == "give_up" and (sender in self.game.not_vote_ls):
            self.game.not_vote_ls.remove(sender)
        elif name != "give_up" and (sender in self.game.not_vote_ls):
            if name not in self.game.candidate_dict.keys():
                self.game.candidate_dict[name] = 0
            elif name in self.game.candidate_dict.keys():
                self.game.candidate_dict[name] += 1
            self.game.not_vote_ls.remove(sender)
        if len(self.game.not_vote_ls) == 0:
            self.game.not_vote_ls = self.game.player_name_ls[:]
            winners = []
            for name, value in self.game.candidate_dict.items():
                if value == max(self.game.candidate_dict.values()):
                    winners.append(name)
            if len(winners) == 1:
                self.game.player_name_ls.remove(winners[0])
                for channel in self.game.player_channel_ls:
                    channel.Send({"action": "Exile", "name": winners[0], "again": False})
                    self.game.candidate_dict = {}
            elif len(winners) > 1:
                self.game.candidate_dict = {}
                for winner in winners:
                    self.game.candidate_dict[winner] = 0   
                for channel in self.game.player_channel_ls:
                    channel.Send({"action": "Exile", "name": winners, "again": True})     
                   
class Game:
    role_base_ls = ["Wolf", "Prophet", "Hunter", "Witch"]
    role_ls = ["Wolf",  "Prophet"]
    wolf_collect_ls = []
    role_base_ls_Index = 0
    night_number = 0
    night_event_dict = {}
    player_channel_ls = []
    player_name_ls = []
    player_id_dict = {}
    not_vote_ls = []
    candidate_dict = {}
    start_game = False
    day_time = "daylight"
    nominate_sheriff = False
    sheriff = "NA"
    target_restrict_dict = {}
    weapon_restrict_dict = {}
    def __init__(self, name, channel):
        Game.player_name_ls.append(name)
        Game.not_vote_ls = Game.player_name_ls[:]
        Game.player_channel_ls = channel
        print "Init Players: ", Game.player_name_ls, Game.player_channel_ls
 
print "\n==================================================================================================="       
print "STARTING SERVER ON LOCALHOST"
print "====================================================================================================\n"
Wolves_Server = Wolves_Server()
while True:
    Wolves_Server.Pump()
    sleep(0.01)
    