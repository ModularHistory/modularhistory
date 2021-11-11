from core.environment import TESTING

if TESTING:
    from .fakers import HistoricDateTimeProvider
