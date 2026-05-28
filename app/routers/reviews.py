from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from app.models import User as UserModel
from app.models import Product as ProductModel
from app.models import Reviews as ReviewsModel

from app.schemas import ReviewsCrete, Review
from app.db_depends import get_async_db
from app.auth import (get_current_seller,
                      get_current_admin,
                      get_current_buyer,
                      get_current_user)

router = APIRouter(prefix='/reviews',
                   tags=['reviews'])




@router.get('/', response_model=list[Review], status_code=status.HTTP_200_OK)
async def get_all_reviews(db: AsyncSession = Depends(get_async_db)):
    """
    GET /reviews/ — Получение всех отзывов
    """
    stmt_reviews = (select(ReviewsModel).
                    where(ReviewsModel.is_active == True))

    reviews = (await db.scalars(stmt_reviews)).all()
    return reviews

@router.post('/',response_model=Review,status_code=status.HTTP_201_CREATED)
async def create_reviews(reviews:ReviewsCrete,
                         db:AsyncSession = Depends(get_async_db),
                         current_user = Depends(get_current_buyer)):
    """
    POST /reviews/ — Добавление отзыва
    """
    stmt_product = (select(ProductModel).
                    where(ProductModel.id == reviews.product_id,
                          ProductModel.is_active == True))
    product = (await db.scalars(stmt_product)).first()
    if product is None:
        raise HTTPException(status_code=404,detail='Not Found')
    db_reviews= ReviewsModel(**reviews.model_dump(),
                             user_id=current_user.id)
    db.add(db_reviews,)
    await db.refresh(product)
    await db.commit()
    await update_product_rating(db,reviews.product_id)
    return db_reviews

@router.delete('/{review_id}',response_model=dict,status_code=status.HTTP_200_OK)
async def delete_reviews(review_id:int,
                         db:AsyncSession =Depends(get_async_db),current_user = Depends(get_current_user)):
    stmt_review = (select(ReviewsModel).where(ReviewsModel.id==review_id).
                   where(ReviewsModel.is_active == True))
    review = (await db.scalars(stmt_review)).first()
    if review is None:
        raise HTTPException(status_code=404,detail='Not Found')

    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=current_user.role)


    await db.execute(
        update(
            ReviewsModel
        ).where(ReviewsModel.id==review_id).values(is_active=False)
    )
    await db.refresh(review)
    await db.commit()
    await update_product_rating(db,review.product_id)
    return {"message": "Review deleted"}


async def update_product_rating(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(func.avg(ReviewsModel.grade)).where(
            ReviewsModel.product_id == product_id,
            ReviewsModel.is_active == True
        )
    )
    avg_rating = result.scalar() or 0.0
    product = await db.get(ProductModel, product_id)
    product.rating = avg_rating
    await db.commit()
