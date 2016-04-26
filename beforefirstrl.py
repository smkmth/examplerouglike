import libtcodpy as libtcod
#   These variables shouldnt be changed and represent the settings
#   for the console window which will appear

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

MAP_WIDTH = 80
MAP_HEIGHT = 45

ROOM_MAX_SIZE =  10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
MAX_ROOM_MONSTERS = 10
FOV_ALGO = 0 #what algorythom to use
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
    def __init__(self, x, y, char, name, color, blocks = False):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks

    def move(self, dx, dy):
        # move by a given amount
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy

    def draw(self):
        if libtcod.map_is_in_fov(fov_map, self.x, self.y,):
        # set the color and draw the object at the position
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con,self.x,self.y,self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erase the character for this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

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
                #create orc
                monster = Object(x, y, 'o', 'orc', libtcod.desaturated_green,
                                 blocks=True)
        else:
            #create troll
            monster = Object(x, y, 'T', 'troll', libtcod.darker_green,
                             blocks=True)

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
        if object.x == x and object.y == y:
            target = object
            break

    if target is not None:
        print 'The' + target.name + 'laughs at your punny attempts to attack him!'
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
            player.move(0, -1)
            fov_recompute = True

        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            player.move(0, 1)
            fov_recompute = True
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            player.move(-1, 0)
            fov_recompute = True
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            player.move(1, 0)
            fov_recompute = True
        else:
            return 'didnt-take-turn'

#   INT stuff here which dictates the console window.

libtcod.console_set_custom_font('arial10x10.png',libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial',False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

player = Object(0, 0, '@', 'player', libtcod.white, blocks= True)

objects = [player]

make_map()

fov_map = libtcod.map_new(MAP_WIDTH,MAP_HEIGHT)
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
            if object != player:
                print 'The' + object.name + 'growls!'
