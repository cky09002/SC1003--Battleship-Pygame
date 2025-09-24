import random

# Battleship Game
print("Welcome to Battleship!")

# Game constants
BOARD_SIZE = 10
row_labels = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
row_to_num = {label: i for i, label in enumerate(row_labels)}

# Ship definitions
ships = {
    "Destroyer": 2,
    "Submarine": 3,
    "Cruiser": 3,
    "Battleship": 4,
    "Carrier": 5
}

class BattleshipGame:
    def __init__(self):
        # 0 = empty water, 1 = ship, 2 = hit, 3 = miss
        self.player_board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.computer_board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.player_attack_board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.computer_attack_board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        
        self.player_ships = {}
        self.computer_ships = {}
        
    def print_board(self, board, show_ships=True, attack_board=False):
        print("  ", end="")
        for i in range(1, BOARD_SIZE + 1): # from 1 to 10
            print(f"{i:2}", end="") # 
        print()
        
        for i, row_label in enumerate(row_labels):
            print(f"{row_label} ", end="") # print
            for j in range(BOARD_SIZE):
                if attack_board:
                    if board[i][j] == 0:
                        print(" .", end="")
                    elif board[i][j] == 2:
                        print(" X", end="")  # Hit
                    elif board[i][j] == 3:
                        print(" O", end="")  # Miss
                else:
                    if board[i][j] == 0:
                        print(" .", end="")
                    elif board[i][j] == 1:
                        print(" S", end="") if show_ships else print(" .", end="")
                    elif board[i][j] == 2:
                        print(" X", end="")  # Hit
                    elif board[i][j] == 3:
                        print(" O", end="")  # Miss
            print()
        print()
    
    def is_valid_placement(self, board, row, col, length, direction):
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
    
    def place_player_ships(self):
        print("Place your ships!")
        self.print_board(self.player_board)
        
        for ship_name, length in ships.items():
            placed = False
            while not placed:
                try:
                    print(f"\nPlacing {ship_name} (length {length})")
                    direction = input("Direction (H for horizontal, V for vertical): ").upper()
                    if direction not in ["H", "V"]:
                        print("Please enter H or V")
                        continue
                    
                    coord_input = input("Enter starting coordinate (e.g., A1): ").upper()
                    if len(coord_input) < 2:
                        print("Invalid coordinate format")
                        continue
                    
                    row_letter = coord_input[0]
                    col_num = int(coord_input[1:]) - 1
                    
                    if row_letter not in row_to_num or col_num < 0 or col_num >= BOARD_SIZE:
                        print("Invalid coordinate")
                        continue
                    
                    row = row_to_num[row_letter]
                    
                    if self.is_valid_placement(self.player_board, row, col_num, length, direction):
                        self.place_ship(self.player_board, self.player_ships, ship_name, row, col_num, length, direction)
                        placed = True
                        print(f"{ship_name} placed successfully!")
                        self.print_board(self.player_board)
                    else:
                        print("Cannot place ship there. Try again.")
                        
                except ValueError:
                    print("Invalid input. Please try again.")
    
    def place_computer_ships(self):
        print("Computer is placing ships...")
        for ship_name, length in ships.items():
            placed = False
            while not placed:
                direction = random.choice(["H", "V"])
                row = random.randint(0, BOARD_SIZE - 1)
                col = random.randint(0, BOARD_SIZE - 1)
                
                if self.is_valid_placement(self.computer_board, row, col, length, direction):
                    self.place_ship(self.computer_board, self.computer_ships, ship_name, row, col, length, direction)
                    placed = True
        print("Computer ships placed!")
    
    def attack(self, board, attack_board, row, col):
        if board[row][col] == 1:  # Hit a ship
            # Find which ship was hit and sink the entire ship
            ship_to_sink = None
            ship_dict = self.computer_ships if board == self.computer_board else self.player_ships
            
            for ship_name, positions in ship_dict.items():
                if (row, col) in positions:
                    # positions is a list, ship name and its position.
                    ship_to_sink = (ship_name, positions)
                    break
            
            if ship_to_sink:
                ship_name, positions = ship_to_sink
                # Mark all positions of this ship as hit (sunk)
                for ship_row, ship_col in positions:
                    board[ship_row][ship_col] = 2
                    attack_board[ship_row][ship_col] = 2
                return "sunk", ship_name
            else:
                # Single hit (shouldn't happen, but fallback)
                board[row][col] = 2
                attack_board[row][col] = 2
                return "hit", None
        else:  # Miss
            board[row][col] = 3
            attack_board[row][col] = 3
            return "miss", None
    
    def is_ship_sunk(self, ship_dict, ship_name, board):
        positions = ship_dict[ship_name]
        for row, col in positions:
            if board[row][col] != 2:  # Not hit
                return False
        return True
    
    def check_all_ships_sunk(self, ship_dict, board):
        for ship_name in ship_dict:
            if not self.is_ship_sunk(ship_dict, ship_name, board):
                return False
        return True
    
    def player_turn(self):
        print("\n--- Your Turn ---")
        print("Your attack board:")
        self.print_board(self.player_attack_board, attack_board=True)
        
        while True:
            try:
                coord_input = input("Enter attack coordinate (e.g., A1): ").upper()
                if len(coord_input) < 2:
                    print("Invalid coordinate format")
                    continue
                
                row_letter = coord_input[0]
                col_num = int(coord_input[1:]) - 1
                
                if row_letter not in row_to_num or col_num < 0 or col_num >= BOARD_SIZE:
                    print("Invalid coordinate")
                    continue
                
                row = row_to_num[row_letter]
                
                if self.player_attack_board[row][col_num] != 0:
                    print("You already attacked this position!")
                    continue
                
                result, ship_name = self.attack(self.computer_board, self.player_attack_board, row, col_num)
                
                if result == "sunk":
                    print(f"HIT AND SUNK! You destroyed the computer's {ship_name}!")
                elif result == "hit":
                    print("HIT!")
                else:
                    print("Miss!")
                
                break
                
            except ValueError:
                print("Invalid input. Please try again.")
    
    def computer_turn(self):
        print("\n--- Computer's Turn ---")
        while True:
            row = random.randint(0, BOARD_SIZE - 1)
            col = random.randint(0, BOARD_SIZE - 1)
            
            if self.computer_attack_board[row][col] == 0:
                result, ship_name = self.attack(self.player_board, self.computer_attack_board, row, col)
                coord = f"{row_labels[row]}{col + 1}"
                
                if result == "sunk":
                    print(f"Computer attacks {coord} - HIT AND SUNK! Computer destroyed your {ship_name}!")
                elif result == "hit":
                    print(f"Computer attacks {coord} - HIT!")
                else:
                    print(f"Computer attacks {coord} - Miss!")
                
                break
    
    def play(self):
        # Setup phase
        self.place_player_ships()
        self.place_computer_ships()
        
        print("\n" + "="*50)
        print("BATTLE BEGINS!")
        print("="*50)
        
        # Game loop
        while True:
            # Player turn
            self.player_turn()
            
            if self.check_all_ships_sunk(self.computer_ships, self.computer_board):
                print("\n🎉 CONGRATULATIONS! You won! All computer ships destroyed! 🎉")
                break
            
            # Computer turn
            self.computer_turn()
            
            if self.check_all_ships_sunk(self.player_ships, self.player_board):
                print("\n💥 Game Over! Computer won! All your ships destroyed! 💥")
                break
            
            # Show current status
            print("\nYour board:")
            self.print_board(self.player_board)
            
            input("Press Enter to continue...")

# Start the game
if __name__ == "__main__":
    game = BattleshipGame()
    game.play()