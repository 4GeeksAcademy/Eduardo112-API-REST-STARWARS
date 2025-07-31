from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List

db = SQLAlchemy()


#Modelo de la tabla de usuarios
class User(db.Model):
    __tablename__= "user"              # __tablename__ Define el nombre de la tabla en la base de datos
    id: Mapped[int] = mapped_column(primary_key=True)               # primary_key Marca esta columna como clave primaria
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)         # unique significa que no puede ser repetido
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False) 
    registration_date: Mapped[datetime] = mapped_column(nullable=False)    # registration_date se genera solo   /    pongo datetime en vez de int y lo importo
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(db.String(120), nullable=False)


    favorites: Mapped[list["FavoritesList"]] = relationship("FavoritesList", back_populates="user", lazy="select")   #lazy: se utiliza para cargar los datos #Agrego la relación para que funcione en ambos sentidos

    def serialize(self):   # te da los datos con los que se rellenó
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "lastname": self.last_name,
            "registration_date": self.registration_date,
            "favorites": [fav.serialize for fav in self.favorites], # serialize cada uno de los favoritos 
            # do not serialize the password, its a security breach
        }
        

#Tabla de favoritos        
class FavoritesList(db.Model):
    __tablename__ = "favoritelist"
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), nullable=False)    #db.ForeignKey Crea una clave foránea, que conecta esta tabla con otra, entre parentesis indica la columna a la que hace referencia
    character_id: Mapped[int] = mapped_column(db.ForeignKey("character.id"), nullable=True)
    planet_id: Mapped[int] = mapped_column(db.ForeignKey("planet.id"), nullable=True)   #IMPORTANTE dentro de la ForeignKey se pone ".  no _"
   
    user: Mapped["User"] = relationship("User", back_populates="favorites")                  #relationship Establece una relación entre modelos (tablas).
    character: Mapped["Character"] = relationship("Character", back_populates="favorites")  #back_populates= Define la relación inversa, conecta ambos lados de la relación
    planet: Mapped["Planet"] = relationship("Planet", back_populates="favorites")

    def serialize(self):   # te da los datos con los que se rellenó
        data = {"id": self.id}
        #character
        if self.character:
            data["type"] = "character"
            data["name"] = self.character.name

        #planet
        elif self.planet:
            data["type"] = "planet"
            data["name"] = self.planet.name
       
      
     
        return data
    



#Modelo de la tabla de personajes
class Character(db.Model):       #db.Model es la clase base que proporciona SQLAlchemy para que puedas definir una tabla de base de datos como si fuera una clase Python.
    __tablename__ =  "character" #Define el nombre de la tabla en la base de datos
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    species: Mapped[str] = mapped_column(db.String(120), nullable=False)
    gender: Mapped[str] = mapped_column(db.String(120), nullable=False)

    favorites: Mapped[list["FavoritesList"]] = relationship("FavoritesList", back_populates="character") #Agrego la relación para que funcione en ambos sentidos

    def serialize(self):   # te da los datos con los que se rellenó
        return {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "gender": self.gender, 
        }


#Modelo de la tabla de Planetas   
class Planet(db.Model):
    __tablename__ = "planet"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(120), nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
    climate: Mapped[str] = mapped_column(db.String(120), nullable=False)
    population: Mapped[int] = mapped_column(nullable=False)

    favorites: Mapped[list["FavoritesList"]] = relationship("FavoritesList", back_populates="planet")  #Agrego la relación para que funcione en ambos sentidos


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "climate": self.climate,
            "population": self.population,
        }




"""
Orden para correrlo en la terminal:
pipenv install
pipenv  shell
pipenv run migrate
pipenv run upgrade
pipenv run diagram
ABRIR PUERTOS ANTES DE LEVANTAR PROYECTO
pipenv run start y ya puedes ver la pagina levantada
"""
