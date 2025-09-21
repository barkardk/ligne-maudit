import random
from enum import Enum

class ActionType(Enum):
    ATTACK = "attack"
    DEFEND = "defend"
    ITEM = "item"
    SKILL = "skill"

class Character:
    def __init__(self, name, max_hp, attack, defense, speed):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.is_alive = True
        self.is_defending = False

    def take_damage(self, damage):
        actual_damage = max(1, damage - (self.defense // 2 if not self.is_defending else self.defense))
        self.hp = max(0, self.hp - actual_damage)
        if self.hp <= 0:
            self.is_alive = False
        return actual_damage

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def attack_enemy(self, target):
        base_damage = self.attack + random.randint(-3, 3)
        return target.take_damage(base_damage)

    def defend(self):
        self.is_defending = True

    def reset_turn_effects(self):
        self.is_defending = False

class Player(Character):
    def __init__(self, name="Soldier", job="Infantry"):
        super().__init__(name, 80, 15, 8, 12)  # max_hp, attack, defense, speed
        self.job = job
        self.exp = 0
        self.level = 1

class Enemy(Character):
    def __init__(self, name, hp, attack, defense, speed, exp_reward=10):
        super().__init__(name, hp, attack, defense, speed)
        self.exp_reward = exp_reward

    def choose_action(self, targets):
        action = random.choice([ActionType.ATTACK, ActionType.DEFEND])
        if action == ActionType.ATTACK and targets:
            return action, random.choice([t for t in targets if t.is_alive])
        return action, None

class GermanSoldier(Enemy):
    def __init__(self):
        super().__init__("German Soldier", hp=45, attack=12, defense=6, speed=10, exp_reward=15)

class GermanOfficer(Enemy):
    def __init__(self):
        super().__init__("German Officer", hp=70, attack=16, defense=10, speed=8, exp_reward=25)