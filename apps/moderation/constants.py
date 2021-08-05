from aenum import Constant


class ModerationStatus(Constant):
    """."""

    PENDING = 0
    APPROVED = 1
    REJECTED = 2


class DraftState(Constant):
    """."""

    DRAFT = 0
    READY = 1
