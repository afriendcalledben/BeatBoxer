#!/usr/bin/env python
import os
import serial
import pygame
import time

gameState = 0

END_MUSIC_EVENT = pygame.USEREVENT + 0

pygame.init()
pygame.display.init()
pygame.mixer.init()
pygame.mouse.set_visible(False)
game_display = pygame.display.set_mode((480,320), pygame.FULLSCREEN | pygame.HWSURFACE)
try:
    leftSer = serial.Serial('/dev/ttyUSB1', 9600)
    rightSer = serial.Serial('/dev/ttyUSB0', 9600)
    #leftSer = serial.Serial('COM4', 9600)
    #rightSer = serial.Serial('COM5', 9600)
except:
    print("Please ensure the controllers are connected.")
    exit()

os.chdir("/home/pi/BeatBoxer")

bg = pygame.image.load("bg.png")
response_1 = pygame.image.load("response_1.png")
response_2 = pygame.image.load("response_2.png")
response_3 = pygame.image.load("response_3.png")
response_4 = pygame.image.load("response_4.png")
response_5 = pygame.image.load("response_5.png")
score_1 = pygame.image.load("score_1.png")
score_2 = pygame.image.load("score_2.png")
score_3 = pygame.image.load("score_3.png")
score_4 = pygame.image.load("score_4.png")
score_5 = pygame.image.load("score_5.png")
title = pygame.image.load("title.png")
title_action = pygame.image.load("title_action.png")
title_action_2 = pygame.image.load("title_action_2.png")
intro_ready = pygame.image.load("intro_ready.png")
intro_set = pygame.image.load("intro_set.png")
intro_ko = pygame.image.load("intro_ko.png")
gloveL = pygame.image.load("left_glove.png")
gloveR = pygame.image.load("right_glove.png")

pygame.mixer.music.load('song.mp3')
#pygame.mixer.music.set_volume(0.0)
pygame.mixer.music.set_endevent(END_MUSIC_EVENT)

pygame.font.init() # you have to call this at the start,
                   # if you want to use this module.
myfont = pygame.font.SysFont('Comic Sans MS', 30)

action_switch = 0
title_timer = time.time()

intro_timer = 0
intro_switch = 0

curr_event_L = 0
events_times_L = [8093, 14093, 16558, 18556, 20548, 22561, 25552, 27587, 33515, 34536, 36570, 40522, 44479, 46572, 52586, 62588, 66031, 70546, 76030, 79554, 82073, 88086, 95602, 96577, 100548, 106079, 108061, 110550, 118507, 124582, 135992]
events_done_L = []
curr_event_R = 0
events_times_R = [10093 , 12093, 17567, 19563, 24555, 26572, 28586, 30488, 32524, 35534, 38571, 42542, 46566, 54508, 60556, 68106, 71579, 74039, 78548, 86028, 89051, 91062, 94584, 102529, 105077, 107057, 111537, 116557, 126559, 135987]
events_done_R = []

response_L = 0
response_L_timer = 0
response_R = 0
response_R_timer = 0

trigger_timer = 0

scores_L = []
scores_R = []

for i in events_times_L:
    events_done_L.append(0)
for i in events_times_R:
    events_done_R.append(0)

hold_events_L = []
hold_events_R = []

leftSer.write('1');
rightSer.write('1');

