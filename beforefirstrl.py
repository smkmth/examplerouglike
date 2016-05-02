import math

import libtcodpy as libtcod
#   These variables shouldnt be changed and represent the settings
#   for the console window which will appear

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

MAP_WIDTH = 80
MAP_HEIGHT = 45

ROOM_MAX_SIZE =  6
ROOM_MIN_SIZE = 4
MAX_ROOMS = 50
MAX_ROOM_MONSTERS = 10
FOV_ALGO = 2 #what algorythom to use
FOV_LIGHT_WALLS = True #should we light walls
TORCH_RADIUS = 10

LIMIT_FPS = 20

color_dark_wall = libtcod.Color(0, 0, 0)
color_light_wall = libtcod.Color(94, 75, 47)
color_dark_ground = libtcod.Color(31, 31, 31)
color_light_ground = libtcod.Color(158, 134, 100)

class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        #tiles start off unexplored
        self.explored = False


        #by defult if a tile is blocked it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return center_x, center_y

    def intersect(self,other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Object:
    #   this is a generic object: the player, a monster on the screen, an item,
    #   stairs, its always represented by a character on screen.
    #    this is an example of composition - these components are stored by classes,
    #   and then passed as parameters when creating the object. The advntange of
    #   this methodology over inherretence is that you can choose to not inherret properties
    #   on initialization
    def __init__(self, x, y, char, name, color, blocks = False, fighter = None, ai = None):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.fighter = fighter
        #so in the fighter class is a variable called owner- which is set to whoever calls
        # that object so we can say 'owner.name even though we dont know what specific instance
        # the method will call/
        if self.fighter :
            self.fighter.owner = self

        self.ai = ai
        if self.ai :
            self.ai.owner = self


    def move(self, dx, dy):
        # move by a given amount
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def move_towards(self,target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #normalize it to length l (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.x - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def send_to_back(self):
        global objects
        objects.remove(self)
        objects.insert(0,self)


    def draw(self):
        if libtcod.map_is_in_fov(fov_map, self.x, self.y,):
        # set the color and draw the object at the position
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con,self.x,self.y,self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erase the character for this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

class Fighter:
    def __init__(self, hp, defense, power, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.death_function = death_function

    def attack(self, target):
        damage = self.power - target.fighter.defense

        if damage > 0:
            print self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hitpoints. '
            target.fighter.take_damage(damage)
        else:
            print self.owner.name.capitalize() + ' attacks ' + target.name +  'but it had no effect!'

    def take_damage(self,damage):
        if damage > 0:
            self.hp -= damage

            if self.hp <= 0 :
                function = self.death_function
                if function is not None:
                    function(self.owner)

class BasicMonster :
    def take_turn(self):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)

            elif player.fighter.hp > 0:
                print "the attack of the" + monster.name + " bounces off your shiny metal armor"




def is_blocked(x, y):
    #first test the map tile
    if map[x][y].blocked:
        return True
    #now check for blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True
    return False

def create_room(room):
    global map
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 +1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False


def create_h_tunnel(x1, x2, y):
    global map
    for x in range(min(x1, x2), max(x1, x2)+ 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False

def create_v_tunnel(y1, y2, x):
    global map
    for y in range(min(y1, y2), max(y1, y2)+ 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False


def make_map():
    global map, player

    #fill map with unblocked tiles
    #this function works by storing the results of a for loop in
    #two seporate lists. The for loop uses the map hieght as an
    #iterator, which is the size of pixles the console is.
    #because the results are stored in a list, we can refer
    #to any individual tile, map[3][3] or all the tiles map[x][y]

    map = [[ Tile(True)
        for y in range(MAP_HEIGHT)]
           for x in range(MAP_WIDTH)]
    #the rooms generated are saved in a list called rooms.
    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        #random widths and heights
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random postion within the  map
        x = libtcod.random_get_int(0,0,MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0,0, MAP_HEIGHT - h - 1)

        new_room = Rect(x, y, w, h)

        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed =True
                break
        if not failed:
            #this means their is no intersections so the room  is valid

            #'paint it' to the new maps tiles
            create_room(new_room)
            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()

#            uncomment to show the order the rooms are created in letters - not numbers
#            room_no = Object(new_x, new_y, chr(65+num_rooms), libtcod.white)
#            objects.insert(0, room_no)

            if num_rooms == 0:
                #this is the first room where the player starts
                player.x = new_x
                player.y = new_y
            else:
                #all rooms after the first
                #conect it to the previous room with a tunnel

                #center coodinates of previous room
                (prev_x, prev_y) =rooms[num_rooms-1].center()

                if libtcod.random_get_int(0, 0, 1) == 1:
                    #first move horizontally then vertiacally
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first move vertically then horzontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            #fill room with stuff and monsters
            place_objects(new_room)
            #finally append new room to list
            rooms.append(new_room)
            num_rooms += 1

def place_objects(room):
    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0,0, MAX_ROOM_MONSTERS)

    for i in range(num_monsters):
        x = libtcod.random_get_int(0, room.x1, room.x2)
        y = libtcod.random_get_int(0, room.y1, room.y2)
        if is_blocked(x, y):
            if libtcod.random_get_int(0, 0, 100) > 80:
                fighter_component= Fighter(hp=10, defense=0, power=3, death_function=monster_death)
                ai_component = BasicMonster()

                monster = Object(x,y, 'o', 'orc' , libtcod.desaturated_green,
                                 blocks=True, fighter= fighter_component, ai=ai_component)

        else:
            #create troll
            fighter_component= Fighter(hp= 16, defense=1, power=4, death_function=monster_death)
            ai_component=BasicMonster()

            monster = Object(x, y, 'T', 'troll', libtcod.darker_green,
                             blocks=True, fighter=fighter_component, ai=ai_component)

            objects.append(monster)



def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute
    #go through all the tiles and set their background color

    if fov_recompute:
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            visible = libtcod.map_is_in_fov(fov_map, x, y)
            wall = map[x][y].block_sight
            if not visible: #its waiting to be explored
                if map[x][y].explored:
                    if wall:
                        libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con,x,y,color_dark_ground,libtcod.BKGND_SET)
            else: #its visiable
                if wall:
                    libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET)
                else:
                    libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET)
                map[x][y].explored = True
    #draw all objects in the list
    for object in objects:
        object.draw()

    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)



