import pygame
import math
import random

# Sorry but whenever you see the word deer in the code assume that it means bear
# TODO: nothing :)
class Player:

    def __init__(self, start, scroller, highscore):

        # create new global variables for the class
        # game display
        self.game_display = start.get_display()

        # high score
        self.high_score = highscore

        # switcher
        self.switcher = start

        # scroller controller
        self.scroller = scroller

        # game state
        self.running = True

        # colors, only main
        # TODO: implement more color RGB values, if updated, update corresponding method
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.grey = (128, 128, 128)
        self.pink = (255, 102, 178)
        self.blue = (0, 0, 255)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.purple = (127, 0, 255)
        self.yellow = (255, 255, 0)
        self.teal = (0, 204, 204)
        self.orange = (255, 128, 0)
        self.health_color = self.green
        # player coordinates and properties
        self.player_x = int(start.get_width() / 2)
        self.player_y = int(start.get_height() / 2)
        self.old_x = self.player_x
        self.old_y = self.player_y
        self.player_width = 80
        self.player_height = 40
        self.player_speed_x = 0
        self.player_speed_y = 0
        self.move_speed = 1
        self.player_health = 100

        # FPS controllers (note start speed should always be 60 / 5 so, 1 / 300
        self.clock = pygame.time.Clock()
        self.fps = 60

        # screen values
        self.width = start.get_width()
        self.height = start.get_height()

        # rotation for car
        self.angle = 90

        # car image and some additional properties
        self.car1 = CarPicker.get_car()
        # for testing self.car1 = self.car1.convert()
        self.car_copy = self.car1
        self.player_rect = self.car1.get_rect()
        self.player_rect.x = self.player_x
        self.player_rect.y = self.player_y
        self.update_size()

        # friction
        self.slowing_up = False
        self.slowing_down = False

        # car current gear
        self.car_gear = 1

        # screen text
        self.my_font = pygame.font.SysFont("Fixedsys", 30)

        # screen
        self.screen_y = 0
        self.old_screen_y = -790
        self.screen = self.scroller.get_screen()
        self.old_screen = self.scroller.get_screen()

        # score
        self.score = 0

        # deer ai
        self.deer_sprite_x = 0 # same for all deers
        self.deer_timer = 0
        self.deers = 2 # must be > 1 and < 8
        self.deers_x = AiDeer.init_pos(self.deers)
        self.deers_rect = [0,0,0,0,0,0,0]
        self.deer_y = -25
        self.deer_speed = 2

        # sounds
        self.growl = pygame.mixer.Sound("Sounds\\growl.wav")
        self.car_noise = pygame.mixer.Sound("Sounds\\car.wav")


    def exit(self):
        pygame.quit()
        self.running = False
        quit()

    def game_loop(self):
        while self.running:
            for event in pygame.event.get():
                # handle input
                self.event_handler(event)

            # reprint canvas
            self.game_display.fill(self.white)

            # print background
            self.screen_picker()

            # update HUD
            # render text
            self.text_update()

            # process player
            self.player_update()

            # draw deer
            self.deer_update()

            # update display
            pygame.display.update()

            # FPS
            self.clock.tick(self.fps)

    def event_handler(self, e):
        if e.type == pygame.QUIT:
            self.exit()
        if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    self.player_speed_x = self.move_speed
                if e.key == pygame.K_RIGHT:
                    self.player_speed_x = -self.move_speed
                if e.key == pygame.K_UP:
                    self.player_speed_y = self.move_speed
                    pygame.mixer.Sound.play(self.car_noise)
                if e.key == pygame.K_DOWN:
                    self.player_speed_y = -self.move_speed
                if e.key == pygame.K_SPACE: # brakes
                    self.player_speed_y = 0
                    self.player_speed_x = 0
                if e.key == pygame.K_LSHIFT:
                    self.gear_up()
                if e.key == pygame.K_LCTRL:
                    self.gear_down()
        if e.type == pygame.KEYUP:
                if e.key == pygame.K_LEFT:
                    self.player_speed_x = 0
                if e.key == pygame.K_RIGHT:
                    self.player_speed_x = 0

    def gear_up(self):
        pygame.mixer.Sound.play(self.car_noise)

        if self.car_gear < 6:
            self.car_gear += 1
            self.move_speed += 1
            self.player_speed_y = self.move_speed

    def gear_down(self):
        if self.car_gear > 1:
            self.car_gear -= 1
            self.move_speed -= 1
            self.player_speed_y = -self.move_speed

    # also checks game over
    def check_valid_move(self):
        if self.player_rect.x < 100:
            self.player_rect.x = 100
            self.player_health -= 1
            self.score -= 1
        if self.player_rect.x > 500 - self.player_rect.width + 10:
            self.player_health -= 1
            self.score -= 1
            self.player_rect.x = 500 - self.player_rect.width + 10
        if self.player_rect.y < 0:
            self.player_rect.y = 0
        if self.player_rect.y > 600 - self.player_rect.height - 10:
            self.player_rect.y = 600 - self.player_rect.height - 10
        if self.player_health < 1:
            self.game_over()

    def update_size(self):
        self.car1 = pygame.transform.scale(self.car1, (self.player_width, self.player_height))
        self.car1 = pygame.transform.rotate(self.car1, -180)

    def rot_center(self, image, rect, angle):
        # rotate an image and keep it's center
        rot_image = pygame.transform.rotate(image, angle)
        rot_rect = rot_image.get_rect(center=rect.center)
        return rot_image,rot_rect

    def player_update(self):
        # update player position
        self.angle += self.player_speed_x
        self.player_x += math.cos(math.radians(self.angle)) * self.player_speed_y
        self.player_y += math.sin(math.radians(self.angle)) * self.player_speed_y * -1

        # check to make sure it's in bounds
        self.check_valid_move()

        # update player rectangle and change image to be printed's rotation
        self.player_rect = self.player_rect.move(self.player_x - self.old_x, self.player_y - self.old_y)
        self.car_copy, self.player_rect = self.rot_center(self.car1, self.player_rect, self.angle)

        # print image
        self.game_display.blit(self.car_copy, self.player_rect)

        # values store to tell difference from last call to current call when moving rectangle
        self.old_x = self.player_x
        self.old_y = self.player_y

        self.score += 1

    def screen_picker(self):
        if self.screen_y >= 800:
            self.screen_y = -790
            self.screen = self.scroller.get_screen()
        if self.old_screen_y >= 800:
            self.old_screen_y = -790
            self.old_screen = self.scroller.get_screen()

        self.game_display.blit(self.screen, (0,self.screen_y, self.width, self.height))
        self.game_display.blit(self.old_screen, (0,self.old_screen_y, self.width, self.height))
        self.screen_y += 5
        self.old_screen_y += 5

    def game_over(self):
        self.running = False
        if self.score > self.high_score:
            self.high_score = self.score
        self.switcher.run_menu(self.high_score)

    def text_update(self):
        if self.player_health > 75:
            self.health_color = self.green
        elif self.player_health > 50:
            self.health_color = self.yellow
        elif self.player_health > 30:
            self.health_color = self.orange
        else:
            self.health_color = self.red
        label = self.my_font.render("Gear " + str(self.car_gear), 1, self.white)
        label2 = self.my_font.render("<3 " + str(self.player_health), 1, self.health_color)
        label3 = self.my_font.render("Score " + str(self.score), 1, self.white)
        self.game_display.blit(label, (0, 0))
        self.game_display.blit(label2, (0, 50))
        self.game_display.blit(label3, (0, 100))

    def deer_update(self):
        # sprite sheet control
        for x in range(-1, self.deers - 1):
            self.deers_rect[x] = AiDeer.draw_deer(self.game_display, self.deers_x[x], self.deer_y, self.deer_sprite_x)
            if self.deer_timer == 7:
                self.deer_timer = 0
                if self.deer_sprite_x > 150:
                    self.deer_sprite_x = 0
                else:
                    self.deer_sprite_x += 56
        self.deer_timer += 1
        self.deer_y += self.deer_speed

        # check for collision
        for x in range(-1, self.deers - 1):
            if self.deers_rect[x].colliderect(self.player_rect):
                self.player_health -= 1
                pygame.mixer.Sound.play(self.growl)

        # check if they are off screen and upgrade difficulty
        # NOTE: when total deers increases you need to recall init_pos to not receive an error
        if self.deer_y > 625:
            self.difficulty()
            self.deer_y = -25
            self.deers_x = AiDeer.init_pos(self.deers)

    def difficulty(self):
        if self.deers < 5:
            self.deer_speed += 1
            self.deers += 1


