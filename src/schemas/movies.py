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
        from_attributes = True  # Дозволяє створювати схему з об'єктів SQLAlchemy


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
    # ЗМІНЕНО: Використовуємо MovieStatusEnum безпосередньо
    status: MovieStatusEnum
    budget: float = Field(..., ge=0)
    revenue: float = Field(..., ge=0)
    # ЗМІНЕНО: Якщо тести використовують "US" (alpha-2), то змініть max_length на 2
    # Якщо ви хочете використовувати alpha-3, тоді тести мають бути змінені на "USA"
    country: str = Field(..., min_length=2, max_length=2)  # ЗМІНЕНО НА 2
    genres: List[str] = Field(default_factory=list)
    actors: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)

    @field_validator("date")
    def date_not_too_far_in_future(cls, v):
        # Якщо ви вже маєте цю валідацію в роутері, то її можна прибрати звідси,
        # щоб уникнути дублювання, але тут вона працює.
        if v > date.today().replace(year=date.today().year + 1):
            raise ValueError("date cannot be more than one year in the future")
        return v

    # `@field_validator("status")` тепер не потрібен, якщо використовується MovieStatusEnum
    # Pydantic автоматично валідуватиме, чи значення відповідає перерахуванню.


class MovieDetailSchema(BaseModel):
    """
    Схема для детальної інформації про фільм.
    """

    id: int
    name: str
    date: date
    score: float
    overview: str
    status: str
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
    # ЗМІНЕНО: Використовуємо Optional[MovieStatusEnum]
    status: Optional[MovieStatusEnum] = None
    budget: Optional[float] = Field(None, ge=0)
    revenue: Optional[float] = Field(None, ge=0)
