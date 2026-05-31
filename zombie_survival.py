import pygame
import random
import math
from collections import deque

# Initialize Pygame
pygame.init()
pygame.mixer.init() # Init audio in case system supports it, but we won't crash if it fails

# -----------------------
# CONSTANTS & CONFIG
# -----------------------
WIDTH, HEIGHT = 960, 640
TILE_SIZE = 32
ROWS = HEIGHT // TILE_SIZE # 20
COLS = WIDTH // TILE_SIZE # 30

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHADOW ESCAPE: SMART APOCALYPSE")
clock = pygame.time.Clock()

# Color Palette (Premium Cyberspace/Horror Aesthetic)
COLOR_BG = (10, 11, 16)
COLOR_WALL = (30, 41, 59)
COLOR_WALL_BORDER = (56, 189, 248) # Electric Cyan
COLOR_PLAYER = (253, 224, 71)      # Glowing Neon Yellow
COLOR_ZOMBIE_NORMAL = (239, 68, 68) # Vivid Neon Red
COLOR_ZOMBIE_FAST = (249, 115, 22)  # Hyper Orange
COLOR_ZOMBIE_TANK = (153, 27, 27)   # Deep Blood Red
COLOR_GOAL = (34, 197, 94)          # Acid Green
COLOR_BULLET = (255, 255, 255)
COLOR_HUD_TEXT = (241, 245, 249)
COLOR_DARKNESS = (12, 12, 22)       # Ambient Dark Tint

# Fonts
FONT_TITLE = pygame.font.SysFont("Outfit", 64, bold=True)
FONT_SUBTITLE = pygame.font.SysFont("Inter", 24, bold=False)
FONT_HUD = pygame.font.SysFont("Consolas", 18, bold=True)
FONT_BIG = pygame.font.SysFont("Outfit", 48, bold=True)