# TODO: nothing :)
class Start:

    def __init__(self, title, width, height):
        # initialize pygame library
        pygame.init()

        # set up specific display properties
        self.game_display = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)

        # screen size
        self.width = width
        self.height = height

        # update display
        pygame.display.update()

        # hold state
        self.running = False

    def get_display(self):
        return self.game_display

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def run_game(self, high_score):
        scroll = Scroller()
        game = Player(self, scroll, high_score)
        game.game_loop()

    def run_menu(self, high_score):
        menu = Menu(self, high_score)
        menu.menu_loop()


# TODO: nothing :)
class Scroller:
    def __init__(self):
        self.screen1 = pygame.image.load("Images\\Racing_Road_Road_Base_Tree2.png")
        self.screen2 = pygame.image.load("Images\\Racing_Road_Road_Base_Tree1.png")
        self.screen3 = pygame.image.load("Images\\Racing_Road_Road_Base_Snow.png")
        self.screen4 = pygame.image.load("Images\\Racing_Road_Road_Base_Crash.png")
        self.screen5 = pygame.image.load("Images\\Racing_Road_Road_Base_Lake.png")
        self.screen6 = pygame.image.load("Images\\Racing_Road_Road_Base_Stop_Sign.png")
        self.screen7 = pygame.image.load("Images\\Racing_Road_Road_LongGrass.png")
        self.screen8 = pygame.image.load("Images\\Racing_Road_Road_Base_People.png")
        self.screens = [self.screen1, self.screen2, self.screen3, self.screen4, self.screen5, self.screen6,
                        self.screen7, self.screen8]

    def get_screen(self):
        x = random.randint(0,7)
        return self.screens[x]


