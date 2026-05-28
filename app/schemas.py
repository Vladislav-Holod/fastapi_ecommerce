from pydantic import BaseModel, Field, ConfigDict, EmailStr
from decimal import Decimal
from datetime import datetime

class CategoryCreate(BaseModel):
    """
    Модель для создания и обновления категории.
    Используется в POST и PUT запросах.
    """
    name: str = Field(..., min_length=3, max_length=50,
                      description="Название категории (3-50 символов)")

    parent_id: int | None = Field(..., description="ID родительской категории, если есть")


class Category(CategoryCreate):
    """
    Модель для ответа с данными категории.
    Используется в Get - запросах.
    """
    id: int = Field(..., description="Уникальный идентификатор категории")
    is_active: bool = Field(..., description='Активность категории')

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    """
    Модель для создания и обновления товара.
    Используется в POST и PUT запросах.
    """
    name: str = Field(..., min_length=3, max_length=100,
                      description="Название товара (3-100 символов)")
    description: str | None = Field(None, max_length=500,
                                    description="Описание товара (до 500 символов)")
    price: Decimal = Field(..., gt=0, description="Цена товара (больше 0)", decimal_places=2)
    image_url: str | None = Field(None, max_length=200, description="URL изображения товара")
    stock: int = Field(..., ge=0, description="Количество товара на складе (0 или больше)")
    category_id: int = Field(..., description="ID категории, к которой относится товар")


class Product(ProductCreate):
    """
    Модель для ответа с данными товара.
    Используется в GET-запросах.
    """
    id: int = Field(..., description="Уникальный идентификатор товара")
    is_active: bool = Field(..., description="Активность товара")

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Модель для создания пользователя
    """
    email: EmailStr = Field(description='Email пользователя')
    password: str = Field(min_length=8, description='Пароль (минимум 8 символов)')
    role: str = Field(default='buyer', pattern="^(buyer|seller)$", description="Роль: 'buyer' или 'seller'")


class User(BaseModel):
    """
    Модель для ответа с данными пользователя
    используется в GET запросах
    """
    id: int =Field(description='Уникальный идентификатор пользователя')
    email: EmailStr = Field(description='Email пользователя')
    is_active: bool = Field(description='Активность пользователя ')
    role: str = Field(default='buyer', pattern="^(buyer|seller)$", description="Роль: 'buyer' или 'seller'")
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    """
    Модель для REFRESH jwt токена
    """
    refresh_token: str = Field('Refresh JWT Tokens')


class ReviewsCrete(BaseModel):
    """
    Модель для создания отзыва
    """
    product_id: int = Field(description='Уникальный идентификатор продукта')
    comment: str | None =Field(description='Содержания отзыва (комментарий) можно без ')
    grade: int = Field(ge=1, le=5,description='Оценка отзыва от 1 до 5')

class Review(BaseModel):
    """
    Модель для ответа с данными отзыва
    используется для GET запросах
    """
    id: int = Field(description='Уникальный идентификатор отзыва')
    user_id: int = Field(description='Уникальный идентификатор юзера')
    product_id: int = Field(description='Уникальный идентификатор продукта')
    comment: str = Field(description='Содержания отзыва (комментарий)')
    comment_date: datetime = Field(description='Время создания отзыва')
    grade: int = Field(description='Оценка отзыва от 1 до 5')
    is_active: bool = Field('Активность отзыва')