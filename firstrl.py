import libtcodpy as libtcod
#   These variables shouldnt be changed and represent the settings
#   for the console window which will appear

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

def handle_keys():
    #   here we set the globals for the players position plus handle movement

    global playerx, playery

    key = libtcod.console_wait_for_keypress(True)
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #alt enter for fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_ESCAPE:
        return True #exit game

    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        playery -= 1

    if libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        playery += 1

    if libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        playerx -= 1

    if libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        playerx += 1


#   INT stuff here which dictates the console window.

libtcod.console_set_custom_font('arial10x10.png',libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'python/libtcod tutorial',False)

libtcod.sys_set_fps(LIMIT_FPS)


playerx = SCREEN_HEIGHT/2
playery = SCREEN_WIDTH/2

#   THIS is the main loop for the game.

while not libtcod.console_is_window_closed():

    libtcod.console_set_default_foreground(0, libtcod.white)

    libtcod.console_put_char(0, playerx, playery, '@', libtcod.BKGND_NONE)

    libtcod.console_flush()

    libtcod.console_put_char(0, playerx, playery, ' ', libtcod.BKGND_NONE)

    exit = handle_keys()

    if exit :
        break
