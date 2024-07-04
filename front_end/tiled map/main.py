import pygame
import pytmx
from person import *

# initialize pygame and create window
pygame.init()
clock = pygame.time.Clock() 

FPS = 1

scale_factor = 3
tile_width = 16 * scale_factor
tile_height =  16 * scale_factor
rows = 20
cols = 20
screen_width = tile_width * rows
screen_height = tile_height * cols

screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Village Map')

# set up fonts
font = pygame.font.SysFont(None, tile_height // 2 )
# set up screen_info
screen_info = {
    'screen': screen,
    'font': font,
    'tile_width': tile_width,
    'tile_height': tile_height,
    'scale_factor': scale_factor
}

# set up colors
black = (0, 0, 0)
white = (255, 255, 255)

# load images
bg_img = pygame.image.load('map.png').convert_alpha()
sc_bg_img = pygame.transform.scale(bg_img, (screen_width,screen_height))
tiled_map = pytmx.load_pygame('map.tmx')

# load agents
agents = []
for obj in tiled_map.get_layer_by_name("agents"):
        agent_image = tiled_map.get_tile_image_by_gid(obj.gid)
        sc_agent_img = pygame.transform.scale(agent_image, (tile_width, tile_height))
        if agent_image:
            agents.append(Person(obj.x * scale_factor, obj.y * scale_factor, sc_agent_img, tile_height))

# function for bg
def draw_bg():
	screen.blit(sc_bg_img, (0,0))

# function for text
def draw_txt(agent, text):
    agent_x = agent.rect.x
    agent_y = agent.rect.y

    # write text
    text_surface = font.render(text, True, black)
    
    # get text size
    text_width, text_height = font.size(text)

    # calculate text box position
    padding = 2.5 * scale_factor
    text_box_rect = pygame.Rect(agent_x + tile_width//2 - text_width//2 - padding, agent_y - text_height - padding * 2, text_width + padding * 2, text_height + padding * 2)

    # draw text box
    pygame.draw.rect(screen, white, text_box_rect)
    pygame.draw.rect(screen, black, text_box_rect, 2)

    screen.blit(text_surface, (agent_x + tile_width//2 - text_width//2 , agent_y - text_height - padding))

# function for movement
def draw_movement(agent, command, text):
    draw_bg()
    agent.move(screen, command, tile_width, tile_height)
    draw_txt(agent, text)
    pygame.display.update()

# commands
commands = []
for i in range(5):
     commands.append(['DOWN','Walk down']) 
command_index = 0

# æ¸¸æä¸»å¾ªç¯
running = True

while running:

    clock.tick(FPS)

    draw_bg()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if command_index < len(commands):
        command, text = commands[command_index]
        draw_movement(agents[0], command, text)
        command_index += 1  # ç§»å¨å°ä¸ä¸ä¸ªå½ä»¤
    
pygame.quit()

# æ¸²æå°å¾
    # for layer in tiled_map.visible_layers:
    #     if isinstance(layer, pytmx.TiledTileLayer):
    #     # å¤çå¾åå±
    #         for x, y, gid in layer:
    #             tile = tiled_map.get_tile_image_by_gid(gid)
    #             if tile:
    #                 tile = pygame.transform.scale(tile, (tiled_map.tilewidth * scale_factor, tiled_map.tileheight * scale_factor))
    #                 screen.blit(tile, (x * tiled_map.tilewidth * scale_factor, y * tiled_map.tileheight * scale_factor))
        # elif isinstance(layer, pytmx.TiledObjectGroup):
        #     # å¤çå¯¹è±¡å±
        #     for obj in layer:
        #         if obj.gid:  # æ£æ¥å¯¹è±¡æ¯å¦æå³èçå¾åï¼éè¿gidï¼
        #             image = tiled_map.get_tile_image_by_gid(obj.gid)
        #             if image:
        #                 image = pygame.transform.scale(image, (int(obj.width * scale_factor), int(obj.height * scale_factor)))
        #                 screen.blit(image, (obj.x * scale_factor, obj.y * scale_factor))
