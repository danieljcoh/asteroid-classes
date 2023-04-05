import pygame, sys
from random import randint, uniform

class Ship(pygame.sprite.Sprite):
    def __init__(self, groups):

        super().__init__(groups)

        self.image = pygame.image.load('ship.png').convert_alpha()
        self.rect = self.image.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))

        self.mask = pygame.mask.from_surface(self.image)

        self.can_shoot = True
        self.shoot_time = None

        self.laser_sound = pygame.mixer.Sound("laser.ogg")

    def input_position(self):
        pos = pygame.mouse.get_pos()
        self.rect.center = pos

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time > 500:
                self.can_shoot = True

    def shoot_laser(self, can_shoot=True, duration=500):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.laser_sound.play()
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
            Laser(laser_group, self.rect.midtop)

    def meteor_collisions(self):
        if pygame.sprite.spritecollide(self, meteor_group, False):
            pygame.quit()
            sys.exit()

    def update(self):
        self.laser_timer()
        self.shoot_laser()
        self.input_position()
        self.meteor_collisions()


class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, pos):

        super().__init__(groups)

        self.image = pygame.image.load('laser.png').convert_alpha()
        self.rect = self.image.get_rect(midbottom=pos)

        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(0, -1)
        self.speed = 600

        self.explosion_sound = pygame.mixer.Sound("explosion.wav")

    def meteor_collision(self):
        if pygame.sprite.spritecollide(self, meteor_group, True):
            self.explosion_sound.play()
            self.kill()

    def update(self):
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.meteor_collision()

        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, pos):

        super().__init__(groups)

        meteor_surf = pygame.image.load("meteor.png").convert_alpha()
        meteor_size = pygame.math.Vector2(meteor_surf.get_size()) * uniform(0.5, 2.0)
        self.scaled_surf = pygame.transform.scale(meteor_surf, meteor_size)
        self.image = self.scaled_surf
        self.rect = self.image.get_rect(center=pos)

        self.mask = pygame.mask.from_surface(self.image)

        self.pos = pygame.math.Vector2(self.rect.topleft)
        self.direction = pygame.math.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400, 600)

        # rotation logic
        self.rotation = 0
        self.rotation_speed = randint(20, 50)

    def rotate(self):
        self.rotation += self.rotation_speed * dt
        rotated_surf = pygame.transform.rotozoom(self.scaled_surf, self.rotation, 1)
        self.image = rotated_surf
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)  # we have to do this again since we overwrote the surface
        # we overwrote the surface to rotate it

    def update(self):
        self.pos += self.direction * self.speed * dt
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.rotate()

        if self.rect.top > WINDOW_HEIGHT:
            self.kill()


class Score:
    def __init__(self):
        self.font = pygame.font.Font('subatomic.ttf', 50)

    def display(self):
        score_text = f"Score: {pygame.time.get_ticks() // 1000}"
        text_surface = self.font.render(score_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(midbottom=(WINDOW_WIDTH /2, WINDOW_HEIGHT - 80))
        display_surface.blit(text_surface, text_rect)
        pygame.draw.rect(display_surface, (255, 255, 255), text_rect.inflate(30, 30), width=8, border_radius=5)


# INIT
pygame.init()
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Asteroid Classes")
clock = pygame.time.Clock()

background_surf = pygame.image.load('background.png').convert()

# sprite groups
spaceship_group = pygame.sprite.GroupSingle()
laser_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()

# sprite creation
ship = Ship(spaceship_group)

# meteor timer
meteor_timer = pygame.event.custom_type()
pygame.time.set_timer(meteor_timer, 400)  # 1000

# Score
score = Score()

# Music
bg_music = pygame.mixer.Sound("music.wav")
bg_music.play(loops=-1)

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == meteor_timer:
            meteor_y_pos = randint(-150, -50)
            meteor_x_pos = randint(-100, WINDOW_WIDTH + 100)
            Meteor(meteor_group, (meteor_x_pos, meteor_y_pos))

    dt = clock.tick() / 1000

    # background
    display_surface.blit(background_surf, (0, 0))

    # update
    spaceship_group.update()
    laser_group.update()
    meteor_group.update()

    # score
    score.display()

    # graphics
    spaceship_group.draw(display_surface)
    laser_group.draw(display_surface)
    meteor_group.draw(display_surface)

    # draw the frame
    pygame.display.update()

