# pygame_game.py
import pygame
import json
import random
import time
import sys
import os

# Ensure assets dir exists (we'll draw shapes instead)
os.makedirs("assets", exist_ok=True)

class HarvestHorizonGame:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1200, 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Harvest Horizon - The Satellite Steward")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        
        self.load_game_data()
        self.load_state()
        
        self.dice_value = 0
        self.is_rolling = False
        self.roll_start_time = 0
        self.rolling_dice = 1
        self.buttons = {}
        self.card_buttons = []
        self.shop_buttons = []

    def load_game_data(self):
        with open("game_content.json", "r") as f:
            self.game_data = json.load(f)

    def load_state(self):
        try:
            with open("game_state.json", "r") as f:
                self.state = json.load(f)
        except:
            self.state = {
                "current_player": 0,
                "players": [
                    {"name": "Player 1", "position": 0, "cash": 10000, "sustainability": 7, "assets": []},
                    {"name": "Player 2", "position": 0, "cash": 10000, "sustainability": 7, "assets": []}
                ],
                "game_state": "ROLL",
                "dice_value": 0,
                "current_card": None,
                "selected_solution": None
            }

    def save_state(self):
        self.state["last_update"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        with open("game_state.json", "w") as f:
            json.dump(self.state, f, indent=2)

    def draw_board(self):
        # Simple circular board with 10 tiles
        center_x, center_y = 600, 400
        radius = 250
        num_tiles = len(self.game_data["board_tiles"])
        
        for i, tile in enumerate(self.game_data["board_tiles"]):
            angle = (i / num_tiles) * 2 * 3.14159 - 1.57  # Start at top
            x = center_x + radius * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            y = center_y + radius * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            
            color = (70, 130, 180) if tile["type"] == "field" else (50, 205, 50) if tile["type"] == "shop" else (255, 140, 0) if tile["type"] == "event" else (100, 100, 100)
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 40)
            
            text = self.small_font.render(tile["name"][:10], True, (255, 255, 255))
            self.screen.blit(text, (x - text.get_width()//2, y - text.get_height()//2))

    def draw_players(self):
        center_x, center_y = 600, 400
        radius = 250
        num_tiles = len(self.game_data["board_tiles"])
        
        for idx, player in enumerate(self.state["players"]):
            pos = player["position"]
            angle = (pos / num_tiles) * 2 * 3.14159 - 1.57
            x = center_x + (radius - 20) * pygame.math.Vector2(1, 0).rotate_rad(angle).x
            y = center_y + (radius - 20) * pygame.math.Vector2(1, 0).rotate_rad(angle).y
            
            color = (255, 0, 0) if idx == 0 else (0, 0, 255)
            pygame.draw.circle(self.screen, color, (int(x), int(y)), 15)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(x), int(y)), 15, 2)

    def draw_ui(self):
        # Player info
        current = self.state["players"][self.state["current_player"]]
        info = [
            f"Turn: {current['name']}",
            f"Cash: ${current['cash']}",
            f"Sustainability: {current['sustainability']}/10"
        ]
        for i, line in enumerate(info):
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (50, 50 + i*40))

        # Game state
        state_text = self.font.render(f"State: {self.state['game_state']}", True, (200, 200, 200))
        self.screen.blit(state_text, (50, 200))

        # Dice
        if self.is_rolling:
            dice_val = random.randint(1, 6)
        else:
            dice_val = self.state.get("dice_value", 0)
        
        dice_text = self.font.render(f"Dice: {dice_val}", True, (255, 255, 0))
        self.screen.blit(dice_text, (50, 250))

        # Buttons
        self.buttons = {}
        if self.state["game_state"] == "ROLL":
            btn = pygame.Rect(50, 320, 150, 50)
            pygame.draw.rect(self.screen, (0, 200, 0), btn)
            text = self.font.render("Roll Dice", True, (255, 255, 255))
            self.screen.blit(text, (btn.x + 10, btn.y + 10))
            self.buttons["roll"] = btn

        elif self.state["game_state"] == "CARD" and self.state["current_card"]:
            card = self.state["current_card"]
            pygame.draw.rect(self.screen, (30, 30, 50), (400, 100, 400, 300))
            title = self.font.render(card["title"], True, (255, 215, 0))
            self.screen.blit(title, (500, 120))
            desc = self.small_font.render(card["description"], True, (255, 255, 255))
            self.screen.blit(desc, (420, 170))
            
            self.card_buttons = []
            for i, sol in enumerate(card["solutions"]):
                btn = pygame.Rect(450, 220 + i*60, 300, 50)
                pygame.draw.rect(self.screen, (70, 130, 180), btn)
                sol_text = self.small_font.render(f"{sol['title']} (${sol['cost']})", True, (255, 255, 255))
                self.screen.blit(sol_text, (btn.x + 10, btn.y + 15))
                self.card_buttons.append((btn, sol))

        elif self.state["game_state"] == "SHOP":
            pygame.draw.rect(self.screen, (30, 50, 30), (400, 100, 400, 300))
            shop_title = self.font.render("Agri-Tech Store", True, (50, 205, 50))
            self.screen.blit(shop_title, (500, 120))
            
            self.shop_buttons = []
            for i, asset in enumerate(self.game_data["assets"]):
                btn = pygame.Rect(450, 180 + i*70, 300, 60)
                color = (100, 200, 100) if current["cash"] >= asset["cost"] else (100, 100, 100)
                pygame.draw.rect(self.screen, color, btn)
                asset_text = self.small_font.render(f"{asset['name']} (${asset['cost']})", True, (0, 0, 0) if color == (100,200,100) else (150,150,150))
                desc_text = self.small_font.render(asset["description"], True, (200, 200, 200))
                self.screen.blit(asset_text, (btn.x + 10, btn.y + 10))
                self.screen.blit(desc_text, (btn.x + 10, btn.y + 30))
                self.shop_buttons.append((btn, asset))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.state["game_state"] == "ROLL" and "roll" in self.buttons:
                    if self.buttons["roll"].collidepoint(mouse_pos):
                        self.roll_dice()
                
                elif self.state["game_state"] == "CARD":
                    for btn, sol in self.card_buttons:
                        if btn.collidepoint(mouse_pos):
                            self.select_solution(sol)
                
                elif self.state["game_state"] == "SHOP":
                    current = self.state["players"][self.state["current_player"]]
                    for btn, asset in self.shop_buttons:
                        if btn.collidepoint(mouse_pos) and current["cash"] >= asset["cost"]:
                            self.buy_asset(asset)

    def roll_dice(self):
        self.is_rolling = True
        self.roll_start_time = pygame.time.get_ticks()
        self.rolling_dice = 1

    def select_solution(self, solution):
        player = self.state["players"][self.state["current_player"]]
        if player["cash"] >= solution["cost"]:
            player["cash"] -= solution["cost"]
            if "sustainability_change" in solution["effect"]:
                player["sustainability"] = max(1, min(10, player["sustainability"] + solution["effect"]["sustainability_change"]))
            self.state["game_state"] = "ROLL"
            self.state["current_card"] = None
            self.end_turn()

    def buy_asset(self, asset):
        player = self.state["players"][self.state["current_player"]]
        player["cash"] -= asset["cost"]
        player["assets"].append(asset["id"])
        # Apply income boost immediately for simplicity
        player["cash"] += asset.get("income_boost", 0)
        self.state["game_state"] = "ROLL"
        self.end_turn()

    def end_turn(self):
        self.state["current_player"] = (self.state["current_player"] + 1) % len(self.state["players"])
        self.save_state()

    def update(self):
        if self.is_rolling:
            now = pygame.time.get_ticks()
            if now - self.roll_start_time > 1000:  # 1 second roll animation
                self.dice_value = random.randint(1, 6)
                self.state["dice_value"] = self.dice_value
                self.is_rolling = False
                
                # Move player
                player = self.state["players"][self.state["current_player"]]
                player["position"] = (player["position"] + self.dice_value) % len(self.game_data["board_tiles"])
                
                # Check tile type
                tile = self.game_data["board_tiles"][player["position"]]
                if tile["type"] == "event":
                    self.state["current_card"] = random.choice(self.game_data["problem_cards"])
                    self.state["game_state"] = "CARD"
                elif tile["type"] == "shop":
                    self.state["game_state"] = "SHOP"
                else:
                    # Field: earn income
                    income = 500
                    # Bonus for assets
                    for aid in player["assets"]:
                        for asset in self.game_data["assets"]:
                            if asset["id"] == aid:
                                income += asset.get("income_boost", 0)
                    player["cash"] += income
                    self.end_turn()
                
                self.save_state()

    def render(self):
        self.screen.fill((20, 30, 40))  # Dark blue background
        self.draw_board()
        self.draw_players()
        self.draw_ui()
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)

if __name__ == "__main__":
    game = HarvestHorizonGame()
    game.run()