import random
import pygame
from pygame.locals import *

# Initialize the mixer module
pygame.mixer.init()
# Load the background music
pygame.mixer.music.load('music/game.mp3')
# Play the background music
pygame.mixer.music.play(-1) # The -1 argument makes the music loop indefinitely

# Constants
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.06
PLAYER_GRAVITY = 0.8

# Platforms
PLATFORM_LIST = [(0, HEIGHT - 40, WIDTH, 40),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4 - 50, 100, 20),
                 (125, HEIGHT - 350, 100, 20),
                 (350, HEIGHT - 200, 100, 20),
                 (175, HEIGHT - 100, 50, 20)]

x_bg = 0
x_e = 0


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        # Load the images for the run animation
        self.run_images = [pygame.image.load(f'player/sonic/run{i}.png').convert_alpha() for i in range(1, 8)]
        self.run_images = [pygame.transform.rotozoom(image, 0, 1.4) for image in self.run_images]
        self.run_images = [pygame.transform.flip(image, True, False) for image in self.run_images]
        # Load the images for the jump animation
        self.jump_images = [pygame.image.load(f'player/sonic/jump{i}.png').convert_alpha() for i in range(1, 11)]
        self.jump_images = [pygame.transform.rotozoom(image, 0, 1.4) for image in self.jump_images]
        #self.jump_images = [pygame.transform.flip(image, True, False) for image in self.jump_images]
        # Load the images for the shoot animation
        self.shoot_images = [pygame.image.load(f'player/soldier/shoot{i}.png').convert_alpha() for i in range(1, 5)]
        # Load the images for the runrun animation
        self.new_images = [pygame.image.load(f'player/sonic/runrun{i}.png').convert_alpha() for i in range(1, 9)]
        self.new_images = [pygame.transform.rotozoom(image, 0, 1.4) for image in self.new_images]
        self.new_images = [pygame.transform.flip(image, True, False) for image in self.new_images]
        # Add variables for shoot animation
        self.shooting = False
        self.shoot_frame = 0
        self.shoot_last_update = 0
        # Load the images for the death animation
        self.death_images = [pygame.image.load(f'player/soldier/dead{i}.png').convert_alpha() for i in range(1, 5)]
        # Add variables for death animation
        self.dead = False
        self.death_frame = 0
        self.death_last_update = 0
        # Set the initial image and rect
        self.image = self.run_images[0]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        
        # Set up other variables
        self.pos = pygame.math.Vector2(WIDTH /5 , HEIGHT -20)
        self.vel = pygame.math.Vector2(0 ,0)
        self.acc = pygame.math.Vector2(0 ,0)
        self.frame = 0
        self.timer = pygame.time.get_ticks()
        self.is_jumping_up = False


    def update(self):
        # Update the image based on what the player is doing
        now = pygame.time.get_ticks()
        self.vel.y += PLAYER_GRAVITY
        
        if self.vel.y < 0:
            self.is_jumping_up = True
        elif self.vel.y > 0:
            self.is_jumping_up = False
        
        if (pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_LEFT]) and not self.is_jumping_up:
            # Player is pressing right or left arrow key and not jumping up
            # Update the frame of the new animation every 100 milliseconds
            if now - self.timer > 100:
                self.frame += 1
                if self.frame >= len(self.new_images):
                    # Reset the frame counter when we reach the end of the animation
                    self.frame = 0
                # Set the new image and reset the timer
                self.image = self.new_images[self.frame]
                self.timer = now

            # Increase the player's speed
            self.vel.x *= 10  # You can change this value to adjust the speed increase

        # Apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION

        # Equations of motion
        #self.vel += self.acc
        self.pos += self.vel + PLAYER_ACC * self.acc
        
        # Update player position
        self.pos.x += self.vel.x
        
        # Wrap around the sides of the screen
        if self.pos.x > WIDTH:
            self.pos.x = WIDTH
            self.vel.x *= -1
        if self.pos.x < 0:
            self.pos.x = WIDTH    

        
        # Add death animation
        if self.dead:
            now = pygame.time.get_ticks()
            if now - self.death_last_update > 50:
                self.death_last_update = now
                if self.death_frame < len(self.death_images) - 1:
                    self.death_frame += 1
                center = self.rect.center
                self.image = self.death_images[self.death_frame]
                self.rect = self.image.get_rect()
                self.rect.center = center
                # Stop game after showing last frame of death animation
                if self.death_frame == len(self.death_images) - 1:
                    global restart
                    restart = True

        # Set the new player position based on above
        self.rect.midbottom = self.pos
        # Animate the sprite by changing the image every 100 milliseconds
        now = pygame.time.get_ticks()
        if now - self.timer > 100 and not self.is_jumping_up:
            self.timer = now
            self.frame = (self.frame + 1) % len(self.run_images)
            self.image = self.run_images[self.frame]
            # Set the colorkey again in case it changes with the image
            self.image.set_colorkey(BLACK)
        
    def shoot(self):
        bullet = Bullet(self.rect.right, self.rect.centery)
        all_sprites.add(bullet)
        bullets.add(bullet)
        # Activate shoot animation
        self.shooting = True
        

    def jump(self, jump_force):
        # Jump only if standing on a platform
        hits = pygame.sprite.spritecollide(self ,platforms ,False)
        if hits:
            self.vel.y = jump_force
