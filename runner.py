

import pygame
import sys
import logic

pygame.init()

MAX_HEIGHT = 700
MAX_WIDTH = 800

BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,255)
RED = (255,0,0)
YELLOW = (255,255,0)

FONT = pygame.font.SysFont("Times New Roman", 36)

game = logic.Connect4()
AI_PLAYER = logic.AI()
AI_PLAYER.populate()

TOTAL_CELLS = game.cells

CLICKABLE_AREA_WIDTH = 150

CELL_RADIUS = (MAX_HEIGHT-CLICKABLE_AREA_WIDTH) // game.rows // 2 

SCREEN = pygame.display.set_mode((MAX_WIDTH,MAX_HEIGHT))
pygame.display.set_caption("Connect Four")

MENU_BUTTON_X,MENU_BUTTON_Y = 200,65
BUTTON_GAP = 30

def main() :

    in_game = False

    while True :

        SCREEN.fill(BLACK)
        
        if not in_game :
            display_menu()
        else :
            display_game()

        for event in pygame.event.get() :
            if event.type == pygame.QUIT :
                sys.exit(1)
            
            if event.type == pygame.MOUSEBUTTONDOWN  :
                if not in_game :
                    in_game = handle_menu_click(event.pos)
                else :
                    in_game = handle_game_click(event.pos)

        pygame.display.flip()
    

def display_menu() :
    center_x,center_y = perfect_center(MENU_BUTTON_X,MENU_BUTTON_Y)
    texts = ["Play AI","Play Locally", "Play Online", "Exit"]
    rectangles = pygame.draw.rect(SCREEN,WHITE,(center_x,center_y,MENU_BUTTON_X,MENU_BUTTON_Y))

    for i,text in enumerate(texts) :
        text_display = FONT.render(text,True,BLACK)
        SCREEN.blit(text_display,(rectangles.bottomleft[0]+MENU_BUTTON_X//(4.25*(i+1)),rectangles.bottomleft[1]-MENU_BUTTON_Y/((i+1)*1.25)))
        if i <= len(texts) - 2 :
            rectangles = pygame.draw.rect(SCREEN,WHITE,(rectangles.bottomleft[0]+10,rectangles.bottomleft[1]+BUTTON_GAP,MENU_BUTTON_X-(20*(i+1)),MENU_BUTTON_Y))

def handle_menu_click(mouse_pos) :
    x,y = mouse_pos
    return perfect_center(200,70,True,False)<x<perfect_center(200,70,True,False)+200 and perfect_center(200,70,False,True)<y<perfect_center(200,70,False,True)+70

def handle_game_click(mouse_pos) :

    if game.get_player() == 2 :
        action = AI_PLAYER.next_move(game)
        game.move(action)
        return handle_win()
    
    x,y = mouse_pos
    col_size = MAX_WIDTH // game.cols
    for k in range(game.cols) :
        if col_size*k<x<col_size*(k+1) :
            if not game.col_availability(k) :
                print("Column is full")
            else :
                row = game.available_row(k)
                action = (row,k)
                game.move(action) 

    return handle_win()

def display_game() :
    display_board()
    display_hover()

def display_board() :

    board_surface = pygame.Surface((MAX_WIDTH,MAX_HEIGHT-CLICKABLE_AREA_WIDTH))
    board_surface.fill(BLUE)

    space_y = 2
    for i,y in enumerate(range(0,MAX_HEIGHT-CLICKABLE_AREA_WIDTH-CELL_RADIUS,CELL_RADIUS*2)) :
        space_x = 8
        for j,x in enumerate(range(0,MAX_WIDTH-CELL_RADIUS,CELL_RADIUS*2+20)) :
            color = RED if game.board[i][j] == 1 else YELLOW if game.board[i][j] == 2 else BLACK
            pygame.draw.circle(board_surface,color,(x+CELL_RADIUS+space_x,y+CELL_RADIUS+space_y),CELL_RADIUS-1)
            space_x+=3
        space_y+=2

    SCREEN.blit(board_surface,(0,MAX_HEIGHT-board_surface.get_height()))

def display_hover() :    
    color = RED if game.get_player() == 1 else YELLOW
    x,y= pygame.mouse.get_pos()
    pygame.draw.circle(SCREEN,color,(x,75),CELL_RADIUS-1)

def handle_win() :

    game_state = game.terminal_state()
    
    if game_state != 0 :
        if game_state == 1 :
            print("Red Won")
        elif game_state == 2 :
            print("Yellow Won")
        elif game_state  == -1 :
            print("Draw")

        game.reset()
        return False
    
    return True

def perfect_center(width,height,x=True,y=True) :

    center_width = (MAX_WIDTH -width)//2
    center_height = (MAX_HEIGHT - height)//2

    if x and y :
        return center_width,center_height
    elif x :
        return center_width
    elif y :
        return center_height
    
    
if __name__ == "__main__" :
    main()