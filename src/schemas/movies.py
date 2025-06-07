from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator

from database.models import MovieStatusEnum


# --- Допоміжні схеми для пов'язаних сутностей ---


class CountrySchema(BaseModel):
    id: int
    code: str
    name: Optional[str] = None

    class Config:
        from_attributes = True


class GenreSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ActorSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class LanguageSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# --- Схеми для кінцевих точок Movies ---


class MovieListItemSchema(BaseModel):
    """
    Схема для відображення фільму в списку.
    """

    id: int
    name: str
    date: date
    score: float
    overview: str

    class Config:
        from_attributes = True


class MovieListResponseSchema(BaseModel):
    """
    Схема для відповіді на запит списку фільмів з пагінацією.
    """

    movies: List[MovieListItemSchema]
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int
    total_items: int


class MovieCreateSchema(BaseModel):
    """
    Схема для створення нового фільму.
    """

    name: str = Field(..., max_length=255)
    date: date
    score: float = Field(..., ge=0, le=100)
    overview: str
    status: MovieStatusEnum  # Використовуємо MovieStatusEnum
    budget: float = Field(..., ge=0)
    revenue: float = Field(..., ge=0)
    # ЗМІНЕНО: max_length=2 для ISO 3166-1 alpha-2 кодів країн
    country: str = Field(..., min_length=2, max_length=2)
    genres: List[str] = Field(default_factory=list)
    actors: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)

    @field_validator("date")
    def date_not_too_far_in_future(cls, v):
        # Якщо ви вже маєте цю валідацію в роутері, то її можна прибрати звідси,
        # щоб уникнути дублювання, але тут вона працює.
        # Можливо, краще залишити її в схемі, оскільки це валідація даних, а не бізнес-логіка роутера.
        if v > date.today().replace(year=date.today().year + 1):
            raise ValueError("Date cannot be more than one year in the future.")
        return v


class MovieDetailSchema(BaseModel):
    """
    Схема для детальної інформації про фільм.
    """

    id: int
    name: str
    date: date
    score: float
    overview: str
    status: MovieStatusEnum  # ЗМІНЕНО: Використовуємо MovieStatusEnum тут теж
    budget: float
    revenue: float
    country: Optional[CountrySchema] = None
    genres: List[GenreSchema]
    actors: List[ActorSchema]
    languages: List[LanguageSchema]

    class Config:
        from_attributes = True


class MovieUpdateSchema(BaseModel):
    """
    Схема для часткового оновлення фільму.
    """

    name: Optional[str] = Field(None, max_length=255)
    date: Optional[date] = None
    score: Optional[float] = Field(None, ge=0, le=100)
    overview: Optional[str] = None
    status: Optional[MovieStatusEnum] = None  # Використовуємо MovieStatusEnum
    budget: Optional[float] = Field(None, ge=0)
    revenue: Optional[float] = Field(None, ge=0)

    # Optional: Додайте валідатор для 'date' тут, якщо він може оновлюватися,
    # і ви хочете зберегти логіку "не більше ніж на рік у майбутнє".
    @field_validator("date")
    def date_not_too_far_in_future_update(cls, v):
        if v is not None and v > date.today().replace(year=date.today().year + 1):
            raise ValueError("Updated date cannot be more than one year in the future.")
        return v
