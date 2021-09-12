import pygame
import random
import button

pygame.init()

# frame_rate
clock = pygame.time.Clock()
fps = 60

# game window
bottom_panel = 150
screen_width = 800
screen_height = 400 + bottom_panel

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Battle')

# define game variables
current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 90
attack = False
potion = False
potion_effect = 15
clicked = False

game_over = 0 # game over = -1, win = 1

# load images

# def fonts
font = pygame.font.SysFont('Times New Roman', 26)

# def colors
red = (255, 0, 0)
green = (0, 255, 0)

custom_cursor = pygame.image.load('img/Icons/sword.png').convert_alpha()
potion_img = pygame.image.load('img/Icons/potion.png').convert_alpha()
restart_img = pygame.image.load('img/Icons/restart.png').convert_alpha()
#load victory and defeat images
victory_img = pygame.image.load('img/Icons/victory.png').convert_alpha()
defeat_img = pygame.image.load('img/Icons/defeat.png').convert_alpha()

# draw text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # move damage text up
        self.rect.y -= 1
        # del text after a few secs
        self.counter += 1
        if self.counter > 30:
            self.kill()


damage_text_group = pygame.sprite.Group()

# background images
background_forest_0 = pygame.image.load('img/Background/Forest1.png').convert_alpha()

# panel image
panel_img = pygame.image.load('img/Icons/panel.png').convert_alpha()


# function for drawing panel
def draw_panel():
    screen.blit(panel_img, (0, screen_height - bottom_panel))

    draw_text(f'{knight.name} HP: {knight.hp}', font, red, 100, screen_height - bottom_panel + 10)
    for count, i in enumerate(bandit_list):
        # show name and HP
        draw_text(f'{i.name} HP: {i.hp}', font, red, 550, (screen_height - bottom_panel + 10) + count * 60)


# draw bg
def draw_bg(bg):
    screen.blit(bg, (0, 0))


# fighter class
class Fighter:
    def __init__(self, x, y, name, max_hp, strength, potions):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.start_potions = potions
        self.potions = potions
        self.alive = True

        # handling animation

        self.action = 0  # 0: idle, 1:attack, 2:hurt, 3:dead
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        # load idle images
        temp_list = []
        for i in range(8):
            charImg = pygame.image.load(f'img/{self.name}/Idle/{i}.png')
            #
            charImg = pygame.transform.scale(charImg, (charImg.get_width() * 3, charImg.get_height() * 3))
            temp_list.append(charImg)
        self.animation_list.append(temp_list)
        # load attack images
        temp_list = []
        for i in range(8):
            charImg = pygame.image.load(f'img/{self.name}/Attack/{i}.png')
            charImg = pygame.transform.scale(charImg, (charImg.get_width() * 3, charImg.get_height() * 3))
            temp_list.append(charImg)
        self.animation_list.append(temp_list)
        # load 'take damage' image'
        temp_list = []
        for i in range(3):
            charImg = pygame.image.load(f'img/{self.name}/Hurt/{i}.png')
            charImg = pygame.transform.scale(charImg, (charImg.get_width() * 3, charImg.get_height() * 3))
            temp_list.append(charImg)
        self.animation_list.append(temp_list)
        # load death images
        temp_list = []
        for i in range(10):
            charImg = pygame.image.load(f'img/{self.name}/Death/{i}.png')
            charImg = pygame.transform.scale(charImg, (charImg.get_width() * 3, charImg.get_height() * 3))
            temp_list.append(charImg)
        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def draw(self):
        screen.blit(self.image, self.rect)

    def update(self):
        animation_cooldown = 100
        # handle animation
        # update image
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            ''' takes the current time, then take away the time it was last updated, 
            if the difference is more than 100 milisecs, update animation.'''
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # check if anim has run out of slides, and if so, reset anim
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        rand = random.randint(-5, 5)
        damage = self.strength + rand
        target.hp -= damage
        target.hurt()
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.die()
        damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
        damage_text_group.add(damage_text)
        # set variables to anim
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        # sets variables for hurt animation
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def die(self):
        # sets variables for death animation
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    #stuff for end of fights

    def reset(self):
        self.alive = True
        self.potions = self.start_potions
        self.hp = self.max_hp
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()


class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        self.hp = hp
        # calc hp ratio
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))


knight = Fighter(200, 260, 'Knight', 30, 10, 3)
bandit0 = Fighter(550, 270, 'Bandit', 17, 6, 1)
bandit1 = Fighter(700, 270, 'Bandit', 17, 6, 1)

bandit_list = []
bandit_list.append(bandit0)
bandit_list.append(bandit1)

