import pygame
import PodSixNet
import datetime
import math
from pygame.locals import *
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep

class WolfGame(ConnectionListener):
    
    def __init__(self):
        self.player_name_ls = []
        self.dead_ls = []
        self.player_photo_dict = {'xukang': 'Resources/xukang.jpg', 'panfeng': 'Resources/panfeng.jpg'}
        self.player_position_dict = {}
        self.player_position_dict_2 = {}
        self.wolf_name_ls = []
        self.weapon_position_ls = {} 
        self.night_number = 0
        self.rect = [[0 for y in range(self.y_number)]for x in range(self.x_number)]
        self.rect_middle = [[0 for y in range(self.y_number)]for x in range(self.x_number)]
        self.selected_rect = [[False for y in range(self.y_number + 3)]for x in range(self.x_number)]
        self.weapon_choice = "NA" 
        self.name = "NA"
        self.role = "NA"
        self.nomination = "NA"
        self.sheriff = "NA"
        self.dead = False
        self.connecting = False
        self.game_started = False
        self.nominating = False
        self.voting = False
        self.night_activative = False
        self.day_activative = False
        self.running_sheriff = False
        self.choice = False
        self.weapon_restrict = "NA"
        self.target_restrict = "NA"
        self.day_time = "white"
        self.width, self.height = 800, 600
        self.x_number, self.y_number = 9, 7
        self.background_width, self.background_height = self.width, int(self.height * (7 / float(8)))
        self.x_margin, self.y_margin = 0.05, 0.05 #with respect to the size of rect
        self.click_count = 0
        self.background = "NA"
        self.hint1 = "Welcome from handsomeRobot."
        self.hint2 = "Click to continue..."
        #divide the public are into rects
        for i in range(self.x_number):
            for j in range(self.y_number):
                if i == 0:
                    self.rect[i][j] = ((2 / (float(self.x_number) + 1.0)) * self.background_width, \
                                       (1 / float(self.y_number)) * self.background_height)
                elif i > 0:
                    self.rect[i][j] = ((1 / (float(self.x_number) + 1.0)) * self.background_width, \
                                       (1 / float(self.y_number)) * self.background_height)
        #define the size of lines
        self.line_length_vertical = self.rect[1][0][1]
        self.line_length_horizontal = self.rect[1][0][0]
        self.line_width = 0.08 * self.rect[1][0][0] #with respect to the rect width
        #set default size of the photos of players
        raw_photo_size = (self.rect[1][0][0] * (1 - 2 * self.x_margin), \
                              self.rect[1][0][1] * (1 - 2 * self.y_margin))
        self.photo_size = [min(raw_photo_size[0], raw_photo_size[1]), min(raw_photo_size[0], raw_photo_size[1])]
        #setup the coords
        for i in range(self.x_number):
            for j in range(self.y_number):
                if i == 0:
                    self.rect_middle[i][j] = (self.rect[0][0][0] / 2.0, \
                                          self.rect[0][0][1] / 2.0 + j * self.rect[0][0][1])
                elif i > 0:
                    self.rect_middle[i][j] = (self.rect[1][0][0] / 2.0 \
                                          + self.rect[0][0][0] + (i - 1) * self.rect[1][0][0], 
                                         self.rect[0][0][1] / 2.0 + j * self.rect[0][0][1])
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
        self.initialize_graph()
    
    def initialize_graph(self):
        #load badges etc
        self.badge_picture = pygame.image.load("Resources/sheriff_badge.jpg")
        self.medicine_picture = pygame.image.load("Resources/med.png")
        self.poison_picture = pygame.image.load("Resources/toc.jpg")
        self.blood_picture = pygame.image.load("Resources/blood.png")
        self.wolf_picture = pygame.image.load("Resources/wolf.jpg")
        #load wallpapers
        self.red_wolf_background = pygame.image.load("Resources/wolfkill.jpg")
        self.red_wolf_background = self.resize(graph = self.red_wolf_background, \
                                 destSize = [self.background_width, self.background_height])
        self.background = self.red_wolf_background
        self.sad_robot_background = pygame.image.load("Resources/sadrobot.jpg")
        self.sad_robot_background = self.resize(graph = self.sad_robot_background, \
                                 destSize = [self.background_width, self.background_height])
        self.wait_background = pygame.image.load("Resources/waiting.jpg")
        self.wait_background = self.resize(graph = self.wait_background, \
                                 destSize = [self.background_width, self.background_height])
        self.night_background = pygame.image.load("Resources/night.png")
        self.night_background = self.resize(graph = self.night_background, \
                                 destSize = [self.background_width, self.background_height])
        self.night_black-white_background = pygame.image.load("Resources/night_black-white.bmp")
        self.night_black-white_background = self.resize(graph = self.night_black-white_background, \
                                 destSize = [self.background_width, self.background_height])
        self.gun_badge_background = pygame.image.load("Resources/gun and badge.jpg")
        self.gun_badge_background = self.resize(graph = self.gun_badge_background, \
                                 destSize = [self.background_width, self.background_height])
        self.court_background = pygame.image.load("Resources/court.jpg")
        self.court_background = self.resize(graph = self.court_background, \
                                 destSize = [self.background_width, self.background_height])
        self.court_black-white_background = pygame.image.load("Resources/court_black-white.bmp")
        self.court_black-white_background = self.resize(graph = self.court_black-white_background, \
                                 destSize = [self.background_width, self.background_height])
        #load and resize hint panel pic
        self.hint_panel = pygame.image.load("Resources/hintpanel.png")
        self.hint_panel = pygame.transform.scale(self.hint_panel, \
                                               [self.background_width, self.height - self.background_height])
        #load and resize button pic
        self.active_button = pygame.image.load("Resources/button.png")
        self.active_button = pygame.transform.scale(self.active_button, [self.background_width / 5, self.height - self.background_height])
        self.negative_button = pygame.image.load("Resources/negButton.png")
        self.negative_button = pygame.transform.scale(self.negative_button, [self.background_width / 5, self.height - self.background_height])
        #load and resize the quare lines
        self.cross_line_horizontal = pygame.image.load("Resources/crossOverLine.png")
        self.cross_line_horizontal = pygame.transform.scale(self.cross_line_horizontal, \
                             [int(self.line_width), int(self.line_length_vertical)])
        self.cross_line_vertical = pygame.transform.rotate(pygame.image.load("Resources/crossOverLine.png"), -90)
        self.cross_line_vertical = pygame.transform.scale(self.cross_line_vertical, \
                             [int(self.line_length_horizontal), int(self.line_width)])
        self.selected_line_horizontal = pygame.image.load("Resources/selectedLine.png")
        self.selected_line_horizontal = pygame.transform.scale(self.selected_line_horizontal, \
                             [int(self.line_width), int(self.line_length_vertical)])
        self.selected_line_vertical = pygame.transform.rotate(pygame.image.load("Resources/selectedLine.png"), -90)
        self.selected_line_vertical = pygame.transform.scale(self.selected_line_vertical, \
                             [int(self.line_length_horizontal), int(self.line_width)])
 
    def Network_reg(self, data):
        #retrive the registered player info
        self.player_name_ls = data['player_names']
        print "\n========================================================================================"
        print "Follow players registered."
        print self.player_name_ls
        print "==========================================================================================\n"
        #initilize the pos of player photos
        for player in self.player_name_ls:
            pos_x = self.player_name_ls.index(player) % self.x_number + 1
            pos_y = self.player_name_ls.index(player) / self.x_number
            self.player_position_dict[player] = [pos_x, pos_y]

    def Network_Start(self, data):
        sleep(0.3)
        self.background = self.night_background
        print "\n==============================================================================="
        print "Now starts the game."
        print "================================================================================\n"
        self.role = data['role']
        #report role to the server
        if self.role == 'Wolf'：
            self.send({'action': "Wolf_Collect", "sender": self.name})
        self.hint1 = "You are " + self.role
        
    def Network_Wolf_Collect(self, data):
        #print out wolf companies
        if self.role == 'Wolf':
            self.hint2 = self.hint2 + " with " + data['wolf'].remove(self.name)
    
    # remove choice
    def Network_Deactivate(self, data):
        self.choice = False
        self.nominating = False 
        self.voting = False

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
            self.player_position_dict_2 = self.player_position_dict.copy()
            for player in self.player_name_ls:
                self.player_position_dict[player] = "NA"
                if player in name:
                    pos_x = 0
                    pos_y = name.index(player)
                    self.player_position_dict[player] = [pos_x, pos_y]
            for player in self.dead_ls:
                self.player_position_dict[player] = "NA"
            self.hint2 = 'Please vote.'
            self.voting = True
        elif status == "over":
            if not again:
                self.sheriff = name
                self.player_position_dict = self.player_position_dict_2.copy()
            elif again:
                self.voting = True
                for player in self.player_name_ls:
                    self.player_position_dict[player] = "NA"
                    if player in name:
                        pos_x = 0
                        pos_y = name.index(player)
                        self.player_position_dict[player] = [pos_x, pos_y]
                self.hint2 = 'Please vote again.'
        elif status == "start":
            self.running_sheriff = True
            self.nominating = True
            self.hint2 = "Raise for Sheriff now."
            self.background = self.gun_badge_background

    #enter night/wake up upon calling from the server
    def Network_Night_Action(self, data):
        print "\n================================================================"
        print "In NIGHT_ACTION\n"
        print "Received from server: ", data
        print datetime.datetime.now()
        print "==================================================================\n"
        if not self.dead:
            self.background = self.night_background
            detail = data['detail']
            if detail == 'enter_night': #enter night
                self.hint2 = "Night."
                self.day_time = "night"
            elif detail == 'wake_up' and self.role == data['role']: #waked up
                self.hint2 = "Please action."
                self.night_activative = True
                try:
                    self.weapon_restrict = data['weapon_restrict'][self.role]
                except KeyError: 
                    pass
                try:
                    self.target_restrict = data['target_restrict'][self.role]
                except KeyError:
                    pass
        elif self.dead:
            self.background = self.night_black-white_background

    def Network_Day_Action(self, data):
        death_list = data["name"]
        for player in death_list:
            self.player_name_ls.remove(player)
            self.dead_ls.append(player)
        if self.name in death_list:
            self.dead = True
            self.hint1 = "You are out of game now."

    #for exile
    def Network_Exile(self, data):
        name = data["name"]    
        again = data["again"]
        if not again:
            playerPos = self.player_position_dict[:]
            for player in self.player_name_ls:
                self.player_position_dict[player] = "NA"
            self.hint2 = name + "is Exiled. Last words please."
            if (self.name == name) and (self.role == "Hunter"):
                self.hint1 = "You can take one with you." 
            self.player_position_dict = playerPos[:]
            del self.player_position_dict[name]
        elif again:
            for player in self.player_name_ls:
                self.player_position_dict[player] = "NA"
            for player in name:
                pos_x = 0
                pos_y = name.index(player)     
                self.player_position_dict[player] = [pox_x, pos_y]      
            self.hint2 = "Please vote again." 

    def resize(self, graph, destSize):
        size = graph.get_rect().size
        times = max(size[0] / float(destSize[0]), \
                    size[1] / float(destSize[1]))
        graph = pygame.transform.scale(graph, (int(size[0] / times), int(size[1] / times)))
        return graph
       
    def drawPhoto(self, photo, pos):
        size = photo.get_rect().size
        self.screen.blit(photo, [self.rect_middle[pos[0]][pos[1]][0] - size[0] / 2.0, \
                        self.rect_middle[pos[0]][pos[1]][1] - size[1] / 2.0])
        
    def drawBg(self):
        graph = self.background
        graphSize = graph.get_rect().size
        self.screen.blit(graph, \
                        [(self.background_width - graphSize[0]) / 2.0, \
                        (self.background_height - graphSize[1]) / 2.0])
            
    def drawSquare(self, pos, selected):
        coord = [self.rect_middle[pos[0]][pos[1]][0], self.rect_middle[pos[0]][pos[1]][1]]
        if not selected:
            self.screen.blit(self.cross_line_horizontal, [coord[0] - self.line_length_horizontal / 2,\
                            coord[1] - self.line_length_vertical / 2.0])
            self.screen.blit(self.cross_line_horizontal, \
                            [coord[0] + self.line_length_horizontal / 2.0 - self.line_width, \
                            coord[1] - self.line_length_vertical / 2])  
            self.screen.blit(self.cross_line_vertical, [coord[0] - self.line_length_horizontal / 2.0, \
                            coord[1] - self.line_length_vertical / 2.0])          
            self.screen.blit(self.cross_line_vertical, [coord[0] - self.line_length_horizontal / 2.0, \
                            coord[1] + self.line_length_vertical / 2.0 - self.line_width])  
        elif selected:
            self.screen.blit(self.selected_line_horizontal, [coord[0] - self.line_length_horizontal / 2,\
                            coord[1] - self.line_length_vertical / 2])
            self.screen.blit(self.selected_line_horizontal, \
                            [coord[0] + self.line_length_horizontal / 2 - self.line_width, \
                            coord[1] - self.line_length_vertical / 2])  
            self.screen.blit(self.selected_line_vertical, [coord[0] - self.line_length_horizontal / 2, \
                            coord[1] - self.line_length_vertical / 2])          
            self.screen.blit(self.selected_line_vertical, [coord[0] - self.line_length_horizontal / 2, \
                            coord[1] + self.line_length_vertical / 2 - self.line_width]) 
        
    def drawHUD(self):
        hint1 = self.hint1
        hint2 = self.hint2
        #draw the background for hint text
        self.screen.blit(self.hint_panel, [0, self.background_height])
        #create font
        myFont = pygame.font.SysFont(None, (self.height - self.background_height) / 2)
        #create text surface
        hint1_message = myFont.render(hint1, 10, (255, 255, 255))
        hint2_message = myFont.render(hint2, 10, (255, 255, 255))
        #draw text
        self.screen.blit(hint1_message, (0, self.background_height))
        self.screen.blit(hint2_message, (0, self.background_height + (self.height - self.background_height) / 2))
        #draw button
        if self.click_count == 2:
            if self.choice:
                self.screen.blit(self.active_button, [self.background_width - self.active_button.get_rect().size[0], self.background_height])
            else:
                self.screen.blit(self.negative_button, [self.background_width - self.active_button.get_rect().size[0], self.background_height])

    def createWindow(self, width, height):
        #update the window
        self.screen = pygame.display.set_mode((self.width, self.height), RESIZABLE)
        
    def update(self):
        connection.Pump()
        self.Pump()
        if self.connecting:
            self.Send({"player_name": self.name, "action": "Register"})
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
        if (self.game_started == False) and (len(self.player_name_ls) >= 2):
            self.choice = True
        for event in pygame.event.get():
        #quit if the quit button was pressed
            if event.type == pygame.QUIT:
                exit()
        #detect mouse click at the start of the game
            if (event.type == pygame.MOUSEBUTTONDOWN) and self.click_count < 2:
                self.click_count += 1
                if self.click_count == 1:
                    self.background = self.sad_robot_background
                    self.hint1 = "HandsomeRobot knows some sad stories."
                    self.hint2 = "Click to continue..."
                elif self.click_count == 2:
                    self.background = self.wait_background
                    self.hint1 = "Galaxy and friends, best things ever."
                    self.hint2 = "Waiting for other players..."
        if self.click_count == 2:
            #draw the photos of players
            for player in self.player_name_ls:
                photo = pygame.image.load(self.player_photo_ls[player])
                photo = self.resize(graph = photo, destSize = self.photo_size)
                if self.player_position_dict[player] != "NA":
                    self.drawPhoto(photo, pos = self.player_position_dict[player])
            for player in self.dead_ls:
                photo = pygame.image.load(self.player_photo_ls[player])
                photo = self.resize(graph = photo, destSize = self.photo_size)
                if self.player_position_dict[player] != "NA":
                    self.drawPhoto(photo, pos = self.player_position_dict[player])
            #specialize the kit of player 
            if self.role == "Witch":
               self.weapon_position_ls = {"Med": [self.x_number - 3, self.y_number], "Toc": [self.x_number - 2, self.y_number]}
               if self.night_activative and self.nomination != "NA":
                   self.medicine_picture = self.resize(self.medicine_picture, destSize = [self.photo_size[0], self.photo_size[1]])
                   self.poison_picture = self.resize(self.poison_picture, destSize = [self.photo_size[0], self.photo_size[1]])
                   self.drawPhoto(self.medicine_picture, self.weapon_position_ls["Med"])
                   self.drawPhoto(self.poison_picture, self.weapon_position_ls["Toc"])
            #draw the police_badge
            if self.sheriff in self.player_name_ls and self.player_position_dict[player] != "NA":
                playerPos = self.player_position_dict[self.sheriff]
                badge_size = [self.photo_size[0] / 4, self.photo_size[1] / 4]
                sheriff_badge = self.resize(graph = self.badge_picture, destSize = badge_size)
                self.screen.blit(sheriff_badge, [self.rect_middle[playerPos[0]][playerPos[1]][0] + self.photo_size[0] / 3.0 - badge_size[0] / 2.0, \
                                 self.rect_middle[playerPos[0]][playerPos[1]][1] - self.photo_size[0] / 3.0 - badge_size[1] / 2.0])
            #draw the blood for the death
            for player in self.dead_ls:
                if self.player_position_dict[player] != "NA":
                    playerPos = self.player_position_dict[player]
                    blood_size = [self.photo_size[0] / 1, self.photo_size[1] / 1]
                    blood = self.resize(graph = self.blood_picture, destSize = blood_size)
                    self.screen.blit(blood, [self.rect_middle[playerPos[0]][playerPos[1]][0] - blood_size[0] / 2.0, \
                                 self.rect_middle[playerPos[0]][playerPos[1]][1] - blood_size[1] / 2.0])   
            #draw the wolf for wolf
            for player in self.wolf_name_ls:
                if self.player_position_dict[player] != "NA":
                    playerPos = self.player_position_dict[player]
                    wolf_size = [self.photo_size[0] / 2, self.photo_size[1] / 2]
                    wolf = self.resize(graph = self.wolf_picture, destSize = wolf_size)
                    self.screen.blit(wolf, [self.rect_middle[playerPos[0]][playerPos[1]][0] - wolf_size[0] / 2.0 - self.photo_size[0] / 3.0, \
                                 self.rect_middle[playerPos[0]][playerPos[1]][1] - wolf_size[1] / 2.0 - self.photo_size[0] / 3.0])         
            #get the position of mouse
            mouse = pygame.mouse.get_pos()
            #trace the mouse coords in the publicArea
            if mouse[0] in range(self.background_width):
                if mouse[0] < self.rect[0][0][0]:
                    mousePosx = 0
                    mousePosy = int(mouse[1] / (self.rect[0][0][1])) 
                    mousePos = [mousePosx, mousePosy]
                else:
                    mousePosx = int((mouse[0] - self.rect[0][0][0]) / self.rect[1][0][0]) + 1
                    mousePosy = int(mouse[1] / (self.rect[0][0][1])) 
                    mousePos = [mousePosx, mousePosy]
                #record the press of the mouse
                if pygame.mouse.get_pressed()[0] and [mousePos[0], mousePos[1]] in self.player_position_dict.values():
                    self.selected_rect[mousePos[0]][mousePos[1]] = True
                elif pygame.mouse.get_pressed()[2]and [mousePos[0], mousePos[1]] in self.player_position_dict.values(): 
                    self.selected_rect[mousePos[0]][mousePos[1]] = False
                #draw the squares
                for i in range(self.x_number):
                    for j in range(self.y_number):
                        if (self.selected_rect[i][j] == False) and (mousePos == [i, j]):
                            self.drawSquare(pos = [i, j], selected = False)
                        elif self.selected_rect[i][j] == True:
                            self.drawSquare(pos = [i, j], selected = True)
                #choose the targeted player 
                if self.nominating or self.voting or self.night_activative or self.day_activative:
                    for i in range(self.x_number):
                        for j in range(self.y_number):
                            if self.selected_rect[i][j]:
                                for name, pos in self.player_position_dict.items():
                                    if pos == [i, j]:
                                        self.nomination = name
                    if self.night_activative or self.day_activative:
                        if self.target_restrict != "NA":
                            if self.nomination == self.target_restrict:
                                self.hint2 = "Prohibited Target."
                                self.nomination = "NA"
                #choose the selected weapon
                if self.night_activative and self.role == "Witch":
                    for i in range(self.x_number):
                        for j in range(self.y_number):
                            if self.selected_rect[i][j]:
                                for weapon, pos in self.weaponPos.items():
                                    if pos == [i, j]:
                                        self.weapon_choice = weapon                   
            #activte the choice button
            if self.nomination != "NA" and (self.nominating or self.voting or self.night_activative or self.day_activative):
                if self.night_activative and self.role == "Witch":
                    if self.weapon_choice != 'NA':
                        self.choice = True
                else:
                    self.choice = True
            #trace the mouse for the button
            #if mouse is in the button area
            if ((self.background_width - self.active_button.get_rect().size[0]) < mouse[0] and mouse[0] < self.width \
                   and self.background_height < mouse[1] and mouse[1] < self.height):
                #if mouse is pressed
                if self.choice and pygame.mouse.get_pressed()[0]:
                    if not self.game_started:
                        self.Send({'action': 'Start', 'sender': self.name})
                        self.choice = False
                        self.game_started = True
                        sleep(0.3)
                    elif self.nominating:
                        if self.running_sheriff:
                            self.Send({"action": "Sheriff", "player_name": self.nomination, "sender": self.name})
                            print "\n======================================================================"
                            print "Sent sheriff_nomination to server. Nomination: " + self.nomination + " Sender: " + self.name
                            print datetime.datetime.now()
                            print "========================================================================\n"
                            self.choice = False   
                            self.nominating = False
                            self.nomination = "NA"
                            self.hint2 = "Nominated."
                            self.selected_rect = [[False for y in range(self.y_number + 3)]for x in range(self.x_number)]
                            sleep(0.3)
                        elif not self.running_sheriff:
                            self.Send({'action': 'Exile', 'player_name': self.nomination, "sender": self.name})
                            self.choice = False
                            self.nominating = False
                            self.nomination = "NA"
                            self.hint2 = "Nominated."
                            self.selected_rect = [[False for y in range(self.y_number + 3)]for x in range(self.x_number)]
                            sleep(0.3)
                    elif self.voting:
                        self.Send({'action': 'Sheriff', 'player_name': self.nomination, 'sender': self.name})
                        print "\n============================================================================="
                        print "Sent sheriff_voting to server. Vote: " + self.nomination + " Sender: " + self.name
                        print datetime.datetime.now()
                        print "==============================================================================\n"
                        self.choice = False
                        self.voting = False
                        self.nomination = "NA"
                        self.hint2 = "Voted."
                        self.selected_rect = [[False for y in range(self.y_number + 3)]for x in range(self.x_number)]
                        sleep(0.3)
                    elif self.night_activative:
                        self.Send({'action': "Night_Special", 'player_name': self.nomination, "sender": self.name, "role": self.role, "weapon": self.weapon_choice})
                        self.night_activative = False
                        self.choice = False
                        self.hint2 = "Acted"
                        sleep(0.3)
                        
                        
        #update the screen
        pygame.display.flip()
        
wg = WolfGame()
while 1:
    wg.update()