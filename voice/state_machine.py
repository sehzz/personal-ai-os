from enum import Enum
import time
from lib.log import logger

log = logger.get_logger()

class State(Enum):
    SLEEPING  = 0
    LISTENING  = 1
    PROCESSING = 2
    SPEAKING = 3
    UNKNOWN = 4


class StateMachine:
    def __init__(self):
        self.state = State.SLEEPING
        self.last_sleeping_at = 0

    def transition(self, new_state):
        if isinstance(new_state, State):
            old_state = self.state
            self.state = new_state
            if new_state == State.SLEEPING:
                self.last_sleeping_at = time.time()
            log.info(f"Transitioned from {old_state.name} to state: {self.state.name}")
        else:
            raise ValueError("Invalid state transition")
    
    @property
    def current_state(self):
        return self.state
    

if __name__ == "__main__":
    sm = StateMachine()
    print(f"Initial state: {sm.current_state.name}")
    sm.transition(State.LISTENING)
    sm.transition(State.PROCESSING)
    sm.transition(State.SPEAKING)