# TODO: nothing :)
class CarPicker:
    @staticmethod
    def get_car():
        car_array= [pygame.image.load("Images\\Car1.png"), pygame.image.load("Images\\Car2.png"),
                    pygame.image.load("Images\\Car5.png"), pygame.image.load("Images\\Car3.png"),
                    pygame.image.load("Images\\Car4.png")]
        return car_array[random.randint(0, 4)]


# TODO: nothing
class AiDeer:
    @staticmethod
    def draw_deer(screen, x, y, cur_sprite_x):

        SPRT_RECT_X= cur_sprite_x
        SPRT_RECT_Y= 0
        # This is where the sprite is found on the sheet

        LEN_SPRT_X= 56
        LEN_SPRT_Y= 56
        # This is the length of the sprite

        sheet = pygame.image.load('Images\\bear_sheet.png')  # Load the sheet

        sheet.set_clip(pygame.Rect(SPRT_RECT_X, SPRT_RECT_Y, LEN_SPRT_X, LEN_SPRT_Y))  # Locate the sprite you want
        draw_me = sheet.subsurface(sheet.get_clip())  # Extract the sprite you want

        rect = pygame.Rect(x, y, 25, 25)  # Create the whole screen so you can draw on it

        screen.blit(draw_me,rect)

        return rect

    @staticmethod
    def init_pos(length):
        deer = [0,0,0,0,0,0,0]
        for x in range(-1, length - 1):  # deer > 1
            deer[x] = random.randint(100, 450)
            for i in range(-1, length - 1):
                while deer[x] > deer[i] - 25 and deer[x] < deer[i] + 25 and i != x:
                    deer[x] = random.randint(100, 450)
        return deer


