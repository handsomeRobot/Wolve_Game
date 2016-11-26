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
        self.candidate = []
        self.playerPhoto = {'xukang': 'Resources/xukang.jpg', 'panfeng': 'Resources/panfeng.jpg'}
        self.playerPos = {}
        self.name = "NA"
        self.role = "NA"
        self.connecting = False
        self.start_game = False
        self.nominate = False
        self.daytime = "Day"
        self.timer_last = 'NA'
        self.timer_start = 'NA'
        self.width, self.height = 800, 600
        self.xNum, self.yNum = 9, 7
        self.publicWidth, self.publicHeight = self.width, int(self.height * (7 / float(8)))
        self.xMargin, self.yMargin = 0.05, 0.05 #with respect to the size of rect
        self.mouse_click = 0
        self.bgs = []
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
        self.nomination = self.name
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
        #initilize the pos of player photos
        for player in self.players:
            pos_x = self.players.index(player) % self.xNum + 1
            pos_y = self.players.index(player) / self.xNum
            self.playerPos[player] = [pos_x, pos_y]

    def Network_Start_Game(self, data):
        sleep(0.3)
        self.start_game = True
        self.bgIndex += 1
        self.role = data['role']
        self.hint1 = "You are " + self.role
        self.hint2 = "Press enter to compain."
        self.nominate = True
        self.timer_last = data['timer']
        self.timer_start = datetime.datetime.now()
    
    # remove choice
    def Network_Deactivate(self, data):
        self.choice = False
        # put the candidates in the first col
        if self.nominate:
            self.nominate = False
            for player in self.players:
                self.playerPos[player] = "NA"  
                if player in self.candidate:
                    pos_x = 0
                    pos_y = self.candidate.index(player) / self.xNum
                    self.playerPos[player] = [pos_x, pos_y]
        self.hint2 = 'Please vote.'
        
    # add candidate
    def Network_Nominate(self, data):
        name = data["name"]
        print "get name", name
        self.candidate.append(name)
    
    def resize(self, graph, destSize):
        size = graph.get_rect().size
        times = max(size[0] / float(destSize[0]), \
                    size[1] / float(destSize[1]))
        graph = pygame.transform.scale(graph, (int(size[0] / times), int(size[1] / times)))
        return graph
    
    def initGraphics(self):
        #load wallpapers
        self.wolfKill = pygame.image.load("Resources/wolfkill.jpg")
        self.bgs.append(self.wolfKill)
        self.sadRobot = pygame.image.load("Resources/sadrobot.jpg")
        self.bgs.append(self.sadRobot)
        self.wait = pygame.image.load("Resources/waiting.jpg")
        self.bgs.append(self.wait)
        self.dock = pygame.image.load("Resources/dock.jpg")
        self.bgs.append(self.dock)
        #resize the wallpapers
        for i in range(len(self.bgs)):
            if i != 2:
                self.bgs[i] = self.resize(graph = self.bgs[i], \
                                 destSize = [self.publicWidth, self.publicHeight])
            else: self.bgs[i] = pygame.transform.scale(self.bgs[i],\
                                   [self.publicWidth, self.publicHeight])
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
        
    def drawBg(self, graph):
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
        #display countdown timer
        if timer != 'NA':
            timer = str(self.timer_last - (datetime.datetime.now() - self.timer_start).seconds)
            if self.timer_last - (datetime.datetime.now() - self.timer_start).seconds > -1:
                timer_message = myFont.render(timer, 50, (255, 255, 255))
                self.screen.blit(timer_message, (self.width / 2, self.publicHeight + (self.height - self.publicHeight) / 2))
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
        self.drawBg(graph = self.bgs[self.bgIndex])
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
                self.bgIndex += 1
                if self.mouse_click == 1:
                    self.hint1 = "Don't you panic..."
                    self.hint2 = "Click to continue..."
                elif self.mouse_click == 2:
                    self.hint1 = "***Selling for ads***"
                    self.hint2 = "Waiting for other players..."
        if self.mouse_click == 2:
            #draw the photos of players
            for player in self.players:
                photo = pygame.image.load(self.playerPhoto[player])
                photo = self.resize(graph = photo, destSize = self.destPhotoSize)
                if self.playerPos[player] != "NA":
                    self.drawPhoto(photo, pos = self.playerPos[player])
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
                if self.nominate and self.choice:
                    for i in range(self.xNum):
                        for j in range(self.yNum):
                            if self.coordSelected[i][j]:
                                for name, pos in self.playerPos.items():
                                    if pos == [i, j]:
                                        self.nomination = name
            #trace the mouse for the button
            #if mouse is in the button area
            if ((self.publicWidth - self.actButton.get_rect().size[0]) < mouse[0] and mouse[0] < self.width \
                   and self.publicHeight < mouse[1] and mouse[1] < self.height):
                #if mouse is pressed
                if self.choice and pygame.mouse.get_pressed()[0]:
                    if not self.start_game:
                        self.Send({'action': 'Launch', 'player_name': self.name})
                    elif self.nominate:
                        self.Send({'action': 'Nominate', 'player_name': self.nomination})
                        self.choice = False
                        self.hint2 = "Nominated."
        #update the screen
        pygame.display.flip()
        
wg = WolfGame()
while 1:
    wg.update()