class Platform(pygame.sprite.Sprite):  
    def __init__(self ,x ,y ,w ,h, is_ground=False):
        pygame.sprite.Sprite.__init__(self)
        if is_ground:
            self.image = pygame.Surface((w ,h))
            self.image.fill((0, 0, 0, 0)) # Color transparente
            self.image.set_colorkey((0, 0, 0)) # Establecer colorkey para transparencia
        else:
            self.image = pygame.image.load("tiles/platform.png").convert_alpha() # Cargar imagen PNG
            w = int(w * 1.1) # Escalar ancho un 10%
            h = int(h * 1.1) # Escalar alto un 10%
            self.image = pygame.transform.scale(self.image, (w, h)) # Escalar imagen al tamaño de la plataforma
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_ground = is_ground

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.image.load(f'enemy/enemy{i}.png').convert_alpha() for i in range(1, 6)]
        self.images = [pygame.transform.rotozoom(image, 0, 1.9) for image in self.images]
        self.images = [pygame.transform.flip(image, True, False) for image in self.images]
        self.current_image = 0
        self.image = self.images[self.current_image]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speedx = -2
        self.animation_speed = 10
        self.frame_count = 0

    def update(self):
        self.rect.x += self.speedx
        if self.rect.right < 0:
            self.kill()
        
        # Actualizar la imagen del enemigo para crear una animación
        self.frame_count += 1
        if self.frame_count % self.animation_speed == 0:
            self.current_image = (self.current_image + 1) % len(self.images)
            self.image = self.images[self.current_image]
            
# Define la función add_enemy fuera de la clase Enemy
def add_enemy(interval):
    x = WIDTH # La posición en el eje x es siempre el borde derecho de la ventana
    y = HEIGHT - 100 # La posición en el eje y es la misma para todos los enemigos
    enemy = Enemy(x, y)
    all_sprites.add(enemy)
    enemies.add(enemy)

    # Genera un intervalo de tiempo aleatorio entre 500 y 3000 milisegundos
    interval = random.randint(500, 3000)
    # Actualiza el temporizador con el nuevo intervalo de tiempo
    pygame.time.set_timer(ADDENEMY, interval)
    
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((5, 5))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedx = 10 # Agrega velocidad en el eje x

    def update(self):
        self.rect.x += self.speedx # Actualiza la posición en el eje x
        # Elimina la bala si sale de la pantalla
        if self.rect.left > WIDTH:
            self.kill()    

# Initialize Pygame and create window
pygame.init()
screen = pygame.display.set_mode((WIDTH ,HEIGHT))
pygame.display.set_caption("PLATFORM1")
clock = pygame.time.Clock()

# Define un nuevo tipo de evento para el temporizador
ADDENEMY = pygame.USEREVENT + 1

# Establece el temporizador para generar un evento ADDENEMY cada 1000 milisegundos (1 segundo)
pygame.time.set_timer(ADDENEMY, 3000)

# Load and scale background image
bg = pygame.image.load('fondos/Background.png').convert()
bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
bg_rect = bg.get_rect()

