from busy_beaver.exceptions import (
    EventEmitterEventAlreadyRegistered,
    EventEmitterEventNotRegistered,
)


class EventEmitter:
    def __init__(self):
        self.registered_events = {}

    def on(self, event, func=None):
        """Pass in a function or use as a decorator"""
        if event in self.registered_events:
            raise EventEmitterEventAlreadyRegistered(f"{event} already registered")

        def _on(f):
            self.registered_events[event] = f
            return f

        if func is None:
            return _on
        else:
            return _on(func)

    def emit(self, _event, *args, default=None, **kwargs):
        if _event not in self.registered_events:
            if not default:
                raise EventEmitterEventNotRegistered(
                    f"{_event} has not been registered"
                )
            _event = default

        func = self.registered_events[_event]
        return func(*args, **kwargs)
