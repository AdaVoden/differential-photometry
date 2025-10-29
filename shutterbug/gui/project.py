import logging

import json


class ShutterbugProject:
    """Save and load functionality for project"""

    @staticmethod
    def save(project_path, state):
        with open(project_path, "w") as f:
            json.dump(state, f, indent=2)

    @staticmethod
    def load(project_path, main_window):
        with open(project_path, "r") as f:
            state = json.load(f)

        main_window.set_state(state)
