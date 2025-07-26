from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List

db = SQLAlchemy()

class User(db.Model):
    __tablename__= "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    registration_date: Mapped[datetime] = mapped_column(nullable=False)    # se genera solo
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    favorites: Mapped[list["FavoritesList"]] = relationship("FavoritesList", back_populates="user", lazy="select")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class FavoritesList(db.Model):
    __tablename__ = "favoritelist"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), nullable=False)
   
    user: Mapped["User"] = relationship("User", back_populates="favorites")