from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, ForeignKey, Text, Numeric, Date, Column, Table
from datetime import datetime


class Base(DeclarativeBase):
    pass


participations = Table('participations', Base.metadata,

                     Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True),
                     Column('employee_id', Integer, ForeignKey('employees.id'), primary_key=True),
                     Column('role',String(50),nullable=False)
                     )


class Project(Base):
    __tablename__ = 'projects'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    start_date = mapped_column(Date, nullable=False)
    employees = relationship('Employee',
                             secondary=participations,
                             back_populates='projects'
    )


class Employee(Base):
    __tablename__ = 'employees'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    projects = relationship('Project',
                             secondary=participations,
                             back_populates='employees'
                             )