knight_health_bar = HealthBar(100, screen_height - bottom_panel + 40, knight.hp, knight.max_hp)
bandit0_health_bar = HealthBar(550, screen_height - bottom_panel + 40, bandit0.hp, bandit0.max_hp)
bandit1_health_bar = HealthBar(550, screen_height - bottom_panel + 100, bandit1.hp, bandit1.max_hp)

potion_button = button.Button(screen, 100, screen_height - bottom_panel + 70, potion_img, 64, 64)
restart_button = button.Button(screen, 330, 120, restart_img, 120, 30)

run = True
while run:

    clock.tick(fps)

    # draw background and panel
    draw_bg(background_forest_0)
    draw_panel()
    # draw characters
    knight.update()
    knight.draw()
    for bandit in bandit_list:
        bandit.update()
        bandit.draw()
    damage_text_group.update()
    damage_text_group.draw(screen)
    # draw hp bars
    knight_health_bar.draw(knight.hp)
    bandit0_health_bar.draw(bandit0.hp)
    bandit1_health_bar.draw(bandit1.hp)

    # control player actions
    attack = False
    potion = False
    target = None
    # make sure mouse is visable when not pointing at enemy rects
    pygame.mouse.set_visible(True)
    pos = pygame.mouse.get_pos()
    for count, bandit in enumerate(bandit_list):
        if bandit.rect.collidepoint(pos):
            # hide mouse
            pygame.mouse.set_visible(False)
            # show sword
            screen.blit(custom_cursor, pos)
            if clicked == True:
                attack = True
                target = bandit_list[count]
    if potion_button.draw():
        print('Potion')
        potion = True

    # show potion # remaining
    draw_text(str(knight.potions) + " left", font, red, 150, screen_height - bottom_panel + 70)
    if game_over == 0:
        if knight.alive == True:
            if current_fighter == 1:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    # look for player action
                    # attack
                    if attack == True and target != None:
                        knight.attack(target)
                        current_fighter += 1
                        action_cooldown = 0
                    # potion
                    if potion == True:
                        if knight.potions > 0:
                            if knight.max_hp - knight.hp > potion_effect:
                                heal_amount = potion_effect
                                knight.hp += heal_amount
                                damage_text = DamageText(knight.rect.centerx, knight.rect.y, str(heal_amount), green)
                                damage_text_group.add(damage_text)
                                action_cooldown = 0
                                knight.potions -= 1
                                current_fighter += 1
                            else:
                                heal_amount = knight.max_hp - knight.hp
                                knight.hp += heal_amount
                                damage_text = DamageText(knight.rect.centerx, knight.rect.y, str(heal_amount), green)
                                damage_text_group.add(damage_text)
                                action_cooldown = 0
                                knight.potions -= 1
                                current_fighter += 1
        else:
            game_over = -1

        # enemy action
        for count, bandit in enumerate(bandit_list):
            if current_fighter == 2 + count:
                if bandit.alive == True:
                    action_cooldown += 1
                    if action_cooldown >= action_wait_time:
                        if bandit.hp / 2 <= bandit.max_hp / 2 and bandit.potions > 0:
                            if bandit.max_hp - bandit.hp > potion_effect:
                                heal_amount = potion_effect
                                bandit.hp += heal_amount
                                damage_text = DamageText(bandit.rect.centerx, bandit.rect.y, str(heal_amount), green)
                                damage_text_group.add(damage_text)
                                bandit.potions -= 1
                                current_fighter += 1
                                action_cooldown = 0
                            else:
                                heal_amount = bandit.max_hp - bandit.hp
                                bandit.hp += heal_amount
                                damage_text = DamageText(bandit.rect.centerx, bandit.rect.y, str(heal_amount), green)
                                damage_text_group.add(damage_text)
                                bandit.potions -= 1
                                current_fighter += 1
                                action_cooldown = 0

                        # attack
                        bandit.attack(knight)
                        current_fighter += 1
                        action_cooldown = 0
                else:
                    current_fighter += 1
        # if all fighters had turn, reset.
        if current_fighter > total_fighters:
            current_fighter = 1

    #check if all bandits are dead

    alive_bandits = 0
    for bandit in bandit_list:
        if bandit.alive == True:
            alive_bandits += 1
    if alive_bandits ==0:
        game_over = 1


    #check for gameover
    if game_over != 0:
        if game_over == 1:
            screen.blit(victory_img, (250,50))
        else:
            screen.blit(defeat_img, (250, 50))
        if restart_button.draw():
            knight.reset()
            for bandit in bandit_list:
                bandit.reset()
            current_fighter = 1
            action_cooldown = 0
            game_over = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False
    pygame.display.update()
pygame.quit()
