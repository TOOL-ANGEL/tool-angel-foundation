"""
Plugin Lifecycle.
"""


class PluginLifecycle:
    """
    Manage plugin lifecycle state.
    """

    CREATED = "created"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    STARTED = "started"
    STOPPED = "stopped"

    def __init__(self):

        self.state = self.CREATED

    def set_state(self, state):

        self.state = state

    def get_state(self):

        return self.state