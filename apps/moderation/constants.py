from aenum import Constant


class ModerationStatus(Constant):
    """."""

    REJECTED = 0
    PENDING = 1
    APPROVED = 2
    MERGED = 3


class DraftState(Constant):
    """."""

    DRAFT = 0
    READY = 1
