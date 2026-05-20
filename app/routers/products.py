from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.models.products import Product as ProductModel
from app.models.categories import Category as CategoryModel
from app.schemas import Product as ProductSchema, ProductCreate
from app.db_depends import get_db

# Создаём маршрутизатор для товаров
router = APIRouter(
    prefix="/products",
    tags=["products"],
)


@router.get("/", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_all_products(db: Session = Depends(get_db)):
    """
    Возвращает список всех товаров.
    """
    stmt = select(ProductModel).where(ProductModel.is_active == True)
    result = db.scalars(stmt).all()
    return result


@router.post("/", response_model=ProductSchema, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Создаёт новый товар.
    """
    stmt = select(CategoryModel).where(CategoryModel.id == product.category_id).where(
        CategoryModel.is_active == True)
    result = db.scalars(stmt).first()
    if result is None:
        raise HTTPException(status_code=400, detail='Category not found or inactive')

    db_product = ProductModel(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/category/{category_id}", response_model=list[ProductSchema], status_code=status.HTTP_200_OK)
async def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    """
    Возвращает список товаров в указанной категории по её ID.
    """
    stmt_category = select(CategoryModel).where(CategoryModel.id == category_id).where(CategoryModel.is_active == True)
    result = db.scalars(stmt_category).first()
    if result is None:
        raise HTTPException(status_code=404, detail='Category not found or inactive')
    stmt_product = select(ProductModel).where(ProductModel.category_id == category_id).where(
        ProductModel.is_active == True)
    result = db.scalars(stmt_product).all()
    return result


@router.get("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Возвращает детальную информацию о товаре по его ID.
    """
    stmt_product = select(ProductModel).where(ProductModel.id == product_id).where(ProductModel.is_active == True)
    product = db.scalars(stmt_product).first()
    if product is None:
        raise HTTPException(status_code=404, detail='Product not found or inactive')
    stmt_category_active = select(CategoryModel).where(CategoryModel.id == product.category_id).where(
        CategoryModel.is_active == True)
    category_is_active = db.scalars(stmt_category_active).first()
    if category_is_active is None:
        raise HTTPException(status_code=400, detail='Category not found or inactive')
    return product


@router.put("/{product_id}", response_model=ProductSchema, status_code=status.HTTP_200_OK)
async def update_product(product_id: int, product: ProductCreate, db: Session = Depends(get_db)):
    """
    Обновляет товар по его ID.
    """
    stmt_active = select(ProductModel).where(ProductModel.id == product_id).where(ProductModel.is_active == True)
    result_product = db.scalars(stmt_active).first()
    if result_product is None:
        raise HTTPException(status_code=404, detail="Product not found or inactive")

    stmt_category_active = select(CategoryModel).where(CategoryModel.id == product.category_id).where(
        CategoryModel.is_active == True)
    result_category = db.scalars(stmt_category_active).first()

    if result_category is None:
        raise HTTPException(status_code=400, detail="Category not found or inactive")

    db.execute(
        update(ProductModel).where(ProductModel.id == product_id).
        values(**product.model_dump()
        )
    )
    db.commit()
    db.refresh(result_product)
    return result_product


@router.delete("/{product_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Удаляет товар по его ID.
    """
    stmt_active_product = select(ProductModel).where(ProductModel.id == product_id).where(
        ProductModel.is_active == True)
    result_product_active = db.scalars(stmt_active_product).first()
    if result_product_active is None:
        raise HTTPException(status_code=404, detail='Product not found or inactive')
    db.execute(
        update(ProductModel).where(ProductModel.id == product_id).
        values(is_active=False))

    db.commit()
    return {"status": "success", "message": "Product marked as inactive"}

