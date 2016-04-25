import libtcodpy as libtcod
#   These variables shouldnt be changed and represent the settings
#   for the console window which will appear

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

MAP_WIDTH = 80
MAP_HEIGHT = 45

LIMIT_FPS = 20

color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)

class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        #by defult if a tile is blocked it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight


class Object:
    #   this is a generic object: the player, a monster on the screen, an item,
    #   stairs, its always represented by a character on screen.
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx, dy):
        # move by a given amount
        if not map[self.x + dx][self.y +dy].blocked :
            self.x += dx
            self.y += dy

    def draw(self):

#       set the color and draw the object at the position
        libtcod.console_set_default_foreground(con,self.color)
        libtcod.console_put_char(con,self.x,self.y,self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erase the character for this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

def make_map():
    global map

    #fill map with unblocked tiles
    map = [[ Tile(False)
             for y in range(MAP_HEIGHT)]
           for x in range(MAP_WIDTH)]
    #Place two pillars to test the map
    map[30][22].blocked = True
    map[30][22].block_sight = True
    map[50][22].blocked = True
    map[50][22].block_sight = True

def render_all():
    global color_light_wall
    global color_light_ground
    #go through all the tiles and set their background color

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = map[x][y].block_sight
            if wall:
                libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
            else:
                libtcod.console_set_char_background(con,x,y,color_dark_ground,libtcod.BKGND_SET)

    #draw all objects in the list
    for object in objects:
        object.draw()

    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)



def handle_keys():
    #   here we set the globals for the players position plus handle movement

    #use check for keypress for realtime
    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #alt enter for fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return True #exit game

    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        player.move(0, -1)

    if libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        player.move(0, 1)

    if libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        player.move(-1, 0)

    if libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        player.move(1, 0)


#   INT stuff here which dictates the console window.

libtcod.console_set_custom_font('arial10x10.png',libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial',False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)

player = Object(SCREEN_WIDTH/2,SCREEN_HEIGHT/2, '@', libtcod.white)
npc = Object(SCREEN_WIDTH/2-6,SCREEN_HEIGHT/2-4, '@', libtcod.yellow)
objects= [npc, player]

make_map()

#   THIS is the main loop for the game.

while not libtcod.console_is_window_closed():

    render_all()

    libtcod.console_flush()


    for object in objects:
        object.clear()


    exit = handle_keys()

    if exit :
        break
