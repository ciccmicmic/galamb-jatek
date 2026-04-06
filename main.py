import pygame
import os
import random
import asyncio

pygame.init()
pygame.mixer.init()

# Ablak méretei
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Vége van kicsi")

# Segédfüggvény a fájlok betöltéséhez (ha nincs mappa, akkor is megtalálja)
def get_path(filename):
    # Megpróbálja az Assets mappákban, ha nem sikerül, nézi simán a főkönyvtárban
    possible_paths = [
        filename,
        os.path.join("Assets/Sounds", filename),
        os.path.join("Assets/Viktor", filename),
        os.path.join("Assets/Avocado", filename),
        os.path.join("Assets/Heli", filename),
        os.path.join("Assets/Other", filename)
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return filename

def load_sound_web(name):
    try:
        return pygame.mixer.Sound(get_path(name))
    except:
        return None

def load_img_web(name, scale=None):
    try:
        img = pygame.image.load(get_path(name)).convert_alpha()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    except:
        # Ha nincs kép, egy piros kockát ad vissza, hogy ne fagyjon le
        s = pygame.Surface((50, 50))
        s.fill((255, 0, 0))
        return s

# Assets betöltése
try:
    jump_sound = load_sound_web("jump.ogg")
    duck_sound = load_sound_web("duck.ogg")
    collision_sound = load_sound_web("collision.ogg")
    coin_sound = load_sound_web("coin.ogg")
    game_over_sound = load_sound_web("game_over.ogg")
    
    RUNNING = [load_img_web("ViktorRun1.png"), load_img_web("ViktorRun2.png")]
    JUMPING = load_img_web("ViktorJump.png")
    DUCKING = [load_img_web("ViktorDuck1.png"), load_img_web("ViktorDuck2.png")]
    SMALL_AVOCADO = [load_img_web("SmallAvocado1.png"), load_img_web("SmallAvocado2.png"), load_img_web("SmallAvocado3.png")]
    LARGE_AVOCADO = [load_img_web("LargeAvocado1.png"), load_img_web("LargeAvocado2.png")]
    HELI = [load_img_web("Heli1.png"), load_img_web("Heli2.png")]
    CLOUD = load_img_web("Cloud.png")
    BACKGROUND = load_img_web("background.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
    BG = load_img_web("Track.png")
    LANDING_PAGE = load_img_web("landingpage.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    pass

class Viktosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5
    GROUND_LEVEL = 380

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING
        self.Viktor_duck = False
        self.Viktor_run = True
        self.Viktor_jump = False
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.Viktor_rect = self.image.get_rect()
        self.Viktor_rect.x = self.X_POS
        self.Viktor_rect.y = self.Y_POS
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, userInput):
        if self.Viktor_duck: self.duck()
        if self.Viktor_run: self.run()
        if self.Viktor_jump: self.jump()
        if self.step_index >= 10: self.step_index = 0

        if userInput[pygame.K_UP] and not self.Viktor_jump:
            self.Viktor_duck = False
            self.Viktor_run = False
            self.Viktor_jump = True
            if jump_sound: jump_sound.play()
        elif userInput[pygame.K_DOWN] and not self.Viktor_jump:
            self.Viktor_duck = True
            self.Viktor_run = False
            self.Viktor_jump = False
            if duck_sound: duck_sound.play()
        elif not (self.Viktor_jump or userInput[pygame.K_DOWN]):
            self.Viktor_duck = False
            self.Viktor_run = True
            self.Viktor_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.Viktor_rect = self.image.get_rect()
        self.Viktor_rect.x = self.X_POS
        self.Viktor_rect.y = self.Y_POS_DUCK
        self.step_index += 1
        self.mask = pygame.mask.from_surface(self.image)

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.Viktor_rect = self.image.get_rect()
        self.Viktor_rect.x = self.X_POS
        self.Viktor_rect.y = self.Y_POS
        self.step_index += 1
        self.mask = pygame.mask.from_surface(self.image)

    def jump(self):
        self.image = self.jump_img
        if self.Viktor_jump:
            self.Viktor_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
            if self.Viktor_rect.y >= self.GROUND_LEVEL - self.image.get_height():
                self.Viktor_rect.y = self.GROUND_LEVEL - self.image.get_height()
                self.Viktor_jump = False
                self.jump_vel = self.JUMP_VEL
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.Viktor_rect.x, self.Viktor_rect.y))

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(100, 150)
        self.image = CLOUD
        self.width = self.image.get_width()
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.mask = pygame.mask.from_surface(self.image)
        self.visible = True

    def update(self, game_speed):
        if self.visible:
            self.x -= game_speed * 0.5
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)
            self.visible = True
        self.rect.x, self.rect.y = int(self.x), int(self.y)

    def draw(self, SCREEN):
        if self.visible: SCREEN.blit(self.image, (self.x, self.y))

class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = 370
        self.mask = pygame.mask.from_surface(self.image[self.type])

    def update(self, game_speed, obstacles):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop(0)

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)

# Fő játék ciklus aszinkron módon
async def main_game(player_name_val):
    global game_speed, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Viktosaur()
    cloud = Cloud()
    game_speed = 20
    points = 0
    obstacles = []
    font = pygame.font.Font(None, 24)

    # Zene indítása
    try:
        pygame.mixer.music.load(get_path("background_music.ogg"))
        pygame.mixer.music.play(-1)
    except:
        pass

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        SCREEN.fill((255, 255, 255))
        SCREEN.blit(BACKGROUND, (0, 0))

        cloud.draw(SCREEN)
        cloud.update(game_speed)

        userInput = pygame.key.get_pressed()
        player.draw(SCREEN)
        player.update(userInput)

        if len(obstacles) == 0:
            r = random.randint(0, 2)
            if r == 0: obstacles.append(Obstacle(SMALL_AVOCADO, random.randint(0, 2)))
            elif r == 1: obstacles.append(Obstacle(LARGE_AVOCADO, random.randint(0, 1)))
            elif r == 2: 
                h = Obstacle(HELI, 0)
                h.rect.y = 300
                obstacles.append(h)

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update(game_speed, obstacles)
            if player.mask.overlap(obstacle.mask, (obstacle.rect.x - player.Viktor_rect.x, obstacle.rect.y - player.Viktor_rect.y)):
                if collision_sound: collision_sound.play()
                pygame.mixer.music.stop()
                if game_over_sound: game_over_sound.play()
                await asyncio.sleep(2)
                return points # Visszatérünk a pontszámmal a menübe

        # Pontszám és felhő ütközés
        points += 1
        score_txt = font.render(f"{player_name_val} - Pontok: {points}", True, (0, 0, 0))
        SCREEN.blit(score_txt, (800, 40))

        pygame.display.update()
        clock.tick(30)
        await asyncio.sleep(0)

# Menü aszinkron módon
async def menu():
    player_name = ""
    font = pygame.font.Font(None, 40)
    input_active = True
    
    while True:
        SCREEN.blit(LANDING_PAGE, (0, 0))
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name:
                    final_points = await main_game(player_name)
                    # Itt lehetne menteni a pontszámot, de weben a fájlba írás korlátozott
                    player_name = "" # Reset a következő körhöz
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 10:
                        player_name += event.unicode

        txt = font.render("Írd be a neved és nyomj ENTER-t:", True, (0, 0, 0))
        SCREEN.blit(txt, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50))
        
        name_txt = font.render(player_name + "_", True, (0, 0, 255))
        SCREEN.blit(name_txt, (SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2 + 20))

        pygame.display.update()
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(menu())
