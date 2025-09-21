import pygame
from .game_state import GameState
from ..entities import Player, GermanSoldier, GermanOfficer, ActionType

class CombatState(GameState):
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.party = [Player("Jean", "French Soldier")]
        self.enemies = [GermanSoldier(), GermanOfficer()]

        self.turn_order = []
        self.current_turn = 0
        self.player_action = None
        self.game_over = False
        self.victory = False

        self.menu_options = ["Attack", "Defend", "Item", "Run"]
        self.selected_option = 0
        self.in_target_selection = False
        self.selected_target = 0

        self.calculate_turn_order()

        self.message_log = ["Combat begins in the Maginot bunker!"]
        self.max_messages = 5

    def calculate_turn_order(self):
        all_combatants = self.party + self.enemies
        all_combatants = [c for c in all_combatants if c.is_alive]
        self.turn_order = sorted(all_combatants, key=lambda x: x.speed, reverse=True)
        self.current_turn = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.game_over:
                return

            current_actor = self.turn_order[self.current_turn] if self.turn_order else None

            if current_actor in self.party:
                if not self.in_target_selection:
                    if event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if self.menu_options[self.selected_option] == "Attack":
                            self.in_target_selection = True
                            self.selected_target = 0
                        elif self.menu_options[self.selected_option] == "Defend":
                            current_actor.defend()
                            self.add_message(f"{current_actor.name} defends!")
                            self.next_turn()
                else:
                    alive_enemies = [e for e in self.enemies if e.is_alive]
                    if alive_enemies:
                        if event.key == pygame.K_UP:
                            self.selected_target = (self.selected_target - 1) % len(alive_enemies)
                        elif event.key == pygame.K_DOWN:
                            self.selected_target = (self.selected_target + 1) % len(alive_enemies)
                        elif event.key == pygame.K_RETURN:
                            target = alive_enemies[self.selected_target]
                            damage = current_actor.attack_enemy(target)
                            self.add_message(f"{current_actor.name} attacks {target.name} for {damage} damage!")
                            if not target.is_alive:
                                self.add_message(f"{target.name} is defeated!")
                            self.in_target_selection = False
                            self.next_turn()
                        elif event.key == pygame.K_ESCAPE:
                            self.in_target_selection = False

    def add_message(self, message):
        self.message_log.append(message)
        if len(self.message_log) > self.max_messages:
            self.message_log.pop(0)

    def next_turn(self):
        if self.turn_order:
            current_actor = self.turn_order[self.current_turn]
            current_actor.reset_turn_effects()

            self.current_turn = (self.current_turn + 1) % len(self.turn_order)

            if self.check_victory():
                self.victory = True
                self.game_over = True
                self.add_message("Victory! The bunker is secure!")
            elif self.check_defeat():
                self.game_over = True
                self.add_message("Defeat! The bunker has fallen...")
            else:
                self.calculate_turn_order()
                if self.current_turn >= len(self.turn_order):
                    self.current_turn = 0

    def check_victory(self):
        return all(not enemy.is_alive for enemy in self.enemies)

    def check_defeat(self):
        return all(not player.is_alive for player in self.party)

    def update(self, dt):
        if not self.game_over and self.turn_order:
            current_actor = self.turn_order[self.current_turn]

            if current_actor not in self.party and current_actor.is_alive:
                alive_players = [p for p in self.party if p.is_alive]
                if alive_players:
                    action, target = current_actor.choose_action(alive_players)

                    if action == ActionType.ATTACK and target:
                        damage = current_actor.attack_enemy(target)
                        self.add_message(f"{current_actor.name} attacks {target.name} for {damage} damage!")
                        if not target.is_alive:
                            self.add_message(f"{target.name} has fallen!")
                    elif action == ActionType.DEFEND:
                        current_actor.defend()
                        self.add_message(f"{current_actor.name} defends!")

                    self.next_turn()

    def render(self, screen):
        screen.fill((40, 30, 20))

        y_offset = 50

        title = self.font.render("LIGNE MAUDITE - COMBAT", True, (255, 255, 255))
        screen.blit(title, (20, 20))

        party_text = self.small_font.render("ALLIED FORCES:", True, (100, 255, 100))
        screen.blit(party_text, (20, y_offset))
        y_offset += 30

        for player in self.party:
            color = (255, 255, 255) if player.is_alive else (128, 128, 128)
            text = f"{player.name}: {player.hp}/{player.max_hp} HP"
            if hasattr(player, 'job'):
                text += f" ({player.job})"
            rendered = self.small_font.render(text, True, color)
            screen.blit(rendered, (40, y_offset))
            y_offset += 25

        y_offset += 20
        enemy_text = self.small_font.render("GERMAN FORCES:", True, (255, 100, 100))
        screen.blit(enemy_text, (20, y_offset))
        y_offset += 30

        for i, enemy in enumerate(self.enemies):
            color = (255, 255, 255) if enemy.is_alive else (128, 128, 128)
            if self.in_target_selection and enemy.is_alive:
                alive_enemies = [e for e in self.enemies if e.is_alive]
                if i < len(alive_enemies) and alive_enemies.index(enemy) == self.selected_target:
                    color = (255, 255, 0)

            text = f"{enemy.name}: {enemy.hp}/{enemy.max_hp} HP"
            rendered = self.small_font.render(text, True, color)
            screen.blit(rendered, (40, y_offset))
            y_offset += 25

        if self.turn_order:
            current_actor = self.turn_order[self.current_turn]
            turn_text = f"Current Turn: {current_actor.name}"
            rendered = self.small_font.render(turn_text, True, (255, 255, 100))
            screen.blit(rendered, (400, 100))

        if not self.game_over and self.turn_order and self.turn_order[self.current_turn] in self.party:
            if not self.in_target_selection:
                menu_text = self.small_font.render("Choose Action:", True, (255, 255, 255))
                screen.blit(menu_text, (400, 150))

                for i, option in enumerate(self.menu_options):
                    color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
                    text = self.small_font.render(f"→ {option}" if i == self.selected_option else f"  {option}", True, color)
                    screen.blit(text, (420, 180 + i * 25))
            else:
                target_text = self.small_font.render("Select Target:", True, (255, 255, 255))
                screen.blit(target_text, (400, 150))

        log_title = self.small_font.render("Combat Log:", True, (255, 255, 255))
        screen.blit(log_title, (400, 300))

        for i, message in enumerate(self.message_log[-self.max_messages:]):
            text = self.small_font.render(message, True, (200, 200, 200))
            screen.blit(text, (400, 330 + i * 20))

        if self.game_over:
            game_over_text = "VICTORY!" if self.victory else "DEFEAT!"
            color = (100, 255, 100) if self.victory else (255, 100, 100)
            rendered = self.font.render(game_over_text, True, color)
            screen.blit(rendered, (400, 500))