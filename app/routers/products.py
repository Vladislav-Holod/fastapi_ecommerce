from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Reviews as ReviewsModel
from app.models import Product as ProductModel
from app.models import Category as CategoryModel
from app.schemas import Product as ProductSchema, ProductCreate,Review
from app.db_depends import get_async_db
from app.models import User as UserModel
from app.auth import get_current_seller
# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех товаров.
    """
    stmt = select(ProductModel).where(ProductModel.is_active == True)
    result = (await db.scalars(stmt)).all()
    return result

@router.get("/{product_id}/reviews", response_model=list[Review])
async def get_reviews_product(product_id: int,
                              db: AsyncSession = Depends(get_async_db)):
    stmt_product = select(ProductModel).where(ProductModel.id == product_id,
                                              ProductModel.is_active == True)

    product = (await db.scalars(stmt_product)).first()
    if product is None:
        raise HTTPException(status_code=404,
                            detail='Not Found')

    stmt_reviews = select(ReviewsModel).where(ReviewsModel.product_id == product_id,
                                              ReviewsModel.is_active == True)
    reviews = (await db.scalars(stmt_reviews)).all()
    return reviews



@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate,
                         db: AsyncSession = Depends(get_async_db),
                         current_user:UserModel= Depends(get_current_seller)):
    """
    Создаёт новый товар.
    """
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id).where(
        CategoryModel.is_active == True)
    result = (await db.scalars(stmt)).all()
    if result is None:
        raise HTTPException(status_code=400, detail='Category not found or inactive')

    db_product = ProductModel(**product.model_dump(),seller_id=current_user.id)
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product) # Для получения id и is_active из базы
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    stmt_category = select(CategoryModel).where(CategoryModel.id == category_id).where(CategoryModel.is_active == True)
    result = (await db.scalars(stmt_category)).first()
    if result is None:
        raise HTTPException(status_code=404, detail='Category not found or inactive')
    stmt_product = select(ProductModel).where(ProductModel.category_id == category_id).where(
        ProductModel.is_active == True)
    result = (await db.scalars(stmt_product)).all()
    return result


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    stmt_product = select(ProductModel).where(ProductModel.id == product_id).where(ProductModel.is_active == True)
    product = (await db.scalars(stmt_product)).first()
    if product is None:
        raise HTTPException(status_code=404, detail='Product not found or inactive')
    stmt_category_active = select(CategoryModel).where(CategoryModel.id == product.category_id).where(
        CategoryModel.is_active == True)
    category_is_active = (await db.scalars(stmt_category_active)).first()
    if category_is_active is None:
        raise HTTPException(status_code=400, detail='Category not found or inactive')
    return product


@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product: ProductCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_seller)
):
    """
    Обновляет товар, если он принадлежит текущему продавцу (только для 'seller').
    """
    result = await db.scalars(select(ProductModel).where(ProductModel.id == product_id, ProductModel.is_active == True))
    db_product = result.first()
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if db_product.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own products")
    category_result = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == product.category_id, CategoryModel.is_active == True)
    )
    if not category_result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category not found or inactive")
    await db.execute(
        update(ProductModel).where(ProductModel.id == product_id).values(**product.model_dump())
    )
    await db.commit()
    await db.refresh(db_product)  # Для консистентности данных
    return db_product


@router.delete("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def delete_product(product_id: int,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_seller)):
    """
    Удаляет товар по его ID.
    """
    stmt_active_product = select(ProductModel).where(ProductModel.id == product_id).where(
        ProductModel.is_active == True)
    result_product_active = (await db.scalars(stmt_active_product)).first()
    if result_product_active is None:
        raise HTTPException(status_code=404, detail='Product not found or inactive')
    if result_product_active.seller_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own products")

    await db.execute(
        update(ProductModel).where(ProductModel.id == product_id).
        values(is_active=False))

    await db.commit()
    await db.refresh(result_product_active)
    return result_product_active