# -----------------------
# PROCEDURAL MAZE GENERATION
# -----------------------
def generate_maze(rows, cols):
    # Start with all walls
    grid = [[1 for _ in range(cols)] for _ in range(rows)]
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    
    # DFS Recursive Backtracker for a perfect maze
    stack = []
    start_r, start_c = 1, 1
    grid[start_r][start_c] = 0
    visited[start_r][start_c] = True
    stack.append((start_r, start_c))
    
    while stack:
        r, c = stack[-1]
        neighbors = []
        for dr, dc in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nr, nc = r + dr, c + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1:
                if not visited[nr][nc]:
                    neighbors.append((nr, nc))
        
        if neighbors:
            nr, nc = random.choice(neighbors)
            # Carve through the wall
            grid[r + (nr - r)//2][c + (nc - c)//2] = 0
            grid[nr][nc] = 0
            visited[nr][nc] = True
            stack.append((nr, nc))
        else:
            stack.pop()
            
    # Loop carving: turn ~18% of walls into passages for better combat/navigation
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if grid[r][c] == 1:
                open_neighbors = 0
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    if grid[r+dr][c+dc] == 0:
                        open_neighbors += 1
                if open_neighbors >= 2 and random.random() < 0.18:
                    grid[r][c] = 0
                    
    # Ensure start (1,1) and goal (rows-2, cols-2) are fully open
    grid[1][1] = 0
    grid[rows-2][cols-2] = 0
    
    # Extra clearing around spawn/exit points
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if 0 < 1+dr < rows-1 and 0 < 1+dc < cols-1:
                if random.random() < 0.4:
                    grid[1+dr][1+dc] = 0
            if 0 < (rows-2)+dr < rows-1 and 0 < (cols-2)+dc < cols-1:
                if random.random() < 0.4:
                    grid[(rows-2)+dr][(cols-2)+dc] = 0
                    
    return grid

# Helper to check wall collisions
def get_colliding_walls(rect, grid):
    colliding = []
    start_c = max(0, rect.left // TILE_SIZE)
    end_c = min(COLS - 1, rect.right // TILE_SIZE)
    start_r = max(0, rect.top // TILE_SIZE)
    end_r = min(ROWS - 1, rect.bottom // TILE_SIZE)
    
    for r in range(int(start_r), int(end_r) + 1):
        for c in range(int(start_c), int(end_c) + 1):
            if grid[r][c] == 1:
                wall_rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if rect.colliderect(wall_rect):
                    colliding.append(wall_rect)
    return colliding

# -----------------------
# PATHFINDING (DIJKSTRA FLOW-FIELD)
# -----------------------
def update_dijkstra_map(grid, player_r, player_c):
    dijkstra = [[9999 for _ in range(COLS)] for _ in range(ROWS)]
    if not (0 <= player_r < ROWS and 0 <= player_c < COLS):
        return dijkstra
        
    dijkstra[player_r][player_c] = 0
    queue = deque([(player_r, player_c)])
    
    while queue:
        r, c = queue.popleft()
        dist = dijkstra[r][c]
        
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if grid[nr][nc] == 0: # Walkable path
                    if dijkstra[nr][nc] > dist + 1:
                        dijkstra[nr][nc] = dist + 1
                        queue.append((nr, nc))
    return dijkstra

# -----------------------
# PARTICLE SYSTEM
# -----------------------
class Particle:
    def __init__(self, x, y, dx, dy, color, size, life):
        self.x = float(x)
        self.y = float(y)
        self.dx = dx
        self.dy = dy
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dx *= 0.95
        self.dy *= 0.95
        self.life -= 1
        return self.life <= 0
        
    def draw(self, surface):
        if self.life > 0:
            pct = self.life / self.max_life
            sz = max(1, int(self.size * pct))
            r, g, b = self.color
            c = (int(r * pct), int(g * pct), int(b * pct))
            pygame.draw.circle(surface, c, (int(self.x), int(self.y)), sz)

# -----------------------
# ENTITY CLASSES
# -----------------------
class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.radius = 9
        self.speed = 3.2
        self.hp = 100
        self.max_hp = 100
        self.ammo = 12
        self.max_ammo = 12
        self.is_reloading = False
        self.reload_timer = 0
        self.reload_duration = 75 # frames (1.25s)
        self.speed_boost_time = 0 # frames
        self.score = 0
        self.kills = 0
        self.invuln_timer = 0 # frames
        self.angle = 0.0
        
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        
    def move(self, dx, dy, grid):
        speed_mult = 1.45 if self.speed_boost_time > 0 else 1.0
        current_speed = self.speed * speed_mult
        
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
            
        move_x = dx * current_speed
        move_y = dy * current_speed
        
        # Move X & Slide
        self.x += move_x
        rect = self.get_rect()
        collided = get_colliding_walls(rect, grid)
        if collided:
            for wall in collided:
                if move_x > 0:
                    self.x = wall.left - self.radius
                elif move_x < 0:
                    self.x = wall.right + self.radius
                    
        # Move Y & Slide
        self.y += move_y
        rect = self.get_rect()
        collided = get_colliding_walls(rect, grid)
        if collided:
            for wall in collided:
                if move_y > 0:
                    self.y = wall.top - self.radius
                elif move_y < 0:
                    self.y = wall.bottom + self.radius
                    
        # Keep inside screens
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

    def shoot(self, target_x, target_y, bullets, particles):
        if self.is_reloading:
            return False
            
        if self.ammo <= 0:
            self.start_reload()
            return False
            
        angle = math.atan2(target_y - self.y, target_x - self.x)
        self.ammo -= 1
        
        bullets.append(Bullet(self.x, self.y, angle))
        
        # Spawn muzzle flash particles
        gun_x = self.x + math.cos(angle) * 12
        gun_y = self.y + math.sin(angle) * 12
        for _ in range(5):
            pa = angle + random.uniform(-0.3, 0.3)
            pspeed = random.uniform(2, 5)
            particles.append(Particle(
                gun_x, gun_y, 
                math.cos(pa) * pspeed, math.sin(pa) * pspeed, 
                (253, 224, 71), random.uniform(3, 5), random.randint(8, 15)
            ))
        return True
        
    def start_reload(self):
        if not self.is_reloading and self.ammo < self.max_ammo:
            self.is_reloading = True
            self.reload_timer = self.reload_duration
            
    def update(self):
        if self.reload_timer > 0:
            self.reload_timer -= 1
            if self.reload_timer == 0:
                self.ammo = self.max_ammo
                self.is_reloading = False
                
        if self.speed_boost_time > 0:
            self.speed_boost_time -= 1
            
        if self.invuln_timer > 0:
            self.invuln_timer -= 1
            
    def draw(self, surface, mouse_x, mouse_y):
        self.angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
        
        if self.invuln_timer > 0 and (self.invuln_timer // 4) % 2 == 0:
            return
            
        # Draw player base
        pygame.draw.circle(surface, COLOR_PLAYER, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), self.radius - 4)
        
        # Draw weapon barrel
        barrel_len = 14
        barrel_end = (
            int(self.x + math.cos(self.angle) * barrel_len),
            int(self.y + math.sin(self.angle) * barrel_len)
        )
        pygame.draw.line(surface, (148, 163, 184), (int(self.x), int(self.y)), barrel_end, 4)
        pygame.draw.circle(surface, (71, 85, 105), barrel_end, 3)

class Bullet:
    def __init__(self, x, y, angle):
        self.x = float(x)
        self.y = float(y)
        self.speed = 11.5
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed
        self.radius = 3
        self.damage = 34
        self.trail = []
        
    def update(self, grid):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)
            
        self.x += self.dx
        self.y += self.dy
        
        # Wall Collision check
        r = int(self.y // TILE_SIZE)
        c = int(self.x // TILE_SIZE)
        if 0 <= r < ROWS and 0 <= c < COLS:
            if grid[r][c] == 1:
                return True
        else:
            return True
        return False
        
    def draw(self, surface):
        # Draw fading trails
        for i, pos in enumerate(self.trail):
            alpha_ratio = (i + 1) / len(self.trail)
            sz = max(1, int(self.radius * alpha_ratio))
            glow_c = (int(253 * alpha_ratio), int(224 * alpha_ratio), int(71 * alpha_ratio))
            pygame.draw.circle(surface, glow_c, (int(pos[0]), int(pos[1])), sz)
            
        pygame.draw.circle(surface, COLOR_BULLET, (int(self.x), int(self.y)), self.radius)

class Zombie:
    def __init__(self, x, y, ztype="stalker"):
        self.x = float(x)
        self.y = float(y)
        self.type = ztype
        
        if ztype == "runner":
            self.radius = 8
            self.speed = 2.1
            self.hp = 30
            self.max_hp = 30
            self.color = COLOR_ZOMBIE_FAST
            self.score_val = 150
        elif ztype == "tank":
            self.radius = 12
            self.speed = 1.0
            self.hp = 100
            self.max_hp = 100
            self.color = COLOR_ZOMBIE_TANK
            self.score_val = 250
        else: # stalker
            self.radius = 9
            self.speed = 1.45
            self.hp = 50
            self.max_hp = 50
            self.color = COLOR_ZOMBIE_NORMAL
            self.score_val = 100
            
        self.angle = 0.0
        
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        
    def update(self, grid, dijkstra_map, player_pos, other_zombies):
        r = int(self.y // TILE_SIZE)
        c = int(self.x // TILE_SIZE)
        
        dir_vector = pygame.Vector2(0, 0)
        player_r = int(player_pos.y // TILE_SIZE)
        player_c = int(player_pos.x // TILE_SIZE)
        
        if (r, c) == (player_r, player_c):
            dir_vector = player_pos - pygame.Vector2(self.x, self.y)
        else:
            best_neighbor = None
            min_dist = 99999
            
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] == 0:
                    dist = dijkstra_map[nr][nc]
                    if dist < min_dist:
                        min_dist = dist
                        best_neighbor = (nr, nc)
            
            if best_neighbor:
                target_x = best_neighbor[1] * TILE_SIZE + TILE_SIZE // 2
                target_y = best_neighbor[0] * TILE_SIZE + TILE_SIZE // 2
                dir_vector = pygame.Vector2(target_x - self.x, target_y - self.y)
            else:
                dir_vector = player_pos - pygame.Vector2(self.x, self.y)
                
        if dir_vector.length() != 0:
            dir_vector = dir_vector.normalize()
            
        sep_force = pygame.Vector2(0, 0)
        for other in other_zombies:
            if other is not self:
                dist = pygame.Vector2(self.x - other.x, self.y - other.y).length()
                bubble_radius = self.radius + other.radius + 4
                if 0 < dist < bubble_radius:
                    push = pygame.Vector2(self.x - other.x, self.y - other.y).normalize()
                    sep_force += push * (bubble_radius - dist) * 0.15
                    
        move_dir = dir_vector + sep_force
        if move_dir.length() != 0:
            move_dir = move_dir.normalize()
            
        # Move X
        move_x = move_dir.x * self.speed
        self.x += move_x
        rect = self.get_rect()
        collided = get_colliding_walls(rect, grid)
        if collided:
            for wall in collided:
                if move_x > 0:
                    self.x = wall.left - self.radius
                elif move_x < 0:
                    self.x = wall.right + self.radius
                    
        # Move Y
        move_y = move_dir.y * self.speed
        self.y += move_y
        rect = self.get_rect()
        collided = get_colliding_walls(rect, grid)
        if collided:
            for wall in collided:
                if move_y > 0:
                    self.y = wall.top - self.radius
                elif move_y < 0:
                    self.y = wall.bottom + self.radius
                    
        if dir_vector.length() > 0:
            self.angle = math.atan2(dir_vector.y, dir_vector.x)
            
    def draw_body(self, surface):
        # Base body
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (10, 10, 10), (int(self.x), int(self.y)), self.radius - 3)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius - 5)
        
        # Hands
        arm_len = self.radius + 4
        left_hand = (
            int(self.x + math.cos(self.angle - 0.4) * arm_len),
            int(self.y + math.sin(self.angle - 0.4) * arm_len)
        )
        right_hand = (
            int(self.x + math.cos(self.angle + 0.4) * arm_len),
            int(self.y + math.sin(self.angle + 0.4) * arm_len)
        )
        pygame.draw.line(surface, self.color, (int(self.x), int(self.y)), left_hand, 2)
        pygame.draw.line(surface, self.color, (int(self.x), int(self.y)), right_hand, 2)
        
        # Health bar
        if self.hp < self.max_hp:
            bar_w = self.radius * 2
            bar_h = 3
            bx = self.x - self.radius
            by = self.y - self.radius - 7
            pygame.draw.rect(surface, (30, 30, 30), (bx, by, bar_w, bar_h))
            hp_w = int(bar_w * (self.hp / self.max_hp))
            pygame.draw.rect(surface, (239, 68, 68), (bx, by, hp_w, bar_h))
            
    def draw_eyes(self, surface):
        # Stealth glowing eyes drawn directly on top of the black shadows
        eye_dist = 4
        eye_angle = 0.5
        eye1 = (
            int(self.x + math.cos(self.angle - eye_angle) * eye_dist),
            int(self.y + math.sin(self.angle - eye_angle) * eye_dist)
        )
        eye2 = (
            int(self.x + math.cos(self.angle + eye_angle) * eye_dist),
            int(self.y + math.sin(self.angle + eye_angle) * eye_dist)
        )
        pygame.draw.circle(surface, (239, 68, 68), eye1, 2)
        pygame.draw.circle(surface, (239, 68, 68), eye2, 2)

class Pickup:
    def __init__(self, x, y, ptype):
        self.x = float(x)
        self.y = float(y)
        self.type = ptype # "medkit", "ammo", "speed"
        self.bounce_timer = random.uniform(0, 100)
        self.radius = 8
        self.collected = False
        
    def update(self):
        self.bounce_timer += 0.06
        
    def draw(self, surface):
        offset_y = math.sin(self.bounce_timer) * 4
        px = int(self.x)
        py = int(self.y + offset_y)
        
        if self.type == "medkit":
            color = (34, 197, 94) # Green
            symbol_color = (255, 255, 255)
        elif self.type == "ammo":
            color = (56, 189, 248) # Sky Cyan
            symbol_color = (255, 255, 255)
        else: # speed
            color = (253, 224, 71) # Gold Yellow
            symbol_color = (15, 23, 42)
            
        glow_size = 14 + int(math.sin(self.bounce_timer) * 2)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, 45), (glow_size, glow_size), glow_size)
        pygame.draw.circle(glow_surf, (*color, 110), (glow_size, glow_size), glow_size - 4)
        surface.blit(glow_surf, (px - glow_size, py - glow_size))
        
        pygame.draw.rect(surface, color, (px - 6, py - 6, 12, 12))
        pygame.draw.rect(surface, (255, 255, 255), (px - 6, py - 6, 12, 12), 1)
        
        if self.type == "medkit":
            pygame.draw.line(surface, symbol_color, (px - 3, py), (px + 3, py), 2)
            pygame.draw.line(surface, symbol_color, (px, py - 3), (px, py + 3), 2)
        elif self.type == "ammo":
            pygame.draw.rect(surface, symbol_color, (px - 2, py - 3, 4, 6))
        else:
            pygame.draw.line(surface, symbol_color, (px - 2, py + 3), (px + 2, py - 3), 2)

# -----------------------
# GAME CONTROLLER STATE
# -----------------------
class GameState:
    def __init__(self):
        self.state = "start" # start, play, win, game_over
        self.level = 1
        self.score = 0
        self.kills = 0
        self.time_elapsed = 0
        self.level_time = 0
        
        self.grid = []
        self.player = None
        self.zombies = []
        self.bullets = []
        self.particles = []
        self.pickups = []
        self.dijkstra_map = []
        
        self.start = pygame.Vector2(0, 0)
        self.goal = pygame.Vector2(0, 0)
        self.portal_angle = 0.0
        
        self.screenshake = 0
        
    def start_level(self, level=1):
        self.level = level
        self.grid = generate_maze(ROWS, COLS)
        
        self.start = pygame.Vector2(1 * TILE_SIZE + TILE_SIZE // 2, 1 * TILE_SIZE + TILE_SIZE // 2)
        self.goal = pygame.Vector2((COLS - 2) * TILE_SIZE + TILE_SIZE // 2, (ROWS - 2) * TILE_SIZE + TILE_SIZE // 2)
        
        self.player = Player(self.start.x, self.start.y)
        self.player.score = self.score
        self.player.kills = self.kills
        
        self.zombies.clear()
        self.bullets.clear()
        self.particles.clear()
        self.pickups.clear()
        
        spawnable_tiles = []
        for r in range(1, ROWS - 1):
            for c in range(1, COLS - 1):
                if self.grid[r][c] == 0:
                    dist_to_start = math.hypot(c * TILE_SIZE + 16 - self.start.x, r * TILE_SIZE + 16 - self.start.y)
                    if dist_to_start > TILE_SIZE * 8:
                        spawnable_tiles.append((r, c))
                        
        num_zombies = 10 + level * 3
        spawn_selections = random.sample(spawnable_tiles, min(len(spawnable_tiles), num_zombies))
        
        for r, c in spawn_selections:
            rand = random.random()
            zx = c * TILE_SIZE + TILE_SIZE // 2
            zy = r * TILE_SIZE + TILE_SIZE // 2
            
            if rand < 0.22 + (level * 0.03):
                self.zombies.append(Zombie(zx, zy, "runner"))
            elif rand > 0.85 - (level * 0.02):
                self.zombies.append(Zombie(zx, zy, "tank"))
            else:
                self.zombies.append(Zombie(zx, zy, "stalker"))
                
        self.dijkstra_map = update_dijkstra_map(self.grid, 1, 1)
        self.level_time = 0
        self.state = "play"

# Instantiation
game = GameState()

# -----------------------
# GAME LOOP FUNCTIONS
# -----------------------
def check_visibility(z_x, z_y, p_x, p_y, f_angle, grid):
    dist = math.hypot(z_x - p_x, z_y - p_y)
    if dist < 72:
        return True
        
    if dist < 265:
        entity_angle = math.atan2(z_y - p_y, z_x - p_x)
        diff = (entity_angle - f_angle + math.pi) % (2 * math.pi) - math.pi
        if abs(diff) < math.radians(33):
            # Raycast line of sight
            steps = int(dist // 10)
            for i in range(1, steps):
                pct = i / steps
                rx = p_x + (z_x - p_x) * pct
                ry = p_y + (z_y - p_y) * pct
                col = int(rx // TILE_SIZE)
                row = int(ry // TILE_SIZE)
                if 0 <= row < ROWS and 0 <= col < COLS:
                    if grid[row][col] == 1:
                        return False
            return True
            
    return False

def update_game():
    if game.screenshake > 0:
        game.screenshake -= 1
        
    game.level_time += 1
    if game.level_time % 60 == 0:
        game.time_elapsed += 1
        
    game.player.update()
    
    p_r = int(game.player.y // TILE_SIZE)
    p_c = int(game.player.x // TILE_SIZE)
    game.dijkstra_map = update_dijkstra_map(game.grid, p_r, p_c)
    
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        dy -= 1
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dy += 1
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        dx -= 1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        dx += 1
        
    game.player.move(dx, dy, game.grid)
    
    if keys[pygame.K_r]:
        game.player.start_reload()
        
    for p in game.pickups:
        p.update()
        p_dist = math.hypot(p.x - game.player.x, p.y - game.player.y)
        if p_dist < game.player.radius + p.radius:
            p.collected = True
            if p.type == "medkit":
                game.player.hp = min(game.player.max_hp, game.player.hp + 30)
                for _ in range(8):
                    game.particles.append(Particle(
                        game.player.x, game.player.y,
                        random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5),
                        (34, 197, 94), random.uniform(3, 5), random.randint(15, 25)
                    ))
            elif p.type == "ammo":
                game.player.ammo = game.player.max_ammo
                game.player.is_reloading = False
                for _ in range(8):
                    game.particles.append(Particle(
                        game.player.x, game.player.y,
                        random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5),
                        (56, 189, 248), random.uniform(3, 5), random.randint(15, 25)
                    ))
            else:
                game.player.speed_boost_time = 300
                for _ in range(12):
                    game.particles.append(Particle(
                        game.player.x, game.player.y,
                        random.uniform(-2.5, 2.5), random.uniform(-2.5, 2.5),
                        (253, 224, 71), random.uniform(3, 5), random.randint(20, 30)
                    ))
                    
    game.pickups = [p for p in game.pickups if not p.collected]
    
    bullets_to_keep = []
    for b in game.bullets:
        collided = b.update(game.grid)
        
        if collided:
            game.screenshake = max(game.screenshake, 2)
            for _ in range(6):
                spark_angle = math.atan2(-b.dy, -b.dx) + random.uniform(-0.6, 0.6)
                speed = random.uniform(1.5, 4.0)
                game.particles.append(Particle(
                    b.x, b.y,
                    math.cos(spark_angle) * speed, math.sin(spark_angle) * speed,
                    (251, 191, 36), random.uniform(2, 4), random.randint(10, 20)
                ))
            continue
            
        hit_enemy = False
        for z in game.zombies:
            dist = math.hypot(b.x - z.x, b.y - z.y)
            if dist < z.radius + b.radius:
                hit_enemy = True
                z.hp -= b.damage
                
                impact_angle = math.atan2(b.dy, b.dx)
                for _ in range(8):
                    sp_a = impact_angle + random.uniform(-0.5, 0.5)
                    sp_speed = random.uniform(1.0, 4.0)
                    game.particles.append(Particle(
                        z.x, z.y,
                        math.cos(sp_a) * sp_speed, math.sin(sp_a) * sp_speed,
                        (185, 28, 28) if z.type != "runner" else (249, 115, 22), 
                        random.uniform(2, 5), random.randint(15, 30)
                    ))
                
                if z.hp <= 0:
                    game.zombies.remove(z)
                    game.player.kills += 1
                    game.player.score += z.score_val
                    
                    if random.random() < 0.32:
                        loot_types = ["medkit", "ammo", "speed"]
                        choice = random.choice(loot_types)
                        if game.player.hp < 40 and random.random() < 0.6:
                            choice = "medkit"
                        elif game.player.ammo < 3 and random.random() < 0.6:
                            choice = "ammo"
                        game.pickups.append(Pickup(z.x, z.y, choice))
                break
                
        if not hit_enemy:
            bullets_to_keep.append(b)
            
    game.bullets = bullets_to_keep
    
    for z in game.zombies:
        z.update(game.grid, game.dijkstra_map, pygame.Vector2(game.player.x, game.player.y), game.zombies)
        
        dist = math.hypot(z.x - game.player.x, z.y - game.player.y)
        if dist < z.radius + game.player.radius:
            if game.player.invuln_timer == 0:
                damage_dealt = 20 if z.type == "tank" else (15 if z.type == "stalker" else 10)
                game.player.hp -= damage_dealt
                game.player.invuln_timer = 40
                game.screenshake = max(game.screenshake, 10)
                
                for _ in range(12):
                    game.particles.append(Particle(
                        game.player.x, game.player.y,
                        random.uniform(-3, 3), random.uniform(-3, 3),
                        (220, 38, 38), random.uniform(3, 6), random.randint(15, 30)
                    ))
                    
                if game.player.hp <= 0:
                    game.player.hp = 0
                    game.score = game.player.score
                    game.kills = game.player.kills
                    game.state = "game_over"
                    
    game.particles = [p for p in game.particles if not p.update()]
    
    escape_dist = math.hypot(game.player.x - game.goal.x, game.player.y - game.goal.y)
    if escape_dist < game.player.radius + 14:
        game.player.score += 1000
        game.score = game.player.score
        game.kills = game.player.kills
        game.state = "win"
        
    game.portal_angle += 0.04
    if random.random() < 0.2:
        pa = random.uniform(0, math.pi * 2)
        pr = random.uniform(2, 14)
        game.particles.append(Particle(
            game.goal.x + math.cos(pa) * pr, game.goal.y + math.sin(pa) * pr,
            random.uniform(-0.5, 0.5), random.uniform(-0.8, -0.2),
            (34, 197, 94), random.uniform(2, 4), random.randint(20, 40)
        ))

def draw_game():
    offset_x = 0
    offset_y = 0
    if game.screenshake > 0:
        offset_x = random.randint(-game.screenshake, game.screenshake)
        offset_y = random.randint(-game.screenshake, game.screenshake)
        
    game_surf = pygame.Surface((WIDTH, HEIGHT))
    game_surf.fill(COLOR_BG)
    
    # 1. Draw Maze Walls
    for r in range(ROWS):
        for c in range(COLS):
            if game.grid[r][c] == 1:
                block_rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(game_surf, COLOR_WALL, block_rect)
                pygame.draw.rect(game_surf, COLOR_WALL_BORDER, block_rect, 1)
                
    # 2. Draw Spawn point & Goal portal
    pygame.draw.circle(game_surf, (15, 23, 42), (int(game.start.x), int(game.start.y)), 16)
    pygame.draw.circle(game_surf, (56, 189, 248), (int(game.start.x), int(game.start.y)), 16, 2)
    
    glow_val = 14 + int(math.sin(game.portal_angle * 3) * 3)
    pygame.draw.circle(game_surf, (22, 101, 52), (int(game.goal.x), int(game.goal.y)), glow_val + 4)
    pygame.draw.circle(game_surf, COLOR_GOAL, (int(game.goal.x), int(game.goal.y)), glow_val, 2)
    pygame.draw.circle(game_surf, (187, 247, 208), (int(game.goal.x), int(game.goal.y)), 6)
    
    exit_text = FONT_HUD.render("EXIT", True, COLOR_GOAL)
    game_surf.blit(exit_text, (int(game.goal.x) - 18, int(game.goal.y) - 26))
    
    # 3. Draw visible Pickups (Pickups are drawn fully under dark but will be multiplied)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    f_angle = game.player.angle
    for p in game.pickups:
        p.draw(game_surf)
        
    # 4. Draw Bullets
    for b in game.bullets:
        b.draw(game_surf)
        
    # 5. Draw illuminated Zombies (full bodies drawn before multiply)
    illuminated_zombies = []
    dark_zombies = []
    
    for z in game.zombies:
        if check_visibility(z.x, z.y, game.player.x, game.player.y, f_angle, game.grid):
            illuminated_zombies.append(z)
            z.draw_body(game_surf)
        else:
            dark_zombies.append(z)
            
    # 6. Draw Player
    game.player.draw(game_surf, mouse_x, mouse_y)
    
    # 7. Draw Particles
    for p in game.particles:
        p.draw(game_surf)
        
    # -----------------------
    # DYNAMIC LIGHT MASK (MULTIPLY BUFFER)
    # -----------------------
    light_mask = pygame.Surface((WIDTH, HEIGHT))
    light_mask.fill(COLOR_DARKNESS) # Dark tinted blue
    
    # Trace flashlight boundaries
    cone_points = [(game.player.x, game.player.y)]
    num_steps = 16
    start_angle = f_angle - math.radians(28)
    end_angle = f_angle + math.radians(28)
    step = math.radians(56) / num_steps
    for i in range(num_steps + 1):
        a = start_angle + i * step
        max_dist = 265
        steps = int(max_dist // 12)
        final_dist = max_dist
        for s in range(1, steps):
            test_r = s * 12
            tx = game.player.x + math.cos(a) * test_r
            ty = game.player.y + math.sin(a) * test_r
            tc = int(tx // TILE_SIZE)
            tr = int(ty // TILE_SIZE)
            if 0 <= tr < ROWS and 0 <= tc < COLS:
                if game.grid[tr][tc] == 1:
                    final_dist = test_r
                    break
        px = game.player.x + math.cos(a) * final_dist
        py = game.player.y + math.sin(a) * final_dist
        cone_points.append((px, py))
        
    # Wide soft cone
    cone_points_wide = [(game.player.x, game.player.y)]
    start_angle_w = f_angle - math.radians(42)
    end_angle_w = f_angle + math.radians(42)
    step_w = math.radians(84) / num_steps
    for i in range(num_steps + 1):
        a = start_angle_w + i * step_w
        max_dist = 230
        steps = int(max_dist // 12)
        final_dist = max_dist
        for s in range(1, steps):
            test_r = s * 12
            tx = game.player.x + math.cos(a) * test_r
            ty = game.player.y + math.sin(a) * test_r
            tc = int(tx // TILE_SIZE)
            tr = int(ty // TILE_SIZE)
            if 0 <= tr < ROWS and 0 <= tc < COLS:
                if game.grid[tr][tc] == 1:
                    final_dist = test_r
                    break
        px = game.player.x + math.cos(a) * final_dist
        py = game.player.y + math.sin(a) * final_dist
        cone_points_wide.append((px, py))
        
    # Draw soft outer cone (grey)
    if len(cone_points_wide) > 2:
        pygame.draw.polygon(light_mask, (100, 100, 115), cone_points_wide)
        
    # Draw bright inner cone (white)
    if len(cone_points) > 2:
        pygame.draw.polygon(light_mask, (255, 255, 255), cone_points)
        
    # Draw radial halo glow centered on player
    for r in range(72, 0, -4):
        pct = (72 - r) / 72
        # Lerp from ambient dark to full white light
        r_val = int(COLOR_DARKNESS[0] + (255 - COLOR_DARKNESS[0]) * pct)
        g_val = int(COLOR_DARKNESS[1] + (255 - COLOR_DARKNESS[1]) * pct)
        b_val = int(COLOR_DARKNESS[2] + (255 - COLOR_DARKNESS[2]) * pct)
        pygame.draw.circle(light_mask, (r_val, g_val, b_val), (int(game.player.x), int(game.player.y)), r)
        
    # Apply Multiply Lighting filter
    game_surf.blit(light_mask, (0, 0), special_flags=pygame.BLEND_MULT)
    
    # -----------------------
    # STEALTH DRAWING (drawn after light multiplier to bypass shadows!)
    # -----------------------
    # Draw glowing zombie eyes in the dark!
    for z in dark_zombies:
        z.draw_eyes(game_surf)
        
    # Present onto screen
    screen.blit(game_surf, (offset_x, offset_y))
    
    # -----------------------
    # DRAW HUD
    # -----------------------
    hud_bg = pygame.Surface((310, 75), pygame.SRCALPHA)
    pygame.draw.rect(hud_bg, (15, 23, 42, 185), (0, 0, 310, 75), border_bottom_right_radius=8)
    pygame.draw.rect(hud_bg, (56, 189, 248, 120), (0, 0, 310, 75), 1, border_bottom_right_radius=8)
    screen.blit(hud_bg, (0, 0))
    
    # 1. Health Bar
    hp_pct = game.player.hp / game.player.max_hp
    hp_color = (34, 197, 94) if hp_pct > 0.5 else ((234, 179, 8) if hp_pct > 0.25 else (239, 68, 68))
    hp_text = FONT_HUD.render(f"VITALITY: {game.player.hp}%", True, hp_color)
    screen.blit(hp_text, (15, 8))
    pygame.draw.rect(screen, (30, 41, 59), (15, 26, 150, 10))
    pygame.draw.rect(screen, hp_color, (15, 26, int(150 * hp_pct), 10))
    pygame.draw.rect(screen, (255, 255, 255), (15, 26, 150, 10), 1)
    
    # 2. Ammo Count & reloading indicators
    ammo_color = (56, 189, 248) if game.player.ammo > 0 else (239, 68, 68)
    ammo_text = FONT_HUD.render(f"MAGAZINE: {game.player.ammo}/{game.player.max_ammo}", True, ammo_color)
    screen.blit(ammo_text, (15, 42))
    
    for i in range(game.player.max_ammo):
        bx = 15 + i * 8
        by = 58
        b_color = (56, 189, 248) if i < game.player.ammo else (71, 85, 105)
        pygame.draw.rect(screen, b_color, (bx, by, 5, 8))
        
    if game.player.is_reloading:
        pct_done = 1.0 - (game.player.reload_timer / game.player.reload_duration)
        bar_w = 26
        bar_h = 4
        bx = game.player.x - 13 - offset_x
        by = game.player.y - 18 - offset_y
        pygame.draw.rect(screen, (30, 41, 59), (bx, by, bar_w, bar_h))
        pygame.draw.rect(screen, (253, 224, 71), (bx, by, int(bar_w * pct_done), bar_h))
        pygame.draw.rect(screen, (255, 255, 255), (bx, by, bar_w, bar_h), 1)
        
        reload_text = FONT_HUD.render("RELOADING", True, (253, 224, 71))
        screen.blit(reload_text, (125, 42))
        
    # 3. Speed Boost Indicator
    if game.player.speed_boost_time > 0:
        boost_pct = game.player.speed_boost_time / 300
        pygame.draw.rect(screen, (30, 41, 59), (180, 26, 110, 10))
        pygame.draw.rect(screen, (253, 224, 71), (180, 26, int(110 * boost_pct), 10))
        pygame.draw.rect(screen, (255, 255, 255), (180, 26, 110, 10), 1)
        
        boost_lbl = FONT_HUD.render("OVERDRIVE BOOST", True, (253, 224, 71))
        screen.blit(boost_lbl, (180, 8))
        
    # Top-Right HUD Card (Level / Score details)
    score_card = pygame.Surface((250, 70), pygame.SRCALPHA)
    pygame.draw.rect(score_card, (15, 23, 42, 185), (0, 0, 250, 70), border_bottom_left_radius=8)
    pygame.draw.rect(score_card, (56, 189, 248, 120), (0, 0, 250, 70), 1, border_bottom_left_radius=8)
    screen.blit(score_card, (WIDTH - 250, 0))
    
    lbl_level = FONT_HUD.render(f"MISSION SECTOR: #{game.level:02d}", True, (253, 224, 71))
    lbl_score = FONT_HUD.render(f"SECURED DATA : {game.player.score:05d}", True, COLOR_HUD_TEXT)
    lbl_kills = FONT_HUD.render(f"ZOMBIES PURGED: {game.player.kills:03d}", True, (239, 68, 68))
    
    screen.blit(lbl_level, (WIDTH - 235, 8))
    screen.blit(lbl_score, (WIDTH - 235, 26))
    screen.blit(lbl_kills, (WIDTH - 235, 44))

# -----------------------
# MENU / STATE DRAWING
# -----------------------
def draw_start_screen():
    screen.fill(COLOR_BG)
    
    # Sleek digital grid backing
    for x in range(0, WIDTH, TILE_SIZE * 2):
        pygame.draw.line(screen, (15, 23, 42), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, TILE_SIZE * 2):
        pygame.draw.line(screen, (15, 23, 42), (0, y), (WIDTH, y))
        
    # Glowing titles
    title_surf = FONT_TITLE.render("SHADOW ESCAPE", True, (239, 68, 68))
    sub_surf = FONT_SUBTITLE.render("AI APOCALYPSE: SMART ZOMBIES IN THE DARK", True, (56, 189, 248))
    
    screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 3 - 60))
    screen.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, HEIGHT // 3 + 10))
    
    # Instruction board
    inst_bg = pygame.Surface((480, 210), pygame.SRCALPHA)
    pygame.draw.rect(inst_bg, (30, 41, 59, 140), (0, 0, 480, 210), border_radius=8)
    pygame.draw.rect(inst_bg, (56, 189, 248, 80), (0, 0, 480, 210), 1, border_radius=8)
    screen.blit(inst_bg, (WIDTH // 2 - 240, HEIGHT // 2 - 30))
    
    inst_lines = [
        "TACTICAL COMMAND OVERVIEW:",
        "------------------------------------",
        "• [W, A, S, D]  - Navigational movement",
        "• [Mouse Aim]   - Target flashlight beam & scope",
        "• [Left Click]  - Discharging firearm projectiles",
        "• [Key R]       - Engage magazine reload",
        "• [Objective]   - Evade monsters, retrieve portal EXIT"
    ]
    
    for i, line in enumerate(inst_lines):
        color = (253, 224, 71) if i == 0 else ((56, 189, 248) if i == 1 else COLOR_HUD_TEXT)
        lbl = FONT_HUD.render(line, True, color)
        screen.blit(lbl, (WIDTH // 2 - 220, HEIGHT // 2 - 18 + i * 24))
        
    pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.004)) * 255)
    prompt = FONT_SUBTITLE.render("CLICK MOUSE TO INITIALIZE COMMAND SYSTEM", True, (pulse, pulse, 255))
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 90))

def draw_victory_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 11, 16, 200))
    screen.blit(overlay, (0, 0))
    
    vic_title = FONT_BIG.render("MISSION SUCCESSFUL", True, COLOR_GOAL)
    sub_title = FONT_SUBTITLE.render(f"SECTOR {game.level:02d} DATA SECURED", True, COLOR_HUD_TEXT)
    
    screen.blit(vic_title, (WIDTH // 2 - vic_title.get_width() // 2, HEIGHT // 3 - 60))
    screen.blit(sub_title, (WIDTH // 2 - sub_title.get_width() // 2, HEIGHT // 3 + 10))
    
    card = pygame.Surface((380, 160), pygame.SRCALPHA)
    pygame.draw.rect(card, (30, 41, 59, 150), (0, 0, 380, 160), border_radius=8)
    pygame.draw.rect(card, COLOR_GOAL, (0, 0, 380, 160), 1, border_radius=8)
    screen.blit(card, (WIDTH // 2 - 190, HEIGHT // 2 - 30))
    
    stat_score = FONT_HUD.render(f"CURRENT SCORE   : {game.player.score}", True, COLOR_HUD_TEXT)
    stat_kills = FONT_HUD.render(f"ZOMBIES REMOVED : {game.player.kills}", True, (239, 68, 68))
    stat_time = FONT_HUD.render(f"TOTAL RUNTIME   : {game.time_elapsed} seconds", True, (56, 189, 248))
    stat_hp = FONT_HUD.render(f"REMAINING HEALTH: {game.player.hp}%", True, COLOR_GOAL)
    
    screen.blit(stat_score, (WIDTH // 2 - 160, HEIGHT // 2 - 15))
    screen.blit(stat_kills, (WIDTH // 2 - 160, HEIGHT // 2 + 10))
    screen.blit(stat_time, (WIDTH // 2 - 160, HEIGHT // 2 + 35))
    screen.blit(stat_hp, (WIDTH // 2 - 160, HEIGHT // 2 + 60))
    
    pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.004)) * 255)
    prompt = FONT_SUBTITLE.render("PRESS [ENTER] TO ADVANCE SECTOR", True, (pulse, 255, pulse))
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 100))

def draw_game_over_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((20, 10, 10, 220))
    screen.blit(overlay, (0, 0))
    
    title = FONT_BIG.render("SYSTEM FAILURE: CONSUMED", True, (239, 68, 68))
    sub = FONT_SUBTITLE.render("YOU WERE OVERRUN BY INTELLIGENT AI HORDE", True, COLOR_HUD_TEXT)
    
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3 - 60))
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 3 + 10))
    
    card = pygame.Surface((380, 130), pygame.SRCALPHA)
    pygame.draw.rect(card, (30, 41, 59, 150), (0, 0, 380, 130), border_radius=8)
    pygame.draw.rect(card, (239, 68, 68), (0, 0, 380, 130), 1, border_radius=8)
    screen.blit(card, (WIDTH // 2 - 190, HEIGHT // 2 - 10))
    
    stat_score = FONT_HUD.render(f"FINAL RECORDED SCORE: {game.score}", True, COLOR_HUD_TEXT)
    stat_kills = FONT_HUD.render(f"THREATS ELIMINATED  : {game.kills}", True, (239, 68, 68))
    stat_time = FONT_HUD.render(f"LIFETIME RUNTIME    : {game.time_elapsed} seconds", True, (56, 189, 248))
    
    screen.blit(stat_score, (WIDTH // 2 - 160, HEIGHT // 2 + 5))
    screen.blit(stat_kills, (WIDTH // 2 - 160, HEIGHT // 2 + 30))
    screen.blit(stat_time, (WIDTH // 2 - 160, HEIGHT // 2 + 55))
    
    pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.004)) * 255)
    prompt = FONT_SUBTITLE.render("PRESS [R] TO REBOOT COMMAND INTERFACE", True, (253, pulse, pulse))
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT - 120))

# -----------------------
# MAIN RUN FUNCTION
# -----------------------
def main():
    running = True
    
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game.state == "start":
                    game.start_level(1)
                elif game.state == "play":
                    if event.button == 1: # Left Click
                        m_x, m_y = pygame.mouse.get_pos()
                        game.player.shoot(m_x, m_y, game.bullets, game.particles)
                        
            elif event.type == pygame.KEYDOWN:
                if game.state == "win":
                    if event.key == pygame.K_RETURN:
                        game.start_level(game.level + 1)
                elif game.state == "game_over":
                    if event.key == pygame.K_r:
                        game.score = 0
                        game.kills = 0
                        game.time_elapsed = 0
                        game.start_level(1)
                        
        if game.state == "start":
            draw_start_screen()
        elif game.state == "play":
            update_game()
            draw_game()
        elif game.state == "win":
            # Keep particles updating during pause screens
            game.particles = [p for p in game.particles if not p.update()]
            game.portal_angle += 0.04
            draw_game()
            draw_victory_screen()
        elif game.state == "game_over":
            draw_game()
            draw_game_over_screen()
            
        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    main()