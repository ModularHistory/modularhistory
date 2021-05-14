from enum import Enum


class OccurrenceTypes(Enum):
    OCCURRENCE = 0
    BIRTH = 1
    DEATH = 2
    PUBLICATION = 3
    VERBALIZATION = 4


OCCURRENCE_TYPES = (
    (OccurrenceTypes.OCCURRENCE.value, 'Occurrence (default)'),
    (OccurrenceTypes.BIRTH.value, 'Birth'),
    (OccurrenceTypes.DEATH.value, 'Death'),
    (OccurrenceTypes.PUBLICATION.value, 'Publication'),
    (OccurrenceTypes.VERBALIZATION.value, 'Verbalization'),
)
