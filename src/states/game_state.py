from abc import ABC, abstractmethod

class GameState(ABC):
    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def render(self, screen):
        pass

class GameStateManager:
    def __init__(self):
        self.states = []
        self.quit = False

    def push_state(self, state):
        self.states.append(state)

    def pop_state(self):
        if self.states:
            return self.states.pop()
        return None

    def change_state(self, state):
        self.states.clear()
        self.states.append(state)

    def handle_event(self, event):
        if self.states:
            self.states[-1].handle_event(event)

    def update(self, dt):
        if self.states:
            self.states[-1].update(dt)

    def render(self, screen):
        if self.states:
            self.states[-1].render(screen)

    def should_quit(self):
        return self.quit or len(self.states) == 0

    def quit_game(self):
        self.quit = True