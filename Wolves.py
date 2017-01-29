import pygame
import PodSixNet
import datetime
import math
from pygame.locals import *
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep

class WolfGame(ConnectionListener):
    
    def __init__(self):
        self.players = []
        self.death = []
        self.candidate = []
        self.playerPhoto = {'xukang': 'Resources/xukang.jpg', 'panfeng': 'Resources/panfeng.jpg'}
        self.playerPos = {}
        self.playerPos_2 = {}
        self.wolves = []
        self.weapon_choice = "NA"
        self.weapon_pos = {}  
        self.name = "NA"
        self.role = "NA"
        self.nomination = "NA"
        self.sheriff = "NA"
        self.dead = False
        self.connecting = False
        self.start_game = False
        self.nominate = False
        self.vote = False
        self.night_special = False
        self.day_special = False
        self.run_sheriff = False
        self.weapon_restrict = "NA"
        self.target_restrict = "NA"
        self.daytime = "Sunlight"
        self.timer_last = 'NA'
        self.timer_start = 'NA'
        self.width, self.height = 800, 600
        self.xNum, self.yNum = 9, 7
        self.publicWidth, self.publicHeight = self.width, int(self.height * (7 / float(8)))
        self.xMargin, self.yMargin = 0.05, 0.05 #with respect to the size of rect
        self.mouse_click = 0
        self.bg = "NA"
        self.bgIndex = 0
        self.hint1 = "Hope you enjoy! by handsomeRbt"
        self.hint2 = "Click to continue..."
        self.choice = False
        self.rects = [[0 for y in range(self.yNum)]for x in range(self.xNum)]
        self.middles = [[0 for y in range(self.yNum)]for x in range(self.xNum)]
        self.coordSelected = [[False for y in range(self.yNum + 3)]for x in range(self.xNum)]
        #divide the public are into rects
        for i in range(self.xNum):
            for j in range(self.yNum):
                if i == 0:
                    self.rects[i][j] = ((2 / (float(self.xNum) + 1.0)) * self.publicWidth, \
                                       (1 / float(self.yNum)) * self.publicHeight)
                elif i > 0:
                    self.rects[i][j] = ((1 / (float(self.xNum) + 1.0)) * self.publicWidth, \
                                       (1 / float(self.yNum)) * self.publicHeight)
        #define the size of lines
        self.lineLengthV = self.rects[1][0][1]
        self.lineLengthH = self.rects[1][0][0]
        self.lineWidth = 0.08 * self.rects[1][0][0] #with respect to the rect width
        #set default size of the photos of players
        rectPhotoSize = (self.rects[1][0][0] * (1 - 2 * self.xMargin), \
                              self.rects[1][0][1] * (1 - 2 * self.yMargin))
        self.destPhotoSize = [min(rectPhotoSize[0], rectPhotoSize[1]), min(rectPhotoSize[0], rectPhotoSize[1])]
        #setup the coords
        for i in range(self.xNum):
            for j in range(self.yNum):
                if i == 0:
                    self.middles[i][j] = (self.rects[0][0][0] / 2.0, \
                                          self.rects[0][0][1] / 2.0 + j * self.rects[0][0][1])
                elif i > 0:
                    self.middles[i][j] = (self.rects[1][0][0] / 2.0 \
                                          + self.rects[0][0][0] + (i - 1) * self.rects[1][0][0], 
                                         self.rects[0][0][1] / 2.0 + j * self.rects[0][0][1])
        #init pygame module
        pygame.init()
        pygame.font.init()
        #intilize conncetion with server.py
        self.Connect()
        print "Connected to server."    
        print "Please input your name: "
        #set and send to server player name
        self.name = raw_input()
        self.connecting = True
        #initilize the screen
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Wolves")
        #initilize pygame clock
        self.clock = pygame.time.Clock()
        #initilize the graphs
        self.initGraphics()
 
    def Network_reg(self, data):
        #retrive the registered player info
        self.players = data['player_names']
        print self.players
        #initilize the pos of player photos
        for player in self.players:
            pos_x = self.players.index(player) % self.xNum + 1
            pos_y = self.players.index(player) / self.xNum
            self.playerPos[player] = [pos_x, pos_y]

    def Network_Start(self, data):
        sleep(0.3)
        self.bg = self.moonlight
        print "start"
        self.role = data['role']
        self.hint1 = "You are " + self.role
        self.hint2 = "Night."
        self.daytime = "Moonlight"
    
    # remove choice
    def Network_Deactivate(self, data):
        self.choice = False
        self.nominate = False 
        self.vote = False
    
    def Network_Test(self, data):
        print "\n=============================================================================="
        print "Communication channel is clear."
        print datetime.datetime.now()
        print "===============================================================================\n"

    #for sheriff
    def Network_Sheriff(self, data):
        print "\n=============================================================================="
        print "Received Sheriff data: ", data
        print datetime.datetime.now()
        print "================================================================================\n"
        status = data["status"]
        name = data["name"]
        again = data["again"]
        if status == "vote":
            self.playerPos_2 = self.playerPos.copy()
            for player in self.players:
                self.playerPos[player] = "NA"
                if player in name:
                    pos_x = 0
                    pos_y = name.index(player)
                    self.playerPos[player] = [pos_x, pos_y]
            for player in self.death:
                self.playerPos[player] = "NA"
            self.hint2 = 'Please vote.'
            self.vote = True
        elif status == "over":
            if not again:
                self.sheriff = name
                self.playerPos = self.playerPos_2.copy()
                '''self.hint2 = "Now argue and exile."
                self.bg = self.court''' 
            elif again:
                self.vote = True
                for player in self.players:
                    self.playerPos[player] = "NA"
                    if player in name:
                        pos_x = 0
                        pos_y = name.index(player)
                        self.playerPos[player] = [pos_x, pos_y]
                self.hint2 = 'Please vote again.'
        elif status == "start":
            self.run_sheriff = True
            self.nominate = True
            self.hint2 = "Raise for Sheriff now."
            self.bg = self.gunNbadge

    #for night action 
    def Network_Night_Action(self, data):
        print "\n================================================================"
        print "NIGHT_ACTION\n"
        print "Received from server: ", data
        print datetime.datetime.now()
        print "==================================================================\n"
        if not self.dead:
            self.bg = self.moonlight
        elif self.dead:
            self.bg = self.moonlight_black-white
        nc_role = data["role"]
        self.hint2 = "Bloody Night."
        if "id" not in data.keys() and self.role == nc_role:
            self.hint2 = "Please action."
            self.night_special = True
            try:
                self.weapon_restrict = data['weapon_restrict'][self.role]
            except KeyError: 
                pass
            try:
                self.target_restrict = data['target_restrict'][self.role]
            except KeyError:
                pass
        elif "id" in data.keys() and self.role == nc_role:
            nc_id = data["id"]
            name = data["name"]
            if nc_id:
                self.wolves.append(name)

    def Network_Day_Action(self, data):
        death_list = data["name"]
        for player in death_list:
            self.players.remove(player)
            self.death.append(player)
        if self.name in death_list:
            self.dead = True
            self.hint1 = "You are out of game now."

    #for exile
    def Network_Exile(self, data):
        name = data["name"]    
        again = data["again"]
        if not again:
            playerPos = self.playerPos[:]
            for player in self.players:
                self.playerPos[player] = "NA"
            self.hint2 = name + "is Exiled. Last words please."
            if (self.name == name) and (self.role == "Hunter"):
                self.hint1 = "You can take one with you." 
            self.playerPos = playerPos[:]
            del self.playerPos[name]
        elif again:
            for player in self.players:
                self.playerPos[player] = "NA"
            for player in name:
                pos_x = 0
                pos_y = name.index(player)     
                self.playerPos[player] = [pox_x, pos_y]      
            self.hint2 = "Please vote again." 

    def resize(self, graph, destSize):
        size = graph.get_rect().size
        times = max(size[0] / float(destSize[0]), \
                    size[1] / float(destSize[1]))
        graph = pygame.transform.scale(graph, (int(size[0] / times), int(size[1] / times)))
        return graph
    
    def initGraphics(self):
        #load badges etc
        self.sheriff_badge = pygame.image.load("Resources/sheriff_badge.jpg")
        self.med = pygame.image.load("Resources/med.png")
        self.toc = pygame.image.load("Resources/toc.jpg")
        self.blood = pygame.image.load("Resources/blood.png")
        self.wolf = pygame.image.load("Resources/wolf.jpg")
        #load wallpapers
        self.wolfKill = pygame.image.load("Resources/wolfkill.jpg")
        self.wolfKill = self.resize(graph = self.wolfKill, \
                                 destSize = [self.publicWidth, self.publicHeight])
        self.bg = self.wolfKill
        self.sadRobot = pygame.image.load("Resources/sadrobot.jpg")
        self.sadRobot = self.resize(graph = self.sadRobot, \
                                 destSize = [self.publicWidth, self.publicHeight])
        self.wait = pygame.image.load("Resources/waiting.jpg")
        self.wait = self.resize(graph = self.wait, \
                                 destSize = [self.publicWidth, self.publicHeight])
        self.moonlight = pygame.image.load("Resources/night.png")
        self.moonlight = self.resize(graph = self.moonlight, \
                                 destSize = [self.publicWidth, self.publicHeight])
        self.moonlight_black-white = pygame.image.load("Resources/night_black-white.bmp")
        self.moonlight_black-white = self.resize(graph = self.moonlight_black-white, \
                                 destSize = [self.publicWidth, self.publicHeight])
        self.gunNbadge = pygame.image.load("Resources/gun and badge.jpg")
        self.gunNbadge = self.resize(graph = self.gunNbadge, \
                                 destSize = [self.publicWidth, self.publicHeight])
        self.court = pygame.image.load("Resources/court.jpg")
        self.court = self.resize(graph = self.court, \
                                 destSize = [self.publicWidth, self.publicHeight])
        self.court_black-white = pygame.image.load("Resources/court_black-white.bmp")
        self.court_black-white = self.resize(graph = self.court_black-white, \
                                 destSize = [self.publicWidth, self.publicHeight])
        #load and resize hint panel pic
        self.hintPanel = pygame.image.load("Resources/hintpanel.png")
        self.hintPanel = pygame.transform.scale(self.hintPanel, \
                                               [self.publicWidth, self.height - self.publicHeight])
        #load and resize button pic
        self.actButton = pygame.image.load("Resources/button.png")
        self.actButton = pygame.transform.scale(self.actButton, [self.publicWidth / 5, self.height - self.publicHeight])
        self.negButton = pygame.image.load("Resources/negButton.png")
        self.negButton = pygame.transform.scale(self.negButton, [self.publicWidth / 5, self.height - self.publicHeight])
        #load and resize the quare lines
        self.crossOverLine = pygame.image.load("Resources/crossOverLine.png")
        self.crossOverLine = pygame.transform.scale(self.crossOverLine, \
                             [int(self.lineWidth), int(self.lineLengthV)])
        self.crossOverLineRight = pygame.transform.rotate(pygame.image.load("Resources/crossOverLine.png"), -90)
        self.crossOverLineRight = pygame.transform.scale(self.crossOverLineRight, \
                             [int(self.lineLengthH), int(self.lineWidth)])
        self.selectedLine = pygame.image.load("Resources/selectedLine.png")
        self.selectedLine = pygame.transform.scale(self.selectedLine, \
                             [int(self.lineWidth), int(self.lineLengthV)])
        self.selectedLineRight = pygame.transform.rotate(pygame.image.load("Resources/selectedLine.png"), -90)
        self.selectedLineRight = pygame.transform.scale(self.selectedLineRight, \
                             [int(self.lineLengthH), int(self.lineWidth)])
       
    def drawPhoto(self, photo, pos):
        size = photo.get_rect().size
        self.screen.blit(photo, [self.middles[pos[0]][pos[1]][0] - size[0] / 2.0, \
                        self.middles[pos[0]][pos[1]][1] - size[1] / 2.0])
        
    def drawBg(self):
        graph = self.bg
        graphSize = graph.get_rect().size
        self.screen.blit(graph, \
                        [(self.publicWidth - graphSize[0]) / 2.0, \
                        (self.publicHeight - graphSize[1]) / 2.0])
            
    def drawSquare(self, pos, selected):
        coord = [self.middles[pos[0]][pos[1]][0], self.middles[pos[0]][pos[1]][1]]
        if not selected:
            self.screen.blit(self.crossOverLine, [coord[0] - self.lineLengthH / 2,\
                            coord[1] - self.lineLengthV / 2.0])
            self.screen.blit(self.crossOverLine, \
                            [coord[0] + self.lineLengthH / 2.0 - self.lineWidth, \
                            coord[1] - self.lineLengthV / 2])  
            self.screen.blit(self.crossOverLineRight, [coord[0] - self.lineLengthH / 2.0, \
                            coord[1] - self.lineLengthV / 2.0])          
            self.screen.blit(self.crossOverLineRight, [coord[0] - self.lineLengthH / 2.0, \
                            coord[1] + self.lineLengthV / 2.0 - self.lineWidth])  
        elif selected:
            self.screen.blit(self.selectedLine, [coord[0] - self.lineLengthH / 2,\
                            coord[1] - self.lineLengthV / 2])
            self.screen.blit(self.selectedLine, \
                            [coord[0] + self.lineLengthH / 2 - self.lineWidth, \
                            coord[1] - self.lineLengthV / 2])  
            self.screen.blit(self.selectedLineRight, [coord[0] - self.lineLengthH / 2, \
                            coord[1] - self.lineLengthV / 2])          
            self.screen.blit(self.selectedLineRight, [coord[0] - self.lineLengthH / 2, \
                            coord[1] + self.lineLengthV / 2 - self.lineWidth]) 
        
    def drawHUD(self):
        hint1 = self.hint1
        hint2 = self.hint2
        timer = self.timer_last
        #draw the background for hint text
        self.screen.blit(self.hintPanel, [0, self.publicHeight])
        #create font
        myFont = pygame.font.SysFont(None, (self.height - self.publicHeight) / 2)
        #create text surface
        hint1_message = myFont.render(hint1, 10, (255, 255, 255))
        hint2_message = myFont.render(hint2, 10, (255, 255, 255))
        #draw text
        self.screen.blit(hint1_message, (0, self.publicHeight))
        self.screen.blit(hint2_message, (0, self.publicHeight + (self.height - self.publicHeight) / 2))
        #draw button
        if self.mouse_click == 2:
            if self.choice:
                self.screen.blit(self.actButton, [self.publicWidth - self.actButton.get_rect().size[0], self.publicHeight])
            else:
                self.screen.blit(self.negButton, [self.publicWidth - self.actButton.get_rect().size[0], self.publicHeight])

    def createWindow(self, width, height):
        #update the window
        self.screen = pygame.display.set_mode((self.width, self.height), RESIZABLE)
        
    def update(self):
        connection.Pump()
        self.Pump()
        if self.connecting:
            self.Send({"player_name": self.name, "action": "reg"})
            self.connecting = False
        #sleep to make the game 60 fps
        self.clock.tick(60)
        #clear the screen
        self.screen.fill(0)
        #draw the graphs
        self.drawBg()
        #draw the text panel
        self.drawHUD()
        #choice for starting game
        if (self.start_game == False) and (len(self.players) >= 2):
            self.choice = True
        for event in pygame.event.get():
        #quit if the quit button was pressed
            if event.type == pygame.QUIT:
                exit()
        #detect mouse click at the start of the game
            if (event.type == pygame.MOUSEBUTTONDOWN) and self.mouse_click < 2:
                self.mouse_click += 1
                if self.mouse_click == 1:
                    self.bg = self.sadRobot
                    self.hint1 = "HandsomeRobot knows some sad stories."
                    self.hint2 = "Click to continue..."
                elif self.mouse_click == 2:
                    self.bg = self.wait
                    self.hint1 = "Galaxy and friends, best things ever."
                    self.hint2 = "Waiting for other players..."
        if self.mouse_click == 2:
            #draw the photos of players
            for player in self.players:
                photo = pygame.image.load(self.playerPhoto[player])
                photo = self.resize(graph = photo, destSize = self.destPhotoSize)
                if self.playerPos[player] != "NA":
                    self.drawPhoto(photo, pos = self.playerPos[player])
            for player in self.death:
                photo = pygame.image.load(self.playerPhoto[player])
                photo = self.resize(graph = photo, destSize = self.destPhotoSize)
                if self.playerPos[player] != "NA":
                    self.drawPhoto(photo, pos = self.playerPos[player])
            #specialize the kit of player 
            if self.role == "Witch":
               self.weapon_pos = {"Med": [self.xNum - 3, self.yNum], "Toc": [self.xNum - 2, self.yNum]}
               if self.night_special and self.nomination != "NA":
                   self.med = self.resize(self.med, destSize = [self.destPhotoSize[0], self.destPhotoSize[1]])
                   self.toc = self.resize(self.toc, destSize = [self.destPhotoSize[0], self.destPhotoSize[1]])
                   self.drawPhoto(self.med, self.weapon_pos["Med"])
                   self.drawPhoto(self.toc, self.weapon_pos["Toc"])
            #draw the police_badge
            if self.sheriff in self.players and self.playerPos[player] != "NA":
                playerPos = self.playerPos[self.sheriff]
                badge_size = [self.destPhotoSize[0] / 4, self.destPhotoSize[1] / 4]
                sheriff_badge = self.resize(graph = self.sheriff_badge, destSize = badge_size)
                self.screen.blit(sheriff_badge, [self.middles[playerPos[0]][playerPos[1]][0] + self.destPhotoSize[0] / 3.0 - badge_size[0] / 2.0, \
                                 self.middles[playerPos[0]][playerPos[1]][1] - self.destPhotoSize[0] / 3.0 - badge_size[1] / 2.0])
            #draw the blood for the death
            for player in self.death:
                if self.playerPos[player] != "NA":
                    playerPos = self.playerPos[player]
                    blood_size = [self.destPhotoSize[0] / 1, self.destPhotoSize[1] / 1]
                    blood = self.resize(graph = self.blood, destSize = blood_size)
                    self.screen.blit(blood, [self.middles[playerPos[0]][playerPos[1]][0] - blood_size[0] / 2.0, \
                                 self.middles[playerPos[0]][playerPos[1]][1] - blood_size[1] / 2.0])   
            #draw the wolf for wolf
            for player in self.wolves:
                if self.playerPos[player] != "NA":
                    playerPos = self.playerPos[player]
                    wolf_size = [self.destPhotoSize[0] / 2, self.destPhotoSize[1] / 2]
                    wolf = self.resize(graph = self.wolf, destSize = wolf_size)
                    self.screen.blit(wolf, [self.middles[playerPos[0]][playerPos[1]][0] - wolf_size[0] / 2.0 - self.destPhotoSize[0] / 3.0, \
                                 self.middles[playerPos[0]][playerPos[1]][1] - wolf_size[1] / 2.0 - self.destPhotoSize[0] / 3.0])         
            #get the position of mouse
            mouse = pygame.mouse.get_pos()
            #trace the mouse coords in the publicArea
            if mouse[0] in range(self.publicWidth):
                if mouse[0] < self.rects[0][0][0]:
                    mousePosx = 0
                    mousePosy = int(mouse[1] / (self.rects[0][0][1])) 
                    mousePos = [mousePosx, mousePosy]
                else:
                    mousePosx = int((mouse[0] - self.rects[0][0][0]) / self.rects[1][0][0]) + 1
                    mousePosy = int(mouse[1] / (self.rects[0][0][1])) 
                    mousePos = [mousePosx, mousePosy]
                #record the press of the mouse
                if pygame.mouse.get_pressed()[0] and [mousePos[0], mousePos[1]] in self.playerPos.values():
                    self.coordSelected[mousePos[0]][mousePos[1]] = True
                elif pygame.mouse.get_pressed()[2]and [mousePos[0], mousePos[1]] in self.playerPos.values(): 
                    self.coordSelected[mousePos[0]][mousePos[1]] = False
                #draw the squares
                for i in range(self.xNum):
                    for j in range(self.yNum):
                        if (self.coordSelected[i][j] == False) and (mousePos == [i, j]):
                            self.drawSquare(pos = [i, j], selected = False)
                        elif self.coordSelected[i][j] == True:
                            self.drawSquare(pos = [i, j], selected = True)
                #choose the targeted player 
                if self.nominate or self.vote or self.night_special or self.day_special:
                    for i in range(self.xNum):
                        for j in range(self.yNum):
                            if self.coordSelected[i][j]:
                                for name, pos in self.playerPos.items():
                                    if pos == [i, j]:
                                        self.nomination = name
                    if self.night_special or self.day_special:
                        if self.target_restrict != "NA":
                            if self.nomination == self.target_restrict:
                                self.hint2 = "Prohibited Target."
                                self.nomination = "NA"
                #choose the selected weapon
                if self.night_special and self.role == "Witch":
                    for i in range(self.xNum):
                        for j in range(self.yNum):
                            if self.coordSelected[i][j]:
                                for weapon, pos in self.weaponPos.items():
                                    if pos == [i, j]:
                                        self.weapon_choice = weapon                   
            #activte the choice button
            if self.nomination != "NA" and (self.nominate or self.vote or self.night_special or self.day_special):
                if self.night_special and self.role == "Witch":
                    if self.weapon_choice != 'NA':
                        self.choice = True
                else:
                    self.choice = True
            #trace the mouse for the button
            #if mouse is in the button area
            if ((self.publicWidth - self.actButton.get_rect().size[0]) < mouse[0] and mouse[0] < self.width \
                   and self.publicHeight < mouse[1] and mouse[1] < self.height):
                #if mouse is pressed
                if self.choice and pygame.mouse.get_pressed()[0]:
                    if not self.start_game:
                        self.Send({'action': 'Start', 'sender': self.name})
                        self.choice = False
                        self.start_game = True
                        sleep(0.3)
                    elif self.nominate:
                        if self.run_sheriff:
                            self.Send({"action": "Sheriff", "player_name": self.nomination, "sender": self.name})
                            print "\n======================================================================"
                            print "Sent sheriff_nomination to server. Nomination: " + self.nomination + " Sender: " + self.name
                            print datetime.datetime.now()
                            print "========================================================================\n"
                            self.choice = False   
                            self.nominate = False
                            self.nomination = "NA"
                            self.hint2 = "Nominated."
                            self.coordSelected = [[False for y in range(self.yNum + 3)]for x in range(self.xNum)]
                            sleep(0.3)
                        elif not self.run_sheriff:
                            self.Send({'action': 'Exile', 'player_name': self.nomination, "sender": self.name})
                            self.choice = False
                            self.nominate = False
                            self.nomination = "NA"
                            self.hint2 = "Nominated."
                            self.coordSelected = [[False for y in range(self.yNum + 3)]for x in range(self.xNum)]
                            sleep(0.3)
                    elif self.vote:
                        self.Send({'action': 'Sheriff', 'player_name': self.nomination, 'sender': self.name})
                        print "\n============================================================================="
                        print "Sent sheriff_voting to server. Vote: " + self.nomination + " Sender: " + self.name
                        print datetime.datetime.now()
                        print "==============================================================================\n"
                        self.choice = False
                        self.vote = False
                        self.nomination = "NA"
                        self.hint2 = "Voted."
                        self.coordSelected = [[False for y in range(self.yNum + 3)]for x in range(self.xNum)]
                        sleep(0.3)
                    elif self.night_special:
                        self.Send({'action': "Night_Special", 'player_name': self.nomination, "sender": self.name, "role": self.role, "weapon": self.weapon_choice})
                        self.night_special = False
                        self.choice = False
                        self.hint2 = "Acted"
                        sleep(0.3)
                        
                        
        #update the screen
        pygame.display.flip()
        
wg = WolfGame()
while 1:
    wg.update()