# TODO: add handling for other options!!!
class Menu:

    def __init__(self, start, highscore):
        # window state and window
        self.game_display = start.get_display()
        self.menu_running = True

        # font for text
        self.my_font = pygame.font.SysFont("Fixedsys", 50)
        self.my_font2 = pygame.font.SysFont("Fixedsys", 25)

        # text animation
        self.start_txt = self.my_font.render("Exit", 1, (0,0,0))
        self.play_txt = self.my_font.render("Play", 1, (0,0,0))
        self.controls_txt = self.my_font.render("Controls", 1, (0,0,0))
        self.story_txt = self.my_font.render("Story", 1, (0,0,0))
        self.t_r = [self.start_txt.get_rect(), self.play_txt.get_rect(), self.controls_txt.get_rect(),
                    self.story_txt.get_rect()]
        self.t = ["Exit", "Play", "Controls", "Story"]

        # set array x and y vals
        self.t_r[0].x = 0
        self.t_r[1].x = 0
        self.t_r[2].x = 0
        self.t_r[3].x = 0
        self.t_r[0].y = 0
        self.t_r[1].y = 50
        self.t_r[2].y = 100
        self.t_r[3].y = 150

        # fps timer
        self.clock = pygame.time.Clock()

        # start to switch to game
        self.switcher = start

        # sounds
        self.snap = pygame.mixer.Sound("Sounds\\snap.wav")

        # high score
        self.score = highscore
        self.score_txt = self.my_font.render("High Score " + str(self.score), 1, (255,255,255))

        # menu screen
        self.br = pygame.image.load("Images\\Racing_Road_Road_Base_Main.png")

        # movie
        self.movie = pygame.movie.Movie("Videos\\The_story_movie.mpg")

        self.movie_screen = pygame.Surface(self.movie.get_size()).convert()

        self.movie.set_display(self.movie_screen)
        self.movie_x = 800
        self.movie_y = 800



    def menu_loop(self):
        while self.menu_running:

            for event in pygame.event.get():
                # handle input
                self.event_handler(event)

            # reprint canvas
            self.game_display.fill((255, 255, 255))

            # print background
            self.game_display.blit(self.br, (0,0))

            # print Text
            self.check_mouse_print()

            # play movie
            if self.movie.get_busy():
                self.game_display.blit(self.movie_screen,(self.movie_x,self.movie_y))
            else:
                self.movie_x = 800
                self.movie_y = 800

            # update and activate all above expressions and statements
            pygame.display.update()

            # 30 fps
            self.clock.tick(30)

    def event_handler(self, e):
        if e.type == pygame.QUIT: # if user clicks upper right red x
            self.exit()
        if e.type == pygame.MOUSEBUTTONDOWN:
            for x in range(0, len(self.t_r)):
                if self.t_r[x].collidepoint(pygame.mouse.get_pos()):
                    self.process_click(x)

    def exit(self):
        pygame.quit()
        self.running = False
        quit()

    def check_mouse_print(self):
        for x in range(0, len(self.t_r)):
            if self.t_r[x].collidepoint(pygame.mouse.get_pos()):
                text = self.my_font.render(self.t[x], 1, (25, 255, 25))
                self.game_display.blit(text, (self.t_r[x].x, self.t_r[x].y))
            else:
                text = self.my_font.render(self.t[x], 1, (255, 255, 255))
                self.game_display.blit(text, (self.t_r[x].x, self.t_r[x].y))
        # high score
        self.game_display.blit(self.score_txt, (325,0))

    def process_click(self, n):
        pygame.mixer.Sound.play(self.snap)
        if n == 0:
            self.exit()
        if n == 1:
            self.menu_running = False
            self.switcher.run_game(self.score)
        if n == 3:
            # story
            self.movie.play()
            self.movie_x = 250
            self.movie_y = 325


# test
x = Start('Road Rage', 600, 600)
x.run_menu(0)
