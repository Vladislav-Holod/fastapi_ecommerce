from datetime import datetime

from sqlalchemy import String, Boolean, Integer, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.database import Base


class Reviews(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'), nullable=False)
    comment: Mapped[String | None] = mapped_column(String(200))
    comment_date: Mapped[datetime] = mapped_column(Date, default=datetime.now())
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    user: Mapped['User'] = relationship('User', back_populates='reviews')
    products: Mapped['Product']= relationship('Product',back_populates='reviews')
