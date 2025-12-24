from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time
import math

#global variables 

WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 800
WINDOW_TITLE = b"Urban Rush: Traffic Dodger"

#lane config
LANE_COORDINATES = [-150, -50, 50, 150]

#game constants
PLAYER_START_LANE = 2
PLAYER_BASE_SPEED = 3.0
PLAYER_NITRO_SPEED = 12.0

MAX_HEALTH = 10
NITRO_CAPACITY = 100.0
NITRO_DRAIN = 1.5
NITRO_REFILL = 0.5

#visual
SPAWN_Z = -1800
DESPAWN_Z = 300
VIEW_DISTANCE = 3000

#color
COLOR_GRASS = (0.0, 0.8, 0.0)    
COLOR_ROAD = (0.2, 0.2, 0.2) 
COLOR_STRIPE = (1.0, 1.0, 0.0)
COLOR_SKY_DAY = (0.53, 0.81, 0.92)
COLOR_SKY_NIGHT = (0.05, 0.05, 0.10)
COLOR_SKY_RAIN = (0.25, 0.30, 0.35)

#global state
player_lane_idx = 2
player_x = 50
player_z = 0
current_speed = 3.0
distance_traveled = 0.0
last_frame_time = 0

#difficulty
base_traffic_speed = 4.0
current_traffic_speed = 4.0
speed_level = 0
speed_up_display_timer = 0

health = 10
collision_count = 0
damage_percent = 0.0
score = 0
coins_collected = 0

paused = False
game_over = False
camera_mode = 1

nitro_amount = 100.0
nitro_active = False
nitro_refilling = False

lights_on = False
cheat_mode = False
autopilot_cd = 0

time_dilation = 1.0
slow_mo_timer = 0

#global features
magnet_active = False
magnet_timer = 0
barriers = [] 
env_idx = 0
env_timer = 0
ENV_CYCLE = 1200

#entities
traffic = []
scenery = []
coins = []
particles = []

#initialization

def init():
    global player_lane_idx, player_x, player_z, current_speed, distance_traveled
    global health, collision_count, damage_percent, score, coins_collected
    global paused, game_over, nitro_amount, nitro_active, nitro_refilling
    global lights_on, cheat_mode, traffic, scenery, coins, particles, time_dilation
    global current_traffic_speed, speed_level, speed_up_display_timer, last_frame_time
    global magnet_active, magnet_timer, barriers
    
    player_lane_idx = PLAYER_START_LANE
    player_x = LANE_COORDINATES[player_lane_idx]
    player_z = 0
    current_speed = PLAYER_BASE_SPEED
    distance_traveled = 0.0
    last_frame_time = time.time()
    
    current_traffic_speed = base_traffic_speed
    speed_level = 0
    speed_up_display_timer = 0
    
    health = MAX_HEALTH
    collision_count = 0
    damage_percent = 0.0
    score = 0
    coins_collected = 0
    
    paused = False
    game_over = False
    
    nitro_amount = NITRO_CAPACITY
    nitro_active = False
    nitro_refilling = False
    
    lights_on = False
    cheat_mode = False
    time_dilation = 1.0
    
#new feature reset
    magnet_active = False
    magnet_timer = 0
    barriers = []
    
    traffic = []
    scenery = []
    coins = []
    particles = []
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, WINDOW_WIDTH/WINDOW_HEIGHT, 10, VIEW_DISTANCE)
    glMatrixMode(GL_MODELVIEW)

#manual drawing  

def draw_box(x, y, z, w, h, l, color):
    w, h, l = w/2, h/2, l/2
    glPushMatrix()
    glTranslatef(x, y, z)
    glBegin(GL_QUADS)
    glColor3f(*color)
