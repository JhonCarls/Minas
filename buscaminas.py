import pygame
import random
import sys

# Inicializar pygame
pygame.init()
pygame.mixer.init()

# Cargar y reproducir la música de fondo
pygame.mixer.music.load("musica_fondo.mp3")
pygame.mixer.music.play(-1)  # El argumento -1 hace que la música se repita indefinidamente

# Dimensiones del tablero y la ventana
BOARD_WIDTH = 300
BOARD_HEIGHT = 300
PANEL_WIDTH = 200  # Espacio para controles y panel lateral
WINDOW_WIDTH = BOARD_WIDTH + PANEL_WIDTH
WINDOW_HEIGHT = 300

ROWS = 10
COLS = 10
MINES = 10
CELL_SIZE = BOARD_WIDTH // COLS

# Colores
GRAY = (160, 160, 160)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Configuración de la pantalla
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Buscaminas")

# Fuentes
font = pygame.font.SysFont(None, 26)
small_font = pygame.font.SysFont(None, 24)

# Estado de la ayuda
help_mode = False
help_response_shown = False
help_uses = 3  # Limitar el uso de la ayuda a 3 veces

# Crear la clase del tablero
class Board:
    def __init__(self, rows, cols, mines):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.flags_available = mines
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]
        self.flags = [[False for _ in range(cols)] for _ in range(rows)]
        self.mine_positions = []
        self.place_mines()
        self.calculate_neighbors()

    def place_mines(self):
        while len(self.mine_positions) < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if (row, col) not in self.mine_positions:
                self.mine_positions.append((row, col))
                self.grid[row][col] = -1  # Representa una mina

    def calculate_neighbors(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] == -1:
                    continue
                mines_count = 0
                for r in range(-1, 2):
                    for c in range(-1, 2):
                        if 0 <= row + r < self.rows and 0 <= col + c < self.cols:
                            if self.grid[row + r][col + c] == -1:
                                mines_count += 1
                self.grid[row][col] = mines_count

    def reveal(self, row, col):
        if self.revealed[row][col] or self.flags[row][col]:
            return
        self.revealed[row][col] = True
        if self.grid[row][col] == 0:
            for r in range(-1, 2):
                for c in range(-1, 2):
                    if 0 <= row + r < self.rows and 0 <= col + c < self.cols:
                        self.reveal(row + r, col + c)

    def flag(self, row, col):
        if not self.revealed[row][col] and self.flags_available > 0:
            self.flags[row][col] = not self.flags[row][col]
            if self.flags[row][col]:
                self.flags_available -= 1
            else:
                self.flags_available += 1

    def draw(self, screen):
        # Dibujar el tablero
        for row in range(self.rows):
            for col in range(self.cols):
                rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.revealed[row][col]:
                    pygame.draw.rect(screen, WHITE, rect)
                    if self.grid[row][col] > 0:
                        text = font.render(str(self.grid[row][col]), True, BLACK)
                        screen.blit(text, (col * CELL_SIZE + 15, row * CELL_SIZE + 10))
                else:
                    pygame.draw.rect(screen, GRAY, rect)
                pygame.draw.rect(screen, BLACK, rect, 1)
                if self.flags[row][col]:
                    pygame.draw.circle(screen, RED, (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2), 10)

        # Dibujar el panel lateral con la información
        panel_rect = pygame.Rect(BOARD_WIDTH, 0, PANEL_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(screen, YELLOW, panel_rect)

        # Mostrar información en el panel
        text_mines = small_font.render(f"Minas: {self.mines}", True, BLACK)
        text_flags = small_font.render(f"Banderas: {self.flags_available}", True, BLACK)
        text_help = small_font.render(f"Ayudas: {help_uses}", True, BLACK)  # Mostrar las ayudas disponibles
        screen.blit(text_mines, (BOARD_WIDTH + 20, 30))
        screen.blit(text_flags, (BOARD_WIDTH + 20, 60))
        screen.blit(text_help, (BOARD_WIDTH + 20, 90))  # Añadir contador de ayudas

    def check_win(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if not self.revealed[row][col] and self.grid[row][col] != -1:
                    return False
        return True

    def check_loss(self, row, col):
        return self.grid[row][col] == -1

    def use_ai(self, row, col):
        
        if not self.is_near_revealed(row, col):
            return "No es posible ayudar, no hay celdas reveladas cerca."
        if self.grid[row][col] == -1:
            return "Cuidado, existe una mina"
        else:
            return "En este cuadro no hay una mina"

    def is_near_revealed(self, row, col):
        # Verifica si la celda tiene vecinos revelados
        for r in range(-1, 2):
            for c in range(-1, 2):
                if r == 0 and c == 0:
                    continue
                if 0 <= row + r < self.rows and 0 <= col + c < self.cols:
                    if self.revealed[row + r][col + c]:
                        return True
        return False

def show_help_message(message):
    # Mostrar la ventana emergente con el mensaje de ayuda
    message_rect = pygame.Rect(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 4, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    pygame.draw.rect(screen, WHITE, message_rect)
    text = font.render(message, True, BLACK)
    screen.blit(text, (WINDOW_WIDTH // 4, WINDOW_HEIGHT // 4))
    pygame.display.flip()
    pygame.time.wait(2000)  # Mostrar por 2 segundos

def show_game_over():
    # Mostrar la ventana emergente cuando se pierde
    message_rect = pygame.Rect(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 4, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    pygame.draw.rect(screen, WHITE, message_rect)
    text = font.render("¡Perdiste!", True, BLACK)
    screen.blit(text, (WINDOW_WIDTH // 3, WINDOW_HEIGHT // 3))
    pygame.display.flip()
    pygame.time.wait(2000)

# Inicializar el tablero
board = Board(ROWS, COLS, MINES)

def main():
    global help_mode, help_response_shown, help_uses
    game_over = False
    running = True
    while running:
        screen.fill(GRAY)
        board.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = event.pos
                col = x // CELL_SIZE
                row = y // CELL_SIZE

                if event.button == 1:  # Click izquierdo
                    if help_mode:
                        message = board.use_ai(row, col)
                        show_help_message(message)
                        help_mode = False  # Desactivar el modo ayuda después de mostrar el mensaje
                        help_response_shown = True
                    elif board.check_loss(row, col):
                        show_game_over()
                        game_over = True
                    else:
                        board.reveal(row, col)

                elif event.button == 3:  # Click derecho
                    board.flag(row, col)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a and not game_over and help_uses > 0:  # Activar la ayuda con la tecla 'A'
                    help_mode = True
                    help_uses -= 1  # Reducir la cantidad de ayudas disponibles

        if board.check_win():
            print("¡Ganaste!")
            game_over = True

        pygame.display.flip()

if __name__ == "__main__":
    main()