def player_move_or_attack(dx, dy):
    global fov_recompute

    x = player.x + dx
    y = player.y + dy

    target = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break

    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True


def handle_keys():
    global fov_recompute
    #   here we set the globals for the players position plus handle movement

    #use check for keypress for realtime
    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #alt enter for fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit' #exit game
    if game_state == 'playing':

        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            player_move_or_attack(0, -1)
            fov_recompute = True

        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            player_move_or_attack(0, 1)
            fov_recompute = True
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            player_move_or_attack(-1, 0)
            fov_recompute = True
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            player_move_or_attack(1, 0)
            fov_recompute = True
        else:
            return 'didnt-take-turn'

def player_death(player):
    global game_state
    print "your dead"
    game_state = 'dead'
    player.char = '%'
    player.colour = libtcod.dark_red

def monster_death(monster):
    print monster.name.capitalize() + "is dead"
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()

#   INT stuff here which dictates the console window.

libtcod.console_set_custom_font('arial10x10.png',libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial',False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

fighter_component = Fighter(hp = 30, defense=2, power=5, death_function=player_death)
player = Object(0, 0, '@', 'player', libtcod.white, blocks= True, fighter=fighter_component)


objects = [player]

make_map()

fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH) :
        libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)

fov_recompute = True
game_state = 'playing'
player_action = None

#   THIS is the main loop for the game.


while not libtcod.console_is_window_closed():

    render_all()

    libtcod.console_flush()


    for object in objects:
        object.clear()


    exit = handle_keys()
    if player_action == 'exit':
        break

    if game_state == 'playing' and player_action != 'didnt-take-turn':
        for object in objects:
            if object.ai:
                object.ai.take_turn()