#faces
    glVertex3f(-w,-h,l); glVertex3f(w,-h,l); glVertex3f(w,h,l); glVertex3f(-w,h,l)
    glVertex3f(-w,-h,-l); glVertex3f(-w,h,-l); glVertex3f(w,h,-l); glVertex3f(w,-h,-l)
    glVertex3f(-w,h,-l); glVertex3f(-w,h,l); glVertex3f(w,h,l); glVertex3f(w,h,-l)
    glVertex3f(-w,-h,-l); glVertex3f(w,-h,-l); glVertex3f(w,-h,l); glVertex3f(-w,-h,l)
    glVertex3f(w,-h,-l); glVertex3f(w,h,-l); glVertex3f(w,h,l); glVertex3f(w,-h,l)
    glVertex3f(-w,-h,-l); glVertex3f(-w,-h,l); glVertex3f(-w,h,l); glVertex3f(-w,h,-l)
    glEnd()
    glPopMatrix()

def draw_pyramid(x, y, z, base_w, height, color):
    w = base_w / 2
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(*color)
    glBegin(GL_TRIANGLES)
    glVertex3f(0,height,0); glVertex3f(-w,0,w); glVertex3f(w,0,w)
    glVertex3f(0,height,0); glVertex3f(w,0,w); glVertex3f(w,0,-w)
    glVertex3f(0,height,0); glVertex3f(w,0,-w); glVertex3f(-w,0,-w)
    glVertex3f(0,height,0); glVertex3f(-w,0,-w); glVertex3f(-w,0,w)
    glEnd()
    glPopMatrix()

def draw_circle_manual(radius, color):
    glPushMatrix()
    glColor3f(*color)
    glBegin(GL_TRIANGLES)
    
    num_segments = 32 
    for i in range(num_segments):
        #calculate angles of current slice
        theta1 = 2.0 * math.pi * float(i) / float(num_segments)
        theta2 = 2.0 * math.pi * float(i + 1) / float(num_segments)
        
        #calculate points on the rim
        x1 = radius * math.cos(theta1)
        y1 = radius * math.sin(theta1)
        
        x2 = radius * math.cos(theta2)
        y2 = radius * math.sin(theta2)
        
        #draws triangle 
        glVertex3f(0, 0, 0) #center
        glVertex3f(x1, y1, 0) #rim point A
        glVertex3f(x2, y2, 0) #point B
        
    glEnd()
    glPopMatrix()

def draw_rect(x, z, w, l, color, y_off=0.0):
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex3f(x-w/2, y_off, z+l/2)
    glVertex3f(x+w/2, y_off, z+l/2)
    glVertex3f(x+w/2, y_off, z-l/2)
    glVertex3f(x-w/2, y_off, z-l/2)
    glEnd()

#3d models

def draw_car(x, z, color, is_player, is_oncoming=True):
    W, H, L = 24, 14, 40
    glPushMatrix()
    glTranslatef(x, 10, z)
    if is_oncoming: glRotatef(180, 0, 1, 0)
    
#body
    draw_box(0, 0, 0, W, H, L, color)
    draw_box(0, H, -2, W*0.85, H*0.7, L*0.6, (color[0]*0.7, color[1]*0.7, color[2]*0.7))
    draw_box(0, H, -2-L*0.3, W*0.75, H*0.6, 1, (0.6, 0.8, 1.0))
    
#wheel
    spin = (distance_traveled * 15) % 360
    for wx in [-W/2-2, W/2+2]:
        for wz in [-L/3, L/3]:
            glPushMatrix()
            glTranslatef(wx, -H/2, wz)
            glRotatef(spin, 1, 0, 0)
            draw_box(0, 0, 0, 4, 10, 10, (0.1, 0.1, 0.1))
            glPopMatrix()
            
#lights in physical housing
    l_active = True if is_oncoming else lights_on
    hl_col = (1, 1, 0) if l_active else (0.2, 0.2, 0.0)
    
    draw_box(-8, 2, -L/2-1, 6, 4, 1, hl_col)
    draw_box( 8, 2, -L/2-1, 6, 4, 1, hl_col)
    draw_box(-8, 2,  L/2+1, 6, 4, 1, (1, 0, 0))
    draw_box( 8, 2,  L/2+1, 6, 4, 1, (1, 0, 0))
    
