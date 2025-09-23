import pygame
import os
import sys
import random
from .game_state import GameState
from ..ui.quit_overlay import QuitOverlay
from ..audio.audio_manager import AudioManager

# Add the project root to the path to import assets
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from assets.sprites.protagonist import create_protagonist_animation_system
from assets.sprites.rat_enemy import create_rat_animation_system

class Fight0State(GameState):
    def __init__(self, screen, audio_manager=None):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Load fight background
        self.background = self.load_fight_background()

        # Create protagonist animation system
        self.protagonist_animation, self.using_sprite_sheet = create_protagonist_animation_system()

        # Character positioning
        self.setup_characters()

        # Create mock rat enemy
        self.create_rat_enemy()

        # Audio manager
        if audio_manager:
            self.audio = audio_manager
        else:
            self.audio = AudioManager()

        # Fight system
        self.setup_fight_system()

        # Quit overlay
        self.quit_overlay = QuitOverlay()

        # Initialize poison cloud effect
        self.poison_cloud = {"active": False}

        # Initialize dual enemies system
        self.dual_enemies = False
        self.enemies = {}
        self.current_enemy_attacker = None

        print("Fight0 scene initialized with protagonist and enemy!")

    def load_fight_background(self):
        """Load fight.png from fight0 folder or create fallback"""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            bg_path = os.path.join(project_root, "assets", "images", "backgrounds", "fight0", "fight.png")

            if os.path.exists(bg_path):
                background = pygame.image.load(bg_path)
                background = pygame.transform.scale(background, (self.screen_width, self.screen_height))
                print(f"Loaded fight background from: {bg_path}")
                return background
            else:
                print(f"fight.png not found at {bg_path}, creating fallback")
                return self.create_fallback_background()

        except Exception as e:
            print(f"Error loading fight background: {e}")
            return self.create_fallback_background()

    def create_fallback_background(self):
        """Create a fallback fight background"""
        background = pygame.Surface((self.screen_width, self.screen_height))

        # Dark battlefield colors
        background.fill((40, 30, 25))  # Dark brown battlefield

        # Draw simple battlefield elements
        # Horizon line
        horizon_y = self.screen_height // 2
        pygame.draw.line(background, (60, 45, 35), (0, horizon_y), (self.screen_width, horizon_y), 3)

        # Ground texture
        for i in range(0, self.screen_width, 30):
            pygame.draw.line(background, (50, 35, 25), (i, horizon_y), (i, self.screen_height), 1)

        # Sky gradient effect
        for y in range(0, horizon_y, 5):
            gray_value = 40 + (y * 20 // horizon_y)
            color = (gray_value, gray_value - 10, gray_value - 15)
            pygame.draw.line(background, color, (0, y), (self.screen_width, y))

        return background

    def setup_characters(self):
        """Setup character positions and scaling"""
        # Smart scaling based on detected frame size
        current_frame = self.protagonist_animation.get_current_frame()
        if current_frame:
            frame_w, frame_h = current_frame.get_size()
            print(f"Detected protagonist frame size: {frame_w}x{frame_h}")

            # Auto-adjust scaling based on frame size
            if frame_w <= 48 and frame_h <= 64:
                self.protagonist_scale = 2.0  # Larger for fight scene
                print("Using 2.0x scale for processed sprites")
            elif frame_w <= 96 and frame_h <= 128:
                self.protagonist_scale = 1.5
                print("Using 1.5x scale for medium sprites")
            elif frame_w <= 160 and frame_h <= 240:
                self.protagonist_scale = 1.0
                print("Using 1.0x scale for large sprites")
            elif frame_w == 256 and frame_h == 320:
                self.protagonist_scale = 0.4
                print("Using 0.4x scale for 256x320 sprites")
            else:
                self.protagonist_scale = 0.4
                print("Using 0.4x scale for very large sprites")
        else:
            self.protagonist_scale = 1.5

        # Position protagonist in lower left (moved to avoid menu overlap)
        self.initial_protagonist_x = self.screen_width * 0.3   # 30% from left (moved right)
        self.initial_protagonist_y = self.screen_height * 0.55  # 55% down (moved up)
        self.protagonist_x = self.initial_protagonist_x
        self.protagonist_y = self.initial_protagonist_y

        # Set protagonist to idle animation facing right (toward enemy)
        self.protagonist_animation.play_animation('idle_right')

    def create_rat_enemy(self):
        """Create animated enemy/enemies - randomly single or dual"""
        # Create enemy animation system
        result = create_rat_animation_system()
        if len(result) == 5:
            self.rat_animation, self.using_rat_sprite_sheet, self.enemy_type, self.enemy_damage, self.enemy_attack = result
        else:
            # Fallback for old return format
            self.rat_animation, self.using_rat_sprite_sheet = result[:2]
            self.enemy_type = "rat"
            self.enemy_damage = 5
            self.enemy_attack = "CLAWS"

        print(f"Selected enemy: {self.enemy_type}")

        # Handle alternating enemy setup
        if self.enemy_type == "both":
            self.dual_enemies = False  # Keep it simple - single enemy with alternating behavior
            # Higher HP since fighting both enemies (alternating)
            enemy_hp = 15  # More HP for both enemies combined
            self.alternating_attacks = True
            self.attack_count = 0  # Track attacks for alternating
            print("Fighting both enemies! They will alternate between BITE and POISON attacks.")
        else:
            self.dual_enemies = False
            self.alternating_attacks = False
            # Single enemy setup
            if self.enemy_type == "cockroach":
                enemy_hp = 6
            elif self.enemy_type == "frog":
                enemy_hp = 7
            else:
                enemy_hp = 30  # Default for rat

        self.rat_stats = {
            "hp": enemy_hp,
            "max_hp": enemy_hp
        }

        # Position enemies
        if not self.dual_enemies:
            # Single enemy positioning
            self.initial_enemy_x = self.screen_width * 0.55   # 55% from left (well centered)
            self.initial_enemy_y = self.screen_height * 0.25   # 25% down (higher up for visibility)
            self.enemy_x = self.initial_enemy_x
            self.enemy_y = self.initial_enemy_y

            # Start with initial selection animation
            self.rat_animation.play_animation('initial_selection')
            self.rat_animation_phase = "initial"
        else:
            # Dual enemies positioning (already set in enemies dict)
            for enemy_name, enemy in self.enemies.items():
                enemy["animation"].play_animation('initial_selection')

        # Enemy scale (much smaller since sprite frames are large!)
        self.enemy_scale = 0.25  # Fixed small scale to ensure visibility


    def setup_fight_system(self):
        """Setup fight menu, stats, and turn system"""
        # Turn system
        self.player_turn = True
        self.turn_indicator_color = (255, 255, 0)  # Yellow

        # Fight menu system
        self.menu_visible = True
        self.selected_menu_item = 0
        self.in_submenu = False
        self.submenu_selected = 0

        # Menu items
        self.main_menu_items = [
            {"text": "Attack", "enabled": True},
            {"text": "Construct", "enabled": False},  # Greyed out
            {"text": "Item", "enabled": True}
        ]

        self.item_submenu = [
            {"text": "Potion 1", "count": 1}
        ]

        # Combat state
        self.combat_state = "menu"  # menu, attacking, item_used
        self.attack_timer = 0.0
        self.attack_duration = 2.0
        self.projectiles = []

        # Heal effect
        self.showing_heal = False
        self.heal_effect_timer = 0.0
        self.heal_effect_duration = 2.0

        # Damage numbers
        self.showing_damage = False
        self.damage_text = ""
        self.damage_timer = 0.0
        self.damage_duration = 1.5
        self.damage_target = None  # "rat" or "protagonist"

        # Rat attack system
        self.rat_attack_state = "none"  # none, banner, jumping, attacking, returning
        self.rat_attack_timer = 0.0
        self.banner_duration = 2.0
        self.rat_jump_duration = 0.5
        self.rat_attack_duration = 0.3
        self.rat_return_duration = 0.5

        # Stats
        self.protagonist_stats = {
            "name": "Proto",
            "hp": 50,
            "mp": 15,
            "anger": 0,
            "max_anger": 10
        }

        # Enemy stats (will be set in create_rat_enemy based on enemy type)

        # Victory system
        self.victory_state = "none"  # none, victory_jump, victory_text, fading
        self.victory_timer = 0.0
        self.jump_count = 0
        self.jump_duration = 0.3
        self.text_duration = 2.0
        self.fade_duration = 2.0

        # Menu positioning (lower left corner)
        self.menu_x = 20
        self.menu_y = self.screen_height - 180
        self.menu_width = 200
        self.menu_height = 120

        # Stats table positioning (next to menu)
        self.stats_x = self.menu_x + self.menu_width + 20
        self.stats_y = self.menu_y
        self.stats_width = 250
        self.stats_height = 80

    def create_potion_icon(self):
        """Create a small potion bottle icon"""
        potion_surface = pygame.Surface((16, 16), pygame.SRCALPHA)

        # Bottle body (glass)
        pygame.draw.rect(potion_surface, (200, 200, 255), (6, 6, 4, 8))
        # Red liquid
        pygame.draw.rect(potion_surface, (255, 50, 50), (6, 10, 4, 4))
        # Bottle neck
        pygame.draw.rect(potion_surface, (150, 150, 150), (7, 4, 2, 3))
        # Cork
        pygame.draw.rect(potion_surface, (139, 69, 19), (7, 3, 2, 2))

        return potion_surface

    def handle_event(self, event):
        # Handle quit overlay input first if it's visible
        if self.quit_overlay.is_visible():
            result = self.quit_overlay.handle_input(event)
            if result == "quit":
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return None
            elif result == "resume":
                return None
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Handle ESC based on menu state
                if self.menu_visible and self.in_submenu:
                    # In submenu - go back to main menu
                    self.in_submenu = False
                elif self.menu_visible and not self.in_submenu:
                    # In main menu - show quit overlay
                    self.quit_overlay.show()
                else:
                    # Menu not visible - show quit overlay
                    self.quit_overlay.show()
            elif event.key == pygame.K_SPACE:
                # Toggle audio mute
                self.audio.toggle_mute()
            elif self.menu_visible and self.combat_state == "menu" and self.player_turn:
                self.handle_menu_input(event)
            elif event.key == pygame.K_r and not self.player_turn:
                # Reset turn to player (for testing) - press R during rat's turn
                self.player_turn = True

        return None

    def handle_menu_input(self, event):
        """Handle menu navigation input"""
        if not self.in_submenu:
            # Main menu navigation
            if event.key == pygame.K_UP:
                self.selected_menu_item = (self.selected_menu_item - 1) % len(self.main_menu_items)
            elif event.key == pygame.K_DOWN:
                self.selected_menu_item = (self.selected_menu_item + 1) % len(self.main_menu_items)
            elif event.key == pygame.K_RETURN:
                selected_item = self.main_menu_items[self.selected_menu_item]
                if selected_item["enabled"]:
                    if selected_item["text"] == "Attack":
                        self.start_attack()
                    elif selected_item["text"] == "Item":
                        self.in_submenu = True
                        self.submenu_selected = 0
        else:
            # Submenu navigation
            if event.key == pygame.K_UP:
                self.submenu_selected = (self.submenu_selected - 1) % len(self.item_submenu)
            elif event.key == pygame.K_DOWN:
                self.submenu_selected = (self.submenu_selected + 1) % len(self.item_submenu)
            elif event.key == pygame.K_RETURN:
                # Only use item if it's available
                if self.submenu_selected < len(self.item_submenu):
                    item = self.item_submenu[self.submenu_selected]
                    if item["count"] > 0:
                        self.use_item()

    def start_attack(self):
        """Start attack sequence with jump to center"""
        self.menu_visible = False
        self.combat_state = "attacking"
        self.attack_timer = 0.0
        self.projectiles = []

        # Attack phases: jumping, shooting, returning
        self.attack_phase = "jumping"  # jumping, shooting, returning
        self.jump_duration = 0.5
        self.shoot_duration = 2.5  # Increased to give projectiles more time to reach rat
        self.return_duration = 0.5

        # Center position for attack
        self.center_x = self.screen_width * 0.5
        self.center_y = self.screen_height * 0.5

    def use_item(self):
        """Use selected item"""
        if self.submenu_selected < len(self.item_submenu):
            item = self.item_submenu[self.submenu_selected]
            if item["count"] > 0:
                item["count"] -= 1
                # Update item text to show new count
                item["text"] = f"Potion {item['count']}"

                # Heal protagonist
                self.protagonist_stats["hp"] = min(50, self.protagonist_stats["hp"] + 50)

                # Show +50 effect
                self.show_heal_effect()

                # Close menu and start rat turn
                self.menu_visible = False
                self.in_submenu = False
                self.combat_state = "item_used"

    def show_heal_effect(self):
        """Show +50 healing effect"""
        self.heal_effect_timer = 0.0
        self.heal_effect_duration = 2.0
        self.showing_heal = True

    def update(self, dt):
        # Don't update game logic if quit overlay is visible
        if self.quit_overlay.is_visible():
            return

        # Update protagonist animation
        self.protagonist_animation.update(dt)

        # Update rat animation
        # Update enemy animations
        print(f"In update: dual_enemies = {self.dual_enemies}")
        if self.dual_enemies:
            # Update both enemy animations
            for enemy_name, enemy in self.enemies.items():
                enemy["animation"].update(dt)
        else:
            # Update single enemy animation
            self.rat_animation.update(dt)

        # Update combat state
        if self.combat_state == "attacking":
            self.update_attack(dt)
        elif self.combat_state == "item_used":
            self.update_heal_effect(dt)

        # Update rat attack (when it's rat's turn and rat is alive)
        if not self.player_turn and self.rat_stats["hp"] > 0:
            self.update_rat_attack(dt)

        # Update damage numbers
        if self.showing_damage:
            self.damage_timer += dt
            if self.damage_timer >= self.damage_duration:
                self.showing_damage = False

        # Update poison cloud effect
        if self.poison_cloud["active"]:
            self.update_poison_cloud(dt)

        # Update victory sequence
        if self.victory_state != "none":
            self.update_victory_sequence(dt)

        return None

    def update_attack(self, dt):
        """Update attack animation and projectiles with phases"""
        self.attack_timer += dt

        if self.attack_phase == "jumping":
            # Animate protagonist jumping to center
            progress = min(1.0, self.attack_timer / self.jump_duration)

            # Smooth interpolation
            smooth_progress = progress * progress * (3.0 - 2.0 * progress)

            self.protagonist_x = self.initial_protagonist_x + (self.center_x - self.initial_protagonist_x) * smooth_progress
            self.protagonist_y = self.initial_protagonist_y + (self.center_y - self.initial_protagonist_y) * smooth_progress

            if progress >= 1.0:
                self.attack_phase = "shooting"
                self.attack_timer = 0.0
                self.create_projectiles()

        elif self.attack_phase == "shooting":
            # Update projectiles
            for projectile in self.projectiles[:]:
                # Handle delay before projectile starts moving
                if 'delay' in projectile:
                    projectile['delay'] -= dt
                    if projectile['delay'] > 0:
                        continue  # Skip movement until delay is over

                # Use velocity components if available, otherwise fall back to speed
                if 'vx' in projectile and 'vy' in projectile:
                    projectile['x'] += projectile['vx'] * dt
                    projectile['y'] += projectile['vy'] * dt
                else:
                    projectile['x'] += projectile.get('speed', 200) * dt

                projectile['life'] -= dt / 2.0

                # Check collision with rat
                if self.check_projectile_rat_collision(projectile):
                    self.projectiles.remove(projectile)
                    self.hit_rat()
                    continue

                # Remove projectiles that are off screen or expired
                if (projectile['x'] > self.screen_width or projectile['x'] < 0 or
                    projectile['y'] > self.screen_height or projectile['y'] < 0 or
                    projectile['life'] <= 0):
                    self.projectiles.remove(projectile)

            # Move to returning phase after shoot duration
            if self.attack_timer >= self.shoot_duration:
                self.attack_phase = "returning"
                self.attack_timer = 0.0

        elif self.attack_phase == "returning":
            # Animate protagonist returning to initial position
            progress = min(1.0, self.attack_timer / self.return_duration)

            # Smooth interpolation
            smooth_progress = progress * progress * (3.0 - 2.0 * progress)

            self.protagonist_x = self.center_x + (self.initial_protagonist_x - self.center_x) * smooth_progress
            self.protagonist_y = self.center_y + (self.initial_protagonist_y - self.center_y) * smooth_progress

            if progress >= 1.0:
                # Attack complete - return to position and start rat turn
                self.protagonist_x = self.initial_protagonist_x
                self.protagonist_y = self.initial_protagonist_y
                self.combat_state = "menu"
                self.menu_visible = True
                self.start_rat_turn()  # Start rat's attack sequence

    def create_projectiles(self):
        """Create 3 projectiles from center position aimed at rat"""
        # Calculate direction to rat center (accounting for larger animated sprite)
        dx = self.enemy_x - (self.protagonist_x + 50)
        # Aim at center of animated rat sprite (much larger frame)
        current_rat_frame = self.rat_animation.get_current_frame()
        if current_rat_frame:
            rat_center_y = self.enemy_y + (current_rat_frame.get_height() * self.enemy_scale) // 2
        else:
            rat_center_y = self.enemy_y + 64  # Fallback
        dy = rat_center_y - (self.protagonist_y + 30)
        distance = (dx**2 + dy**2)**0.5

        for i in range(3):
            # Calculate velocity components to aim at rat
            base_speed = 180 + (i * 15)  # Slightly slower and more spread out
            vx = (dx / distance) * base_speed if distance > 0 else base_speed
            vy = (dy / distance) * base_speed if distance > 0 else 0

            projectile = {
                'x': self.protagonist_x + 50,
                'y': self.protagonist_y + 30 + (i * 8),  # More spread
                'vx': vx,  # Velocity components instead of just speed
                'vy': vy,
                'life': 3.0,  # Increased lifetime to reach the rat
                'delay': i * 0.2  # Add 0.2 second delay between projectiles
            }
            self.projectiles.append(projectile)

    def check_projectile_rat_collision(self, projectile):
        """Check if projectile hits the rat"""
        # Get current rat frame to determine size
        current_rat_frame = self.rat_animation.get_current_frame()
        if current_rat_frame:
            rat_width = int(current_rat_frame.get_width() * self.enemy_scale)
            rat_height = int(current_rat_frame.get_height() * self.enemy_scale)
        else:
            # Fallback size
            rat_width = int(64 * self.enemy_scale)
            rat_height = int(48 * self.enemy_scale)

        projectile_rect = pygame.Rect(projectile['x'], projectile['y'], 8, 4)
        rat_rect = pygame.Rect(self.enemy_x, self.enemy_y, rat_width, rat_height)

        collision = projectile_rect.colliderect(rat_rect)
        return collision

    def hit_rat(self):
        """Handle rat being hit by projectile"""
        # Don't allow hits if rat is already dead
        if self.rat_stats["hp"] <= 0:
            return

        # Each bullet deals 1 damage to enemy (fixed amount)
        bullet_damage = 1
        self.rat_stats["hp"] = max(0, self.rat_stats["hp"] - bullet_damage)

        # Increase anger by 5% (0.5 out of 10)
        self.protagonist_stats["anger"] = min(self.protagonist_stats["max_anger"],
                                             self.protagonist_stats["anger"] + 0.5)

        # Show damage number
        self.show_damage_number(f"-{bullet_damage}", "rat")

        # Check for victory
        if self.rat_stats["hp"] <= 0:
            self.start_victory_sequence()

    def show_damage_number(self, text, target):
        """Show damage number above target"""
        self.showing_damage = True
        self.damage_text = text
        self.damage_target = target
        self.damage_timer = 0.0

    def start_rat_turn(self):
        """Start the rat's turn with attack"""
        self.player_turn = False
        self.rat_attack_state = "banner"
        self.rat_attack_timer = 0.0
        # Play Row 2 attack animation during rat's turn
        self.rat_animation.play_animation('rat_attack')
        self.rat_animation_phase = "attacking"

    def update_rat_attack(self, dt):
        """Update rat attack sequence"""
        if self.rat_attack_state == "none":
            return

        self.rat_attack_timer += dt

        if self.rat_attack_state == "banner":
            # Show enemy attack banner for 2 seconds
            if self.rat_attack_timer >= self.banner_duration:
                self.rat_attack_state = "jumping"
                self.rat_attack_timer = 0.0

        elif self.rat_attack_state == "jumping":
            # Animate rat jumping to protagonist
            progress = min(1.0, self.rat_attack_timer / self.rat_jump_duration)
            smooth_progress = progress * progress * (3.0 - 2.0 * progress)

            target_x = self.protagonist_x - 30
            target_y = self.protagonist_y

            self.enemy_x = self.initial_enemy_x + (target_x - self.initial_enemy_x) * smooth_progress
            self.enemy_y = self.initial_enemy_y + (target_y - self.initial_enemy_y) * smooth_progress

            if progress >= 1.0:
                self.rat_attack_state = "attacking"
                self.rat_attack_timer = 0.0
                self.hit_protagonist()

        elif self.rat_attack_state == "attacking":
            # Brief attack animation
            if self.rat_attack_timer >= self.rat_attack_duration:
                self.rat_attack_state = "returning"
                self.rat_attack_timer = 0.0

        elif self.rat_attack_state == "returning":
            # Animate rat returning to original position
            progress = min(1.0, self.rat_attack_timer / self.rat_return_duration)
            smooth_progress = progress * progress * (3.0 - 2.0 * progress)

            current_x = self.protagonist_x - 30
            current_y = self.protagonist_y

            self.enemy_x = current_x + (self.initial_enemy_x - current_x) * smooth_progress
            self.enemy_y = current_y + (self.initial_enemy_y - current_y) * smooth_progress

            if progress >= 1.0:
                self.enemy_x = self.initial_enemy_x
                self.enemy_y = self.initial_enemy_y
                self.rat_attack_state = "none"
                # Switch to Row 3 waiting animation for protagonist's turn
                self.rat_animation.play_animation('waiting')
                self.rat_animation_phase = "waiting"
                self.player_turn = True  # Return to player's turn

    def hit_protagonist(self):
        """Handle protagonist being hit by enemy"""
        # Different damage based on enemy type
        if getattr(self, 'enemy_type', 'rat') == 'frog':
            # Frog deals 4 damage and creates poison cloud
            damage = 4
            self.protagonist_stats["hp"] = max(0, self.protagonist_stats["hp"] - damage)
            self.show_damage_number(f"-{damage}", "protagonist")
            self.create_poison_cloud()
        else:
            # Cockroach deals 3 damage (or default 3 for rat)
            damage = 3
            self.protagonist_stats["hp"] = max(0, self.protagonist_stats["hp"] - damage)
            self.show_damage_number(f"-{damage}", "protagonist")

    def create_poison_cloud(self):
        """Create a green poison cloud effect around the protagonist"""
        # Initialize poison cloud effect
        self.poison_cloud = {
            "active": True,
            "timer": 0.0,
            "duration": 2.0,  # Show for 2 seconds
            "particles": []
        }

        # Create poison cloud particles around protagonist
        for i in range(15):  # 15 poison particles
            particle = {
                "x": self.protagonist_x + random.randint(-30, 30),
                "y": self.protagonist_y + random.randint(-20, 20),
                "vx": random.randint(-20, 20),
                "vy": random.randint(-20, 20),
                "size": random.randint(3, 8),
                "alpha": 255
            }
            self.poison_cloud["particles"].append(particle)

    def update_poison_cloud(self, dt):
        """Update poison cloud particles"""
        self.poison_cloud["timer"] += dt

        # Update particle positions and fade
        for particle in self.poison_cloud["particles"]:
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["vy"] += 20 * dt  # Gravity effect
            # Fade out over time
            fade_progress = self.poison_cloud["timer"] / self.poison_cloud["duration"]
            particle["alpha"] = max(0, 255 * (1 - fade_progress))

        # Remove poison cloud when duration expires
        if self.poison_cloud["timer"] >= self.poison_cloud["duration"]:
            self.poison_cloud["active"] = False

    def start_victory_sequence(self):
        """Start the victory sequence"""
        self.victory_state = "victory_jump"
        self.victory_timer = 0.0
        self.jump_count = 0
        self.player_turn = True  # Stop rat attacks
        self.rat_attack_state = "none"
        self.menu_visible = False

    def update_victory_sequence(self, dt):
        """Update victory sequence"""
        if self.victory_state == "none":
            return

        self.victory_timer += dt

        if self.victory_state == "victory_jump":
            # Hero jumps 3 times
            if self.victory_timer >= self.jump_duration:
                self.jump_count += 1
                self.victory_timer = 0.0

                if self.jump_count >= 3:
                    self.victory_state = "victory_text"
                    self.victory_timer = 0.0

        elif self.victory_state == "victory_text":
            # Show victory text for 2 seconds
            if self.victory_timer >= self.text_duration:
                self.victory_state = "fading"
                self.victory_timer = 0.0

        elif self.victory_state == "fading":
            # Fade out
            if self.victory_timer >= self.fade_duration:
                # Victory complete - could return to main menu or next scene
                self.victory_state = "complete"  # Stop the victory sequence

    def update_heal_effect(self, dt):
        """Update heal effect display"""
        if hasattr(self, 'showing_heal') and self.showing_heal:
            self.heal_effect_timer += dt
            if self.heal_effect_timer >= self.heal_effect_duration:
                self.showing_heal = False
                self.combat_state = "menu"
                self.menu_visible = True
                self.start_rat_turn()  # Start rat's turn after healing

    def render(self, screen):
        # Draw background
        screen.blit(self.background, (0, 0))

        # Draw scene number
        scene_font = pygame.font.Font(None, 36)
        scene_text = scene_font.render("FIGHT 0", True, (255, 255, 255))
        scene_rect = scene_text.get_rect()
        scene_rect.topright = (self.screen_width - 20, 20)

        # Draw scene background
        scene_bg_rect = scene_rect.inflate(10, 5)
        pygame.draw.rect(screen, (0, 0, 0, 180), scene_bg_rect)
        screen.blit(scene_text, scene_rect)

        # Draw location text
        font = pygame.font.Font(None, 24)
        location_text = font.render("Fight Scene 0 - Battle Arena", True, (255, 255, 255))
        text_rect = location_text.get_rect()
        text_rect.topleft = (10, 10)

        # Draw text background
        bg_rect = text_rect.inflate(10, 5)
        pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
        screen.blit(location_text, text_rect)

        # Draw protagonist (repositioned to avoid menu overlap)
        protagonist_sprite = self.protagonist_animation.get_current_frame()
        if protagonist_sprite:
            if self.protagonist_scale != 1.0:
                scaled_width = int(protagonist_sprite.get_width() * self.protagonist_scale)
                scaled_height = int(protagonist_sprite.get_height() * self.protagonist_scale)
                protagonist_sprite = pygame.transform.scale(protagonist_sprite, (scaled_width, scaled_height))

            # Apply jumping animation during victory
            jump_y_offset = 0
            if self.victory_state == "victory_jump":
                # Simple jump animation
                jump_phase = (self.victory_timer / self.jump_duration) * 2 * 3.14159  # Full sine wave per jump
                jump_y_offset = -abs(int(20 * __import__('math').sin(jump_phase)))  # Jump up to 20 pixels

            screen.blit(protagonist_sprite, (int(self.protagonist_x), int(self.protagonist_y + jump_y_offset)))

        # Draw turn indicator (yellow triangle above current turn character)
        if self.player_turn:
            # Triangle above protagonist
            triangle_x = int(self.protagonist_x + (scaled_width // 2) if protagonist_sprite else self.protagonist_x + 32)
            triangle_y = int(self.protagonist_y - 20)
            triangle_points = [
                (triangle_x, triangle_y),
                (triangle_x - 8, triangle_y - 12),
                (triangle_x + 8, triangle_y - 12)
            ]
            pygame.draw.polygon(screen, self.turn_indicator_color, triangle_points)
        else:
            # Triangle above rat (rat's turn) - use animated rat frame for size
            current_rat_frame = self.rat_animation.get_current_frame()
            if current_rat_frame:
                rat_width = int(current_rat_frame.get_width() * self.enemy_scale)
            else:
                rat_width = 32
            triangle_x = int(self.enemy_x + (rat_width // 2))
            triangle_y = int(self.enemy_y - 20)
            triangle_points = [
                (triangle_x, triangle_y),
                (triangle_x - 8, triangle_y - 12),
                (triangle_x + 8, triangle_y - 12)
            ]
            pygame.draw.polygon(screen, self.turn_indicator_color, triangle_points)

        # Draw animated enemies (with blinking/fading if dead)
        if self.dual_enemies:
            # Draw both enemies
            for enemy_name, enemy in self.enemies.items():
                current_frame = enemy["animation"].get_current_frame()
                if current_frame:
                    if self.enemy_scale != 1.0:
                        scaled_width = int(current_frame.get_width() * self.enemy_scale)
                        scaled_height = int(current_frame.get_height() * self.enemy_scale)
                        scaled_enemy = pygame.transform.scale(current_frame, (scaled_width, scaled_height))
                    else:
                        scaled_enemy = current_frame

                    # Apply effects if enemy is dead
                    if enemy["hp"] <= 0:
                        if self.victory_state == "victory_jump":
                            # Blinking effect during jump sequence
                            blink_speed = 10
                            if int(self.victory_timer * blink_speed) % 2 == 0:
                                blinking_enemy = scaled_enemy.copy()
                                blinking_enemy.set_alpha(100)
                                screen.blit(blinking_enemy, (int(enemy["x"]), int(enemy["y"])))
                        elif self.victory_state == "victory_text":
                            # Fade out during text phase
                            fade_progress = self.victory_timer / self.text_duration
                            alpha = int(255 * (1.0 - fade_progress))
                            fading_enemy = scaled_enemy.copy()
                            fading_enemy.set_alpha(alpha)
                            screen.blit(fading_enemy, (int(enemy["x"]), int(enemy["y"])))
                    else:
                        # Draw normally
                        screen.blit(scaled_enemy, (int(enemy["x"]), int(enemy["y"])))
        else:
            # Single enemy drawing
            current_rat_frame = self.rat_animation.get_current_frame()
            if current_rat_frame:
                if self.enemy_scale != 1.0:
                    scaled_width = int(current_rat_frame.get_width() * self.enemy_scale)
                    scaled_height = int(current_rat_frame.get_height() * self.enemy_scale)
                    scaled_rat = pygame.transform.scale(current_rat_frame, (scaled_width, scaled_height))
                else:
                    scaled_rat = current_rat_frame

                # Apply effects if rat is dead
                if self.rat_stats["hp"] <= 0:
                    if self.victory_state == "victory_jump":
                        # Blinking effect during jump sequence
                        blink_speed = 10  # Blinks per second
                        if int(self.victory_timer * blink_speed) % 2 == 0:
                            # Make rat transparent (blinking)
                            blinking_rat = scaled_rat.copy()
                            blinking_rat.set_alpha(100)
                            screen.blit(blinking_rat, (int(self.enemy_x), int(self.enemy_y)))
                    elif self.victory_state == "victory_text":
                        # Fade out during text phase
                        fade_progress = self.victory_timer / self.text_duration
                        alpha = int(255 * (1.0 - fade_progress))
                        fading_rat = scaled_rat.copy()
                        fading_rat.set_alpha(max(0, alpha))
                        screen.blit(fading_rat, (int(self.enemy_x), int(self.enemy_y)))
                    # Don't draw rat during fading phase
                else:
                    # Normal rat drawing
                    screen.blit(scaled_rat, (int(self.enemy_x), int(self.enemy_y)))

        # Draw character labels
        label_font = pygame.font.Font(None, 24)

        # Protagonist label
        protag_label = label_font.render("Protagonist", True, (255, 255, 255))
        protag_rect = protag_label.get_rect()
        protag_rect.centerx = int(self.protagonist_x + (protagonist_sprite.get_width() * self.protagonist_scale) // 2) if protagonist_sprite else int(self.protagonist_x + 32)
        protag_rect.bottom = int(self.protagonist_y) - 5

        # Draw label background
        label_bg = protag_rect.inflate(6, 2)
        pygame.draw.rect(screen, (0, 0, 0, 128), label_bg)
        screen.blit(protag_label, protag_rect)

        # Enemy label
        enemy_label = label_font.render("Rat Enemy", True, (255, 255, 255))
        enemy_rect = enemy_label.get_rect()
        if current_rat_frame and self.enemy_scale != 1.0:
            enemy_rect.centerx = int(self.enemy_x + (scaled_rat.get_width()) // 2)
        elif current_rat_frame:
            enemy_rect.centerx = int(self.enemy_x + (current_rat_frame.get_width()) // 2)
        else:
            enemy_rect.centerx = int(self.enemy_x + 32)
        enemy_rect.bottom = int(self.enemy_y) - 5

        # Draw label background
        label_bg = enemy_rect.inflate(6, 2)
        pygame.draw.rect(screen, (0, 0, 0, 128), label_bg)
        screen.blit(enemy_label, enemy_rect)

        # Draw rat health counter
        health_text = f"HP: {self.rat_stats['hp']}/{self.rat_stats['max_hp']}"
        health_color = (255, 255, 255) if self.rat_stats["hp"] > 0 else (255, 100, 100)  # Red if dead
        health_label = label_font.render(health_text, True, health_color)
        health_rect = health_label.get_rect()
        health_rect.centerx = enemy_rect.centerx
        health_rect.top = enemy_rect.bottom + 2  # Just below the enemy label

        # Draw health label background
        health_bg = health_rect.inflate(6, 2)
        pygame.draw.rect(screen, (0, 0, 0, 128), health_bg)
        screen.blit(health_label, health_rect)

        # Draw combat state indicator
        if self.combat_state == "attacking":
            attack_font = pygame.font.Font(None, 36)
            attack_text = attack_font.render("ATTACKING", True, (255, 255, 0))
            attack_rect = attack_text.get_rect()
            attack_rect.centerx = self.screen_width // 2
            attack_rect.top = 20

            # Draw border background
            border_rect = attack_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 180), border_rect)
            pygame.draw.rect(screen, (255, 255, 0), border_rect, 2)
            screen.blit(attack_text, attack_rect)

        # Draw projectiles
        for projectile in self.projectiles:
            alpha = max(0, min(255, int(255 * (projectile['life'] / 3.0))))  # Normalize based on max life
            projectile_surface = pygame.Surface((8, 4), pygame.SRCALPHA)
            pygame.draw.ellipse(projectile_surface, (255, 255, 0), (0, 0, 8, 4))
            projectile_surface.set_alpha(alpha)
            screen.blit(projectile_surface, (int(projectile['x']), int(projectile['y'])))

        # Draw heal effect
        if hasattr(self, 'showing_heal') and self.showing_heal:
            heal_font = pygame.font.Font(None, 32)
            heal_text = heal_font.render("+50", True, (255, 255, 0))
            heal_x = int(self.protagonist_x + 40)
            heal_y = int(self.protagonist_y - 30)
            screen.blit(heal_text, (heal_x, heal_y))

        # Draw damage numbers
        if self.showing_damage:
            damage_font = pygame.font.Font(None, 32)
            if self.damage_target == "rat":
                damage_x = int(self.enemy_x + 40)
                damage_y = int(self.enemy_y - 30)
                color = (255, 100, 100)  # Red for damage to enemy
            else:  # protagonist
                damage_x = int(self.protagonist_x + 40)
                damage_y = int(self.protagonist_y - 30)
                color = (255, 100, 100)  # Red for damage to protagonist

            damage_text = damage_font.render(self.damage_text, True, color)
            screen.blit(damage_text, (damage_x, damage_y))

        # Draw rat attack banner
        if self.rat_attack_state == "banner":
            banner_font = pygame.font.Font(None, 48)
            attack_name = getattr(self, 'enemy_attack', 'CLAWS')  # Use enemy attack name
            banner_text = banner_font.render(attack_name, True, (255, 0, 0))
            banner_rect = banner_text.get_rect()
            banner_rect.centerx = self.screen_width // 2
            banner_rect.top = 80

            # Draw banner background
            banner_bg_rect = banner_rect.inflate(30, 15)
            pygame.draw.rect(screen, (0, 0, 0, 200), banner_bg_rect)
            pygame.draw.rect(screen, (255, 0, 0), banner_bg_rect, 3)
            screen.blit(banner_text, banner_rect)

        # Draw poison cloud effect
        if self.poison_cloud["active"]:
            self.draw_poison_cloud(screen)

        # Draw fight menu (lower left corner) - only during player's turn
        if self.menu_visible and self.player_turn:
            self.draw_fight_menu(screen)

        # Draw stats table (next to menu)
        self.draw_stats_table(screen)

        # Draw controls
        controls_font = pygame.font.Font(None, 20)
        if self.player_turn and self.menu_visible:
            controls_text = controls_font.render("Arrow Keys: Navigate | Enter: Select | ESC: Back/Quit", True, (200, 200, 200))
        elif not self.player_turn:
            if self.rat_attack_state == "banner":
                controls_text = controls_font.render("Rat prepares to attack...", True, (200, 200, 200))
            elif self.rat_attack_state in ["jumping", "attacking", "returning"]:
                controls_text = controls_font.render("Rat is attacking!", True, (200, 200, 200))
            else:
                controls_text = controls_font.render("Rat's Turn | Press R to reset to player turn", True, (200, 200, 200))
        else:
            controls_text = controls_font.render("Combat in progress...", True, (200, 200, 200))
        controls_rect = controls_text.get_rect()
        controls_rect.bottomleft = (10, self.screen_height - 10)
        screen.blit(controls_text, controls_rect)

        # Draw victory text and fade
        if self.victory_state == "victory_text":
            # Victory text background
            text_bg = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            text_bg.fill((0, 0, 0, 150))
            screen.blit(text_bg, (0, 0))

            # Victory text
            victory_font = pygame.font.Font(None, 64)
            victory_text = victory_font.render("VICTORY!", True, (255, 255, 0))
            victory_rect = victory_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
            screen.blit(victory_text, victory_rect)

            # Rewards text
            reward_font = pygame.font.Font(None, 48)
            potion_text = reward_font.render("Potion 1", True, (255, 255, 255))
            potion_rect = potion_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
            screen.blit(potion_text, potion_rect)

            gold_text = reward_font.render("Gold 23", True, (255, 215, 0))
            gold_rect = gold_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 70))
            screen.blit(gold_text, gold_rect)

        elif self.victory_state == "fading":
            # Fade to black
            fade_progress = self.victory_timer / self.fade_duration
            fade_alpha = int(255 * fade_progress)
            fade_surface = pygame.Surface((self.screen_width, self.screen_height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))

        # Draw quit overlay
        self.quit_overlay.render(screen)

    def draw_poison_cloud(self, screen):
        """Draw the poison cloud effect"""
        for particle in self.poison_cloud["particles"]:
            if particle["alpha"] > 0:
                # Create a surface for the particle with alpha
                particle_surface = pygame.Surface((particle["size"] * 2, particle["size"] * 2), pygame.SRCALPHA)

                # Draw green circle with alpha
                green_color = (0, 255, 100, int(particle["alpha"]))
                pygame.draw.circle(particle_surface, green_color,
                                 (particle["size"], particle["size"]),
                                 particle["size"])

                # Blit to screen
                screen.blit(particle_surface, (particle["x"] - particle["size"], particle["y"] - particle["size"]))

    def draw_fight_menu(self, screen):
        """Draw the fight menu in lower left corner"""
        # Menu background (semi-transparent)
        menu_surface = pygame.Surface((self.menu_width, self.menu_height), pygame.SRCALPHA)
        pygame.draw.rect(menu_surface, (0, 0, 0, 180), (0, 0, self.menu_width, self.menu_height))
        pygame.draw.rect(menu_surface, (255, 255, 255), (0, 0, self.menu_width, self.menu_height), 2)
        screen.blit(menu_surface, (self.menu_x, self.menu_y))

        font = pygame.font.Font(None, 28)

        if not self.in_submenu:
            # Draw main menu
            for i, item in enumerate(self.main_menu_items):
                y_pos = self.menu_y + 20 + (i * 30)

                # Determine text color
                if not item["enabled"]:
                    color = (128, 128, 128)  # Grey for disabled
                elif i == self.selected_menu_item:
                    color = (255, 255, 0)  # Yellow for selected
                else:
                    color = (255, 255, 255)  # White for normal

                # Draw selection indicator
                if i == self.selected_menu_item and item["enabled"]:
                    pygame.draw.polygon(screen, (255, 255, 0), [
                        (self.menu_x + 10, y_pos + 10),
                        (self.menu_x + 18, y_pos + 6),
                        (self.menu_x + 18, y_pos + 14)
                    ])

                text = font.render(item["text"], True, color)
                screen.blit(text, (self.menu_x + 30, y_pos))
        else:
            # Draw item submenu
            title_font = pygame.font.Font(None, 24)
            title_text = title_font.render("Items:", True, (255, 255, 255))
            screen.blit(title_text, (self.menu_x + 10, self.menu_y + 10))

            for i, item in enumerate(self.item_submenu):
                y_pos = self.menu_y + 40 + (i * 30)

                # Check if item is available
                available = item["count"] > 0

                # Selection indicator (only if available)
                if i == self.submenu_selected and available:
                    pygame.draw.polygon(screen, (255, 255, 0), [
                        (self.menu_x + 10, y_pos + 10),
                        (self.menu_x + 18, y_pos + 6),
                        (self.menu_x + 18, y_pos + 14)
                    ])

                # Draw potion icon (greyed out if not available)
                potion_icon = self.create_potion_icon()
                if not available:
                    # Make icon grey
                    grey_icon = potion_icon.copy()
                    grey_icon.fill((128, 128, 128), special_flags=pygame.BLEND_MULT)
                    screen.blit(grey_icon, (self.menu_x + 25, y_pos + 2))
                else:
                    screen.blit(potion_icon, (self.menu_x + 25, y_pos + 2))

                # Item text (grey if not available)
                if not available:
                    color = (128, 128, 128)  # Grey
                elif i == self.submenu_selected:
                    color = (255, 255, 0)  # Yellow selected
                else:
                    color = (255, 255, 255)  # White

                text = font.render(item["text"], True, color)
                screen.blit(text, (self.menu_x + 45, y_pos))

    def draw_stats_table(self, screen):
        """Draw the stats table next to the menu"""
        # Table background (transparent with border)
        table_surface = pygame.Surface((self.stats_width, self.stats_height), pygame.SRCALPHA)
        pygame.draw.rect(table_surface, (0, 0, 0, 120), (0, 0, self.stats_width, self.stats_height))
        pygame.draw.rect(table_surface, (255, 255, 255), (0, 0, self.stats_width, self.stats_height), 1)
        screen.blit(table_surface, (self.stats_x, self.stats_y))

        font = pygame.font.Font(None, 24)

        # Header row
        headers = ["Name", "HP", "MP", "Anger"]
        col_width = self.stats_width // 4

        for i, header in enumerate(headers):
            text = font.render(header, True, (255, 255, 255))
            x_pos = self.stats_x + (i * col_width) + 5
            screen.blit(text, (x_pos, self.stats_y + 5))

        # Stats row
        stats = self.protagonist_stats
        y_pos = self.stats_y + 30

        # Name
        name_text = font.render(stats["name"], True, (255, 255, 255))
        screen.blit(name_text, (self.stats_x + 5, y_pos))

        # HP
        hp_text = font.render(str(stats["hp"]), True, (255, 255, 255))
        screen.blit(hp_text, (self.stats_x + col_width + 5, y_pos))

        # MP
        mp_text = font.render(str(stats["mp"]), True, (255, 255, 255))
        screen.blit(mp_text, (self.stats_x + (2 * col_width) + 5, y_pos))

        # Anger bar
        anger_x = self.stats_x + (3 * col_width) + 5
        anger_width = col_width - 10
        anger_height = 15

        # Gray background bar
        pygame.draw.rect(screen, (128, 128, 128), (anger_x, y_pos + 2, anger_width, anger_height))

        # Blue fill based on anger level
        if stats["anger"] > 0:
            fill_width = int((stats["anger"] / stats["max_anger"]) * anger_width)
            pygame.draw.rect(screen, (0, 100, 255), (anger_x, y_pos + 2, fill_width, anger_height))

        # Bar border
        pygame.draw.rect(screen, (255, 255, 255), (anger_x, y_pos + 2, anger_width, anger_height), 1)

    def cleanup(self):
        """Clean up resources when fight0 state is destroyed"""
        pass