# Sprites group
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Player object
player = Player()
all_sprites.add(player)

# Platforms objects
for plat in PLATFORM_LIST:
    if plat[1] == HEIGHT - 40:
        p = Platform(*plat, is_ground=True)
    else:
        p = Platform(*plat)
    all_sprites.add(p)
    platforms.add(p)

# Agrega una variable para rastrear cuánto tiempo se ha mantenido presionada la tecla de espacio
space_pressed_time = 0

# Add a variable to indicate if the game should restart
restart = False

# Add a variable to track how long the player has been dead
death_time = 0


# Game loop
running=True
bg_x = 0
plat_x = 0

# Add a global variable to indicate if the game should restart
restart = False

while running:
    # Keep loop running at the right speed
    clock.tick(FPS)

    # Check for bullet-enemy collisions
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)

# Move enemies
    for enemy in enemies:
        enemy.update() # Llama al método update de cada enemigo para actualizar su posición

    # Move background
    bg_x -= 4 # Aumenta este valor para aumentar la velocidad de movimiento del fondo
    if bg_x < -bg_rect.width:
        bg_x = 0

    # Move platforms
    plat_x -= 4 # Aumenta este valor para aumentar la velocidad de movimiento de las plataformas
    for plat in platforms:
        if not plat.is_ground:
            plat.rect.x -= 4 # Aumenta este valor para aumentar la velocidad de movimiento de las plataformas individuales
            if plat.rect.right < 0:
                plat.kill()
                # Generate random platform size and position
                plat_width = random.randint(50, 150)
                plat_height = 20
                plat_x = WIDTH + plat_x
                plat_y = random.randint(HEIGHT // 2, HEIGHT - plat_height - 50)
                p = Platform(plat_x, plat_y, plat_width, plat_height)
                all_sprites.add(p)
                platforms.add(p)
                
# Create a boolean variable to indicate if the game is paused or not
    paused = False

    for event in pygame.event.get():
    # Check for closing window event
        if event.type == QUIT:
            running=False
        elif event.type == ADDENEMY:
            # Llama a la función add_enemy cuando se recibe un evento ADDENEMY
            interval = random.randint(500, 3000)
            add_enemy(interval)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                # Toggle the paused variable
                paused = not paused
                if paused:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
            if event.key == pygame.K_SPACE:
                space_pressed_time = pygame.time.get_ticks()
            elif event.key == pygame.K_z:
                player.shoot()
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                # Player is pressing right or left arrow key
                player.vel.x *= 20  # You can change this value to adjust the speed increase
            elif event.key == pygame.K_RIGHT:
                x_bg += 5
                x_e += 5
            elif event.key == pygame.K_LEFT:
                x_bg -= 5
                x_e -= 5
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                space_pressed_duration = pygame.time.get_ticks() - space_pressed_time
                jump_force = -20 if space_pressed_duration < 500 else -30
                player.jump(jump_force)
                if player.is_jumping_up:
                    # Going up
                    player.image = player.jump_images[0]
                else:
                    # Going down
                    player.image = player.jump_images[1]
                
    # If the game is paused, enter a while loop
    while paused:
    # Process events inside the loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                paused = False
        # Check if the key p is pressed again
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                # Toggle the paused variable and exit the loop
                    paused = not paused  
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()      

    # Update sprites group
    all_sprites.update()

    # Check if player hits a platform - only if falling
    if player.vel.y >0:
        hits=pygame.sprite.spritecollide(player ,platforms ,False)
        if hits:
            player.pos.y=hits[0].rect.top +1 
            player.vel.y=0
            # Desactiva la gravedad cuando el jugador aterriza en una plataforma
            player.gravity = False

    # Check if player hits an enemy
    hits = pygame.sprite.spritecollide(player, enemies, False)
    if hits:
        # Player hit an enemy!
        # Activate death animation
        player.dead = True

    # Draw / render sprites group and flip display after drawing everything!
    screen.fill(BLACK)
    screen.blit(bg, (bg_x, 0))
    screen.blit(bg, (bg_x + bg_rect.width, 0))
    all_sprites.draw(screen)
    pygame.display.flip()

    # Check if game should restart
    if restart:
        running = False

# Quit game
pygame.quit()