#fixed headlights 
    if is_player and lights_on:
        glBegin(GL_LINES)
        
        beam_length = 250
        beam_spread = 35
        
    #left headlight fan
        for i in range(-5, 6): #11 rays
            offset = i * (beam_spread / 5)
            glColor3f(1, 1, 0) #source-yellow
            glVertex3f(-8, 2, -L/2-1)
            glColor3f(0.2, 0.2, 0.2) #target-road color fade
            glVertex3f(-8 + offset, 0, -L/2 - beam_length)

    #right headlight fan
        for i in range(-5, 6):
            offset = i * (beam_spread / 5)
            glColor3f(1, 1, 0) 
            glVertex3f(8, 2, -L/2-1)
            glColor3f(0.2, 0.2, 0.2) 
            glVertex3f(8 + offset, 0, -L/2 - beam_length)
            
        glEnd()

    glPopMatrix()

def draw_barrier(x, z):
    #concrete base
    draw_box(x, 10, z, 30, 20, 10, (0.6, 0.6, 0.6))
    #warning stripes  in black n yellow
    draw_box(x-10, 10, z+1, 5, 20, 11, (1, 0.8, 0))
    draw_box(x, 10, z+1, 5, 20, 11, (0.1, 0.1, 0.1))
    draw_box(x+10, 10, z+1, 5, 20, 11, (1, 0.8, 0))

def draw_smoke():
    for p in particles:
        sz = p['size'] * p['life']
        c_val = 0.5 * p['life']
        draw_box(p['x'], p['y'], p['z'], sz, sz, sz, (c_val, c_val, c_val))

def draw_tree(x, z):
    draw_box(x, 15, z, 10, 30, 10, (0.4, 0.2, 0.1))
    col = (0.05, 0.4, 0.05) if env_idx != 2 else (0.02, 0.15, 0.02)
    draw_pyramid(x, 30, z, 40, 30, col)
    draw_pyramid(x, 45, z, 30, 25, col)

def draw_building(x, z, h):
    col = (0.5, 0.5, 0.55) if env_idx != 2 else (0.2, 0.2, 0.25)
    draw_box(x, h/2, z, 60, h, 60, col)
    if z > -1500:
        win = (1, 1, 0.5) if env_idx == 2 else (0.1, 0.2, 0.4)
        for i in range(int(h/30)):
            draw_box(x, i*30+15, z+31, 50, 10, 2, win)

def draw_coin_obj(x, z, type_s):
    glPushMatrix()
    glTranslatef(x, 20, z)
    #rotate around y to spin
    glRotatef((time.time()*200)%360, 0, 1, 0)
    
    col = (1, 0.8, 0) # gold
    if type_s == 'timer': col = (0, 1, 1) #color-cyan
    elif type_s == 'magnet': col = (1, 0, 1) #color-purple
        
    #draw flat circle
    draw_circle_manual(12, col)
    glPopMatrix()

#render logic
def setupCamera():
    if camera_mode == 1:
        gluLookAt(0, 200, 350, 0, 0, -200, 0, 1, 0)
    else:
        gluLookAt(player_x, 20, 0, player_x, 20, -200, 0, 1, 0)

def draw_shapes():
#background
    grass = COLOR_GRASS if env_idx != 2 else (0.0, 0.2, 0.0)
    draw_rect(0, 0, 4000, 4000, grass, 0.0)
    scroll = distance_traveled % 100
    draw_rect(0, 0, 400, 4000, COLOR_ROAD, 0.1)
    
#road stripe
    for i in range(-25, 20):
        z = -i * 100 + scroll
        draw_rect(-5, z, 2, 50, COLOR_STRIPE, 0.2)
        draw_rect( 5, z, 2, 50, COLOR_STRIPE, 0.2)
        draw_rect(-100, z, 2, 40, (1,1,1), 0.2)
        draw_rect( 100, z, 2, 40, (1,1,1), 0.2)
        draw_rect(-210, z, 20, 100, (0.4,0.4,0.4), 0.2)
        draw_rect( 210, z, 20, 100, (0.4,0.4,0.4), 0.2)

#scenery
    for s in scenery:
        if s['type']=='tree': draw_tree(s['x'], s['z'])
        else: draw_building(s['x'], s['z'], s['height'])
    
#game objects
    for b in barriers: draw_barrier(b['x'], b['z'])
    for c in coins: draw_coin_obj(c['x'], c['z'], c['type'])
    for t in traffic: draw_car(t['x'], t['z'], t['color'], False, True)
    
#player
    draw_car(player_x, 0, (0.9, 0.1, 0.1), True, False)
    draw_smoke()
    
#rain effects
    if env_idx == 1:
        glLineWidth(1); glBegin(GL_LINES); glColor3f(0.7, 0.7, 0.8)
        for _ in range(300):
            rx=random.randint(-400,400); ry=random.randint(0,300); rz=random.randint(-500,200)
            glVertex3f(rx,ry,rz); glVertex3f(rx-5, ry-20, rz+5)
        glEnd()

def draw_text(x, y, text, color=(1,1,1)):
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glColor3f(*color); glRasterPos2f(x,y)
    for c in text: glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(c))
    glPopMatrix(); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW)

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT); glLoadIdentity() #enable depth test is active here
    
    bg = COLOR_SKY_DAY
    if env_idx == 1: bg = COLOR_SKY_RAIN
    if env_idx == 2: bg = COLOR_SKY_NIGHT
    glClearColor(*bg, 1.0)
    
    setupCamera()
    draw_shapes()
    
    #HUD
    draw_text(20, 770, f"SCORE: {int(score)}")
    draw_text(20, 750, f"COINS: {coins_collected}", (1, 0.8, 0))
    draw_text(20, 730, f"DIST : {int(distance_traveled/100)}m")
    draw_text(20, 700, f"COLLISIONS: {collision_count}")
    
    dcol = (0,1,0) if damage_percent < 40 else (1,1,0) if damage_percent < 70 else (1,0,0)
    draw_text(20, 680, f"DAMAGE: {damage_percent}%", dcol)
    
    ntxt = "NITRO READY"; ncol = (0,1,1)
    if nitro_active: ntxt="NITRO BOOST!"; ncol=(1,0.6,0)
    if nitro_refilling: ntxt="RECHARGING"; ncol=(0.5,0.5,0.5)
    draw_text(20, 660, f"{ntxt} [{int(nitro_amount)}%]", ncol)
    
    if lights_on: draw_text(850, 770, "LIGHTS: ON", (1,1,0))
    else: draw_text(850, 770, "LIGHTS: OFF", (0.5,0.5,0.5))
    
    if speed_up_display_timer > 0:
        draw_text(400, 600, "SPEED UP !!!", (1, 0, 0))
    
    if magnet_active:
        draw_text(400, 640, f"MAGNET ACTIVE! {int(magnet_timer/60)}s", (1, 0, 1))

    if cheat_mode: draw_text(400, 770, "AUTO-PILOT ON", (0,1,0))
    if time_dilation < 1.0: draw_text(400, 720, "TIME SLOW", (0,1,1))
    
    if game_over:
        draw_text(400, 400, "GAME OVER", (1,0,0))
        draw_text(380, 370, "PRESS R TO RESTART")
    glutSwapBuffers()

