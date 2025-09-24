import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
BOARD_SIZE = 10
CELL_SIZE = 40
BOARD_OFFSET_X = 50
BOARD_OFFSET_Y = 100
ATTACK_BOARD_OFFSET_X = 650

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
DARK_BLUE = (0, 0, 139)
YELLOW = (255, 255, 0)

# Ship definitions
ships = {
    "Destroyer": 2,
    "Submarine": 3,
    "Cruiser": 3,
    "Battleship": 4,
    "Carrier": 5
}

class BattleshipPygame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Battleship Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        
        # Game state
        self.game_state = "SETUP"  # SETUP, PLAYING, GAME_OVER
        self.current_ship = 0
        self.ship_names = list(ships.keys())
        self.ship_direction = "H"  # H or V
        self.selected_cell = None
        
        # Boards: 0=empty, 1=ship, 2=hit, 3=miss
        self.player_board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.computer_board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.player_attack_board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        # Ship positions
        self.player_ships = {}
        self.computer_ships = {}
        
        # Turn management
        self.player_turn = True
        self.message = "Place your ships! Click to place, R to rotate"
        
        self.place_computer_ships()
    
    def place_computer_ships(self):
        """Randomly place computer ships"""
        for ship_name, length in ships.items():
            placed = False
            while not placed:
                direction = random.choice(["H", "V"])
                row = random.randint(0, BOARD_SIZE - 1)
                col = random.randint(0, BOARD_SIZE - 1)
                
                if self.is_valid_placement(self.computer_board, row, col, length, direction):
                    self.place_ship(self.computer_board, self.computer_ships, ship_name, row, col, length, direction)
                    placed = True
    
    def is_valid_placement(self, board, row, col, length, direction):
        """Check if ship placement is valid"""
        if direction == "H":
            if col + length > BOARD_SIZE:
                return False
            for i in range(length):
                if board[row][col + i] != 0:
                    return False
        else:  # Vertical
            if row + length > BOARD_SIZE:
                return False
            for i in range(length):
                if board[row + i][col] != 0:
                    return False
        return True
    
    def place_ship(self, board, ship_dict, ship_name, row, col, length, direction):
        """Place a ship on the board"""
        positions = []
        if direction == "H":
            for i in range(length):
                board[row][col + i] = 1
                positions.append((row, col + i))
        else:  # Vertical
            for i in range(length):
                board[row + i][col] = 1
                positions.append((row + i, col))
        ship_dict[ship_name] = positions
    
    def get_cell_from_mouse(self, mouse_pos, board_offset_x):
        """Convert mouse position to board cell coordinates"""
        x, y = mouse_pos
        if (board_offset_x <= x <= board_offset_x + BOARD_SIZE * CELL_SIZE and
            BOARD_OFFSET_Y <= y <= BOARD_OFFSET_Y + BOARD_SIZE * CELL_SIZE):
            col = (x - board_offset_x) // CELL_SIZE
            row = (y - BOARD_OFFSET_Y) // CELL_SIZE
            return row, col
        return None
    
    def attack(self, row, col):
        """Attack a cell on computer's board"""
        if self.computer_board[row][col] == 1:  # Hit
            # Find and sink entire ship
            for ship_name, positions in self.computer_ships.items():
                if (row, col) in positions:
                    # Mark all positions of this ship as hit
                    for ship_row, ship_col in positions:
                        self.computer_board[ship_row][ship_col] = 2
                        self.player_attack_board[ship_row][ship_col] = 2
                    self.message = f"HIT AND SUNK! You destroyed the {ship_name}!"
                    return True
        else:  # Miss
            self.computer_board[row][col] = 3
            self.player_attack_board[row][col] = 3
            self.message = "Miss!"
            return False
    
    def computer_attack(self):
        """Computer makes a random attack"""
        while True:
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 1)
            
            if self.player_board[row][col] in [0, 1]:  # Not already attacked
                if self.player_board[row][col] == 1:  # Hit
                    # Find and sink entire ship
                    for ship_name, positions in self.player_ships.items():
                        if (row, col) in positions:
                            # Mark all positions of this ship as hit
                            for ship_row, ship_col in positions:
                                self.player_board[ship_row][ship_col] = 2
                            self.message = f"Computer HIT AND SUNK your {ship_name}!"
                            return True
                else:  # Miss
                    self.player_board[row][col] = 3
                    self.message = f"Computer missed at {chr(65+row)}{col+1}"
                    return False
    
    def check_game_over(self):
        """Check if all ships of either player are sunk"""
        player_ships_alive = any(1 in row for row in self.player_board)
        computer_ships_alive = any(1 in row for row in self.computer_board)
        
        if not computer_ships_alive:
            self.game_state = "GAME_OVER"
            self.message = "🎉 YOU WON! All enemy ships destroyed! 🎉"
            return True
        elif not player_ships_alive:
            self.game_state = "GAME_OVER"
            self.message = "💥 GAME OVER! All your ships destroyed! 💥"
            return True
        return False
    
    def draw_board(self, board, offset_x, offset_y, show_ships=True, attack_board=False):
        """Draw a game board"""
        # Draw grid
        for row in range(BOARD_SIZE + 1):
            y = offset_y + row * CELL_SIZE
            pygame.draw.line(self.screen, BLACK, (offset_x, y), (offset_x + BOARD_SIZE * CELL_SIZE, y))
        
        for col in range(BOARD_SIZE + 1):
            x = offset_x + col * CELL_SIZE
            pygame.draw.line(self.screen, BLACK, (x, offset_y), (x, offset_y + BOARD_SIZE * CELL_SIZE))
        
        # Draw cells
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x = offset_x + col * CELL_SIZE
                y = offset_y + row * CELL_SIZE
                cell_rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
                
                if attack_board:
                    if board[row][col] == 0:
                        pygame.draw.rect(self.screen, LIGHT_BLUE, cell_rect)
                    elif board[row][col] == 2:
                        pygame.draw.rect(self.screen, RED, cell_rect)  # Hit
                        self.draw_x(x, y)
                    elif board[row][col] == 3:
                        pygame.draw.rect(self.screen, WHITE, cell_rect)  # Miss
                        pygame.draw.circle(self.screen, BLUE, (x + CELL_SIZE//2, y + CELL_SIZE//2), 8)
                else:
                    if board[row][col] == 0:
                        pygame.draw.rect(self.screen, LIGHT_BLUE, cell_rect)
                    elif board[row][col] == 1:
                        if show_ships:
                            pygame.draw.rect(self.screen, GRAY, cell_rect)  # Ship
                        else:
                            pygame.draw.rect(self.screen, LIGHT_BLUE, cell_rect)
                    elif board[row][col] == 2:
                        pygame.draw.rect(self.screen, RED, cell_rect)  # Hit
                        self.draw_x(x, y)
                    elif board[row][col] == 3:
                        pygame.draw.rect(self.screen, WHITE, cell_rect)  # Miss
                        pygame.draw.circle(self.screen, BLUE, (x + CELL_SIZE//2, y + CELL_SIZE//2), 8)
        
        # Draw coordinates
        for i in range(BOARD_SIZE):
            # Row labels (A-J)
            text = self.font.render(chr(65 + i), True, BLACK)
            self.screen.blit(text, (offset_x - 25, offset_y + i * CELL_SIZE + 12))
            # Column labels (1-10)
            text = self.font.render(str(i + 1), True, BLACK)
            self.screen.blit(text, (offset_x + i * CELL_SIZE + 15, offset_y - 25))
    
    def draw_x(self, x, y):
        """Draw an X for hits"""
        pygame.draw.line(self.screen, BLACK, (x + 5, y + 5), (x + CELL_SIZE - 5, y + CELL_SIZE - 5), 3)
        pygame.draw.line(self.screen, BLACK, (x + CELL_SIZE - 5, y + 5), (x + 5, y + CELL_SIZE - 5), 3)
    
    def preview_ship_placement(self, row, col):
        """Preview where ship would be placed"""
        if self.current_ship < len(self.ship_names):
            ship_name = self.ship_names[self.current_ship]
            length = ships[ship_name]
            
            # Check if placement would be within bounds first
            if self.ship_direction == "H":
                if col + length > BOARD_SIZE or row < 0 or row >= BOARD_SIZE:
                    return
            else:  # Vertical
                if row + length > BOARD_SIZE or col < 0 or col >= BOARD_SIZE:
                    return
            
            if self.is_valid_placement(self.player_board, row, col, length, self.ship_direction):
                for i in range(length):
                    if self.ship_direction == "H":
                        preview_row, preview_col = row, col + i
                    else:
                        preview_row, preview_col = row + i, col
                    
                    x = BOARD_OFFSET_X + preview_col * CELL_SIZE
                    y = BOARD_OFFSET_Y + preview_row * CELL_SIZE
                    preview_rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)
                    pygame.draw.rect(self.screen, YELLOW, preview_rect)
    
    def handle_setup_click(self, mouse_pos):
        """Handle mouse clicks during ship setup"""
        cell = self.get_cell_from_mouse(mouse_pos, BOARD_OFFSET_X)
        if cell and self.current_ship < len(self.ship_names):
            row, col = cell
            ship_name = self.ship_names[self.current_ship]
            length = ships[ship_name]
            
            if self.is_valid_placement(self.player_board, row, col, length, self.ship_direction):
                self.place_ship(self.player_board, self.player_ships, ship_name, row, col, length, self.ship_direction)
                self.current_ship += 1
                
                if self.current_ship >= len(self.ship_names):
                    self.game_state = "PLAYING"
                    self.message = "All ships placed! Click on attack board to attack!"
                else:
                    next_ship = self.ship_names[self.current_ship]
                    self.message = f"Place your {next_ship} (length {ships[next_ship]}). R to rotate"
    
    def handle_attack_click(self, mouse_pos):
        """Handle mouse clicks during attack phase"""
        cell = self.get_cell_from_mouse(mouse_pos, ATTACK_BOARD_OFFSET_X)
        if cell and self.player_turn:
            row, col = cell
            if self.player_attack_board[row][col] == 0:  # Not already attacked
                self.attack(row, col)
                
                if not self.check_game_over():
                    self.player_turn = False
                    pygame.time.set_timer(pygame.USEREVENT + 1, 1500)  # Computer attack delay
    
    def run(self):
        """Main game loop"""
        running = True
        mouse_pos = (0, 0)
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = event.pos
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == "SETUP":
                        self.handle_setup_click(event.pos)
                    elif self.game_state == "PLAYING":
                        self.handle_attack_click(event.pos)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and self.game_state == "SETUP":
                        # Rotate ship
                        self.ship_direction = "V" if self.ship_direction == "H" else "H"
                    elif event.key == pygame.K_SPACE and self.game_state == "GAME_OVER":
                        # Restart game
                        self.__init__()
                
                elif event.type == pygame.USEREVENT + 1:
                    # Computer attack
                    if not self.player_turn and self.game_state == "PLAYING":
                        self.computer_attack()
                        if not self.check_game_over():
                            self.player_turn = True
                        pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Cancel timer
            
            # Clear screen
            self.screen.fill(WHITE)
            
            # Draw title
            title = self.big_font.render("BATTLESHIP", True, BLACK)
            self.screen.blit(title, (WINDOW_WIDTH // 2 - 80, 20))
            
            # Draw boards
            if self.game_state == "SETUP":
                # Only show player board during setup
                board_title = self.font.render("Your Ships", True, BLACK)
                self.screen.blit(board_title, (BOARD_OFFSET_X, BOARD_OFFSET_Y - 50))
                self.draw_board(self.player_board, BOARD_OFFSET_X, BOARD_OFFSET_Y)
                
                # Preview ship placement
                if self.current_ship < len(self.ship_names):
                    cell = self.get_cell_from_mouse(mouse_pos, BOARD_OFFSET_X)
                    if cell:
                        self.preview_ship_placement(cell[0], cell[1])
                
            else:
                # Show both boards during play
                board_title1 = self.font.render("Your Ships", True, BLACK)
                self.screen.blit(board_title1, (BOARD_OFFSET_X, BOARD_OFFSET_Y - 50))
                self.draw_board(self.player_board, BOARD_OFFSET_X, BOARD_OFFSET_Y)
                
                board_title2 = self.font.render("Attack Board", True, BLACK)
                self.screen.blit(board_title2, (ATTACK_BOARD_OFFSET_X, BOARD_OFFSET_Y - 50))
                self.draw_board(self.player_attack_board, ATTACK_BOARD_OFFSET_X, BOARD_OFFSET_Y, attack_board=True)
            
            # Draw message
            message_text = self.font.render(self.message, True, BLACK)
            self.screen.blit(message_text, (50, 600))
            
            # Draw instructions
            if self.game_state == "SETUP":
                if self.current_ship < len(self.ship_names):
                    ship_name = self.ship_names[self.current_ship]
                    instructions = f"Placing: {ship_name} (Length: {ships[ship_name]}) | Direction: {self.ship_direction} | Press R to rotate"
                    inst_text = self.font.render(instructions, True, DARK_BLUE)
                    self.screen.blit(inst_text, (50, 630))
            elif self.game_state == "PLAYING":
                turn_text = "Your turn - Click on attack board" if self.player_turn else "Computer's turn..."
                inst_text = self.font.render(turn_text, True, DARK_BLUE)
                self.screen.blit(inst_text, (50, 630))
            elif self.game_state == "GAME_OVER":
                restart_text = self.font.render("Press SPACE to play again", True, GREEN)
                self.screen.blit(restart_text, (50, 650))
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = BattleshipPygame()
    game.run()