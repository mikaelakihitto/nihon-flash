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


class LearningStage(str, enum.Enum):
    curto_prazo = "curto_prazo"
    transicao = "transicao"
    consolidacao = "consolidacao"
    longo_prazo = "longo_prazo"
    memoria_estavel = "memoria_estavel"
