import enum


class NoteFieldType(str, enum.Enum):
    text = "text"
    rich_text = "rich_text"
    image = "image"
    audio = "audio"
    furigana = "furigana"
    json = "json"


class MediaType(str, enum.Enum):
    image = "image"
    audio = "audio"


class CardStatus(str, enum.Enum):
    new = "new"
    learning = "learning"
    review = "review"
    suspended = "suspended"
