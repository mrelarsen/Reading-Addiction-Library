from enum import Enum

class ReadingStatus(Enum):
    DOWNLOADED = 1
    READING = 2
    COMPLETED = 3
    SHOULD_REREAD = 4