#animation n inputs 
def animate():
    global distance_traveled, score, nitro_amount, nitro_active, nitro_refilling
    global current_speed, env_timer, env_idx, slow_mo_timer, time_dilation
    global health, damage_percent, collision_count, game_over
    global traffic, scenery, coins, barriers, autopilot_cd, player_lane_idx, player_x
    global coins_collected, current_traffic_speed, speed_level, speed_up_display_timer, particles
    global last_frame_time, magnet_active, magnet_timer

    current_time = time.time()
    if current_time - last_frame_time < 0.016: 
        return
    last_frame_time = current_time
    
    if not paused and not game_over:
        env_timer += 1
        if env_timer > ENV_CYCLE:
            env_idx = (env_idx + 1) % 3
            env_timer = 0
        
        new_level = int(distance_traveled // 6000)
        if new_level > speed_level:
            speed_level = new_level
            current_traffic_speed += 1.0 
            speed_up_display_timer = 60
        if speed_up_display_timer > 0: speed_up_display_timer -= 1
        
        
        if magnet_active:          #magnet logic
            magnet_timer -= 1
            if magnet_timer <= 0: magnet_active = False
            for c in coins:       #pull coins towards player
                if c['z'] > -400 and c['z'] < 100: #if coin is somewhat near
                    if c['x'] < player_x: c['x'] += 5.0
                    if c['x'] > player_x: c['x'] -= 5.0
        
        target = PLAYER_BASE_SPEED
        if nitro_active:
            if nitro_amount > 0:
                target = PLAYER_NITRO_SPEED
                nitro_amount -= NITRO_DRAIN
            else:
                nitro_active = False
                nitro_refilling = True
        elif nitro_refilling:
            nitro_amount += NITRO_REFILL
            if nitro_amount >= NITRO_CAPACITY: nitro_refilling = False
        current_speed = target
        
        if slow_mo_timer > 0:
            slow_mo_timer -= 1
            if slow_mo_timer == 0: time_dilation = 1.0
            
        move = current_speed * time_dilation
        distance_traveled += move
        score += move * 0.1
        
        if damage_percent > 0:
            prob = (damage_percent / 100.0) * 0.5
            if random.random() < prob:
                particles.append({'x': player_x+random.uniform(-5,5), 'y': 10, 'z': 20, 
                                  'life': 1.0, 'size': random.uniform(2,5)})
        for p in particles:
            p['y'] += 1.0; p['z'] += move; p['life'] -= 0.02
        particles[:] = [p for p in particles if p['life'] > 0]
        
    #spawning logic traffic n barriers
        if random.random() < 0.03 * time_dilation:
            l = random.randint(0, 3)
            safe = True           
            for c in traffic:            #check cars
                if c['lane']==l and abs(c['z']-SPAWN_Z)<250: safe=False
            for b in barriers:                # check barriers
                if b['lane']==l and abs(b['z']-SPAWN_Z)<250: safe=False
            
            if safe:                
                if random.random() < 0.10:       #10% chance to spawn a barrier instead of a car
                    barriers.append({'x': LANE_COORDINATES[l], 'z': SPAWN_Z, 'lane': l})
                else:
                    traffic.append({'x': LANE_COORDINATES[l], 'z': SPAWN_Z, 'lane': l, 
                                   'speed': current_traffic_speed, 'color': (random.random(),random.random(),random.random())})
        
        if random.random() < 0.15:
            x = random.choice([-1,1]) * random.randint(250, 600)
            typ = 'building' if random.random()<0.2 else 'tree'
            h = random.randint(100, 400) if typ=='building' else 0
            scenery.append({'x': x, 'z': SPAWN_Z, 'type': typ, 'height': h})
            
        if random.random() < 0.015: #slightly increased coin spawn rate
            l = random.randint(0, 3)
            #coin types- normal 85%, timer 10%, magnet 5%
            r = random.random()
            typ = 'score'
            if r < 0.05: typ = 'magnet'
            elif r < 0.15: typ = 'timer'
            
            coins.append({'x': LANE_COORDINATES[l], 'z': SPAWN_Z, 'type': typ})
            
 #update position
        for c in traffic: c['z'] += move + (c['speed'] * time_dilation)
        for b in barriers: b['z'] += move #barriers don't move forward on their own
        for s in scenery: s['z'] += move
        for c in coins: c['z'] += move
        
        #cleanup
        traffic[:] = [x for x in traffic if x['z'] < DESPAWN_Z]
        barriers[:] = [x for x in barriers if x['z'] < DESPAWN_Z]
        scenery[:] = [x for x in scenery if x['z'] < DESPAWN_Z]
        coins[:] = [x for x in coins if x['z'] < DESPAWN_Z]
        
#collisions
        px = player_x        
        for c in traffic:      #car collision
            if abs(c['x']-px)<30 and abs(c['z'])<30:
                if health > 0:
                    health -= 1
                    collision_count += 1
                    damage_percent = int((1 - (health/MAX_HEALTH))*100)
                    traffic.remove(c)
                    if health <= 0: game_over = True
                break
                
        for b in barriers:        #barrier collision causing high damage
            if abs(b['x']-px)<30 and abs(b['z'])<30:
                if health > 0:
                    health -= 3      #barriers hurt more
                    collision_count += 1
                    damage_percent = int((1 - (health/MAX_HEALTH))*100)
                    barriers.remove(b)
                    if health <= 0: game_over = True
                break
        
        for c in coins:     #coin collection
            if abs(c['x']-px)<30 and abs(c['z'])<30:
                if c['type']=='timer':
                    time_dilation = 0.5
                    slow_mo_timer = 300
                elif c['type']=='magnet':
                    magnet_active = True
                    magnet_timer = 300    #5 seconds {60fps*5}
                else:
                    score += 1000
                    coins_collected += 1
                coins.remove(c)
                break
                
        #autopilot
        if cheat_mode and autopilot_cd == 0:
            cur = player_lane_idx
            danger = False
            for c in traffic:     #check cars and barriers for danger
                if c['lane'] == cur and -800 < c['z'] < 50: danger = True; break
            for b in barriers:
                if b['lane'] == cur and -800 < b['z'] < 50: danger = True; break
                
            if danger:
                left = cur > 0
                if left:
                    for c in traffic: 
                        if c['lane'] == cur-1 and -800 < c['z'] < 50: left = False
                    for b in barriers:
                        if b['lane'] == cur-1 and -800 < b['z'] < 50: left = False
                right = cur < 3
                if right:
                    for c in traffic:
                        if c['lane'] == cur+1 and -800 < c['z'] < 50: right = False
                    for b in barriers:
                        if b['lane'] == cur+1 and -800 < b['z'] < 50: right = False
                        
                if left:
                    player_lane_idx -= 1
                    player_x = LANE_COORDINATES[player_lane_idx]
                    autopilot_cd = 15
                elif right:
                    player_lane_idx += 1
                    player_x = LANE_COORDINATES[player_lane_idx]
                    autopilot_cd = 15
        if autopilot_cd > 0: autopilot_cd -= 1

    glutPostRedisplay()

def keyboardListener(key, x, y):
    global paused, nitro_active, cheat_mode, camera_mode, lights_on
    k = key.decode("utf-8").lower()
    if k=='q': glutLeaveMainLoop()
    if k=='r': init()
    if k=='p': paused = not paused
    if k==' ': 
        if not nitro_refilling: nitro_active = True
    if k=='c': cheat_mode = not cheat_mode
    if k=='v': camera_mode = 1 if camera_mode==2 else 2
    if k=='l': lights_on = not lights_on

def keyboardUpListener(key, x, y):
    global nitro_active
    if key.decode("utf-8") == ' ': nitro_active = False

def specialKeyListener(key, x, y):
    global player_lane_idx, player_x
    if paused or game_over or cheat_mode: return
    if key==GLUT_KEY_LEFT and player_lane_idx > 0:
        player_lane_idx -= 1
        player_x = LANE_COORDINATES[player_lane_idx]
    if key==GLUT_KEY_RIGHT and player_lane_idx < 3:
        player_lane_idx += 1
        player_x = LANE_COORDINATES[player_lane_idx]

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(WINDOW_TITLE)
    init()

    glEnable(GL_DEPTH_TEST); glEnable(GL_NORMALIZE)  #depth test
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutKeyboardUpFunc(keyboardUpListener)
    glutSpecialFunc(specialKeyListener)
    glutIdleFunc(animate)
    glutMainLoop()

if __name__ == "__main__":
    main()