while True:
    if (gameState == 2):
        game_display.fill((255,255,255))
        game_display.blit(bg, (0, 0))
    else:
        game_display.fill((0,42,255))
    leftMessage = ''
    rightMessage = ''
    if (leftSer.in_waiting > 0):
        leftMessage = leftSer.read(leftSer.in_waiting)
    if (rightSer.in_waiting > 0):
        rightMessage = rightSer.read(rightSer.in_waiting)
    if gameState == 0:
        game_display.blit(title, (240, 0))
        if (action_switch == 0):
            game_display.blit(title_action, (0, 0))
        else:
            game_display.blit(title_action_2, (0, 0))
        if (time.time() - title_timer > 1):
            title_timer = time.time()
            if (action_switch == 0):
                action_switch = 1
            else:
                action_switch = 0
        game_display.blit(title, (240, 0))
        if (leftMessage == "*" or rightMessage == "*"):
            intro_switch = 0
            intro_timer = time.time()
            leftSer.write('b');
            rightSer.write('b');
            gameState = 1
    if gameState == 1:
        if (intro_switch == 0):
            game_display.blit(intro_ready, (0, 0))
        elif (intro_switch == 1):
            game_display.blit(intro_set, (0, 0))
        elif (intro_switch > 1):
            game_display.blit(intro_ko, (0, 0))
        if (intro_switch == 4):
            pygame.mixer.music.play(0, 0.0)
            gameState = 2
        if (time.time() - intro_timer > 1):
            intro_switch = intro_switch + 1
            intro_timer = time.time()
    if gameState == 2:
        pos = pygame.mixer.music.get_pos()
        textsurface = myfont.render(str(pos), False, (0, 0, 0))
        if (curr_event_L < len(events_times_L)):
            ltime = events_times_L[curr_event_L]
            if (pos > ltime - 600 and pos < ltime + 300):
                if (events_done_L[curr_event_L] == 0):
                    leftSer.write('c')
                    events_done_L[curr_event_L] = 1
                glpos = - int((ltime - pos) / 5)
                if (glpos > 0):
                    glpos = 0
                game_display.blit(gloveL, (glpos,0))
            if (pos > ltime + 300):
                if (len(scores_L) == curr_event_L):
                    scores_L.append(6)
                curr_event_L = curr_event_L + 1
        if (curr_event_R < len(events_times_R)):
            rtime = events_times_R[curr_event_R]
            if (pos > rtime - 600 and pos < rtime + 300):
                if (events_done_R[curr_event_R] == 0):
                    rightSer.write('c')
                    events_done_R[curr_event_R] = 1
                grpos = - int((rtime - pos) / 5)
                if (grpos > 0):
                    grpos = 0
                game_display.blit(gloveR, (grpos,160))
            if (pos > rtime + 300):
                if (len(scores_R) == curr_event_R):
                    scores_R.append(6)
                curr_event_R = curr_event_R + 1
            if (len(leftMessage) > 0):
                response_L = int(leftMessage)
                scores_L.append(response_L)
                response_L_timer = time.time()
            if (len(rightMessage) > 0):
                response_R = int(rightMessage)
                scores_R.append(response_R)
                response_R_timer = time.time()
            if (response_L > 0):
                if (response_L == 1):
                    game_display.blit(response_1, (240,40))
                if (response_L == 2):
                    game_display.blit(response_2, (240,40))
                if (response_L == 3):
                    game_display.blit(response_3, (240,40))
                if (response_L == 4):
                    game_display.blit(response_4, (240,40))
                if (response_L == 5):
                    game_display.blit(response_5, (240,40))
                if (time.time() - response_L_timer > 1):
                    response_L = 0
            if (response_R > 0):
                if (response_R == 1):
                    game_display.blit(response_1, (240,160))
                if (response_R == 2):
                    game_display.blit(response_2, (240,160))
                if (response_R == 3):
                    game_display.blit(response_3, (240,160))
                if (response_R == 4):
                    game_display.blit(response_4, (240,160))
                if (response_R == 5):
                    game_display.blit(response_5, (240,160))
                if (time.time() - response_R_timer > 1):
                    response_R = 0
    if (gameState == 3):
        final_score_list = scores_L + scores_R
        final_score = int(float(sum(final_score_list))/float(len(final_score_list)))
        if (final_score == 1):
            game_display.blit(score_1, (0,0))
        if (final_score == 2):
            game_display.blit(score_2, (0,0))
        if (final_score == 3):
            game_display.blit(score_3, (0,0))
        if (final_score == 4):
            game_display.blit(score_4, (0,0))
        if (final_score >= 5):
            game_display.blit(score_5, (0,0))
        if (leftMessage == "*" or rightMessage == "*"):
            action_switch = 0
            curr_event_L = 0
            events_done_L = []
            curr_event_R = 0
            events_done_R = []
            response_L = 0
            response_L_timer = 0
            response_R = 0
            response_R_timer = 0
            scores_L = []
            scores_R = []
            for i in events_times_L:
                events_done_L.append(0)
            for i in events_times_R:
                events_done_R.append(0)
            hold_events_L = []
            hold_events_R = []
            title_timer = time.time()
            gameState = 0
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == END_MUSIC_EVENT:
            print("SONG END")
            pygame.mixer.music.rewind()
            leftSer.write('a')
            rightSer.write('a')
            gameState = 3
        if event.type == pygame.QUIT:
            pygame.mouse.set_visible(True)
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                print("A")
                hold_events_L.append(pygame.mixer.music.get_pos())
                #leftSer.write('1')
            if event.key == pygame.K_s:
                print("S")
                hold_events_R.append(pygame.mixer.music.get_pos())
                #rightSer.write('1')
            if event.key == pygame.K_SPACE:
                print(hold_events_L);
                print(hold_events_R);
                #rightSer.write('1')
            if event.key == pygame.K_q:
                pygame.quit()
