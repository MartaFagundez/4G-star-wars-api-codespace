from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return 'id: ' + str(self.id) + ', email: ' + self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
            "is_active": self.is_active,
        }
    
class Planet(db.Model):
    __tablename__ = 'Planets'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    climate = db.Column(db.String(20))
    terrain = db.Column(db.String(20))
    diameter = db.Column(db.String(20))
    rotation_period = db.Column(db.String(10))
    orbital_period = db.Column(db.String(10))
    gravity = db.Column(db.String(10))
    population = db.Column(db.String(20))

    def __repr__(self):
        return 'id: ' + str(self.id) + ', name: ' + self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "terrain": self.terrain,
            "diameter": self.diameter,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
            "gravity": self.gravity,
            
        }

class Character(db.Model):
    __tablename__ = 'Characters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    height = db.Column(db.String(10))
    mass = db.Column(db.String(10))
    hair_color = db.Column(db.String(20))
    skin_color = db.Column(db.String(20))
    eye_color = db.Column(db.String(20))
    birth_year = db.Column(db.String(20))
    gender = db.Column(db.String(10))
    home_world_id = db.Column(db.Integer, db.ForeignKey('Planets.id'))
    home_world = db.relationship(Planet)

    def __repr__(self):
        return 'id: ' + str(self.id) + ', name: ' + self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "home_world_id": self.home_world_id,
            "home_world_name": self.home_world.serialize()['name']
        }

class FavoriteCharacter(db.Model):
    __tablename__ = 'FavoriteCharacters'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    user = db.relationship(User)
    character_id = db.Column(db.Integer, db.ForeignKey('Characters.id'), nullable=False)
    character = db.relationship(Character)

    def __repr__(self):
        return 'id: ' + str(self.id) + ', user_id: ' + str(self.user_id) + ', character_id: ' + str(self.character_id)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "character": self.character.serialize()
        }

class FavoritePlanet(db.Model):
    __tablename__ = 'FavoritePlanets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    user = db.relationship(User)
    planet_id = db.Column(db.Integer, db.ForeignKey('Planets.id'), nullable=False)
    planet = db.relationship(Planet)

    def __repr__(self):
        return 'id: ' + str(self.id) + ', user_id: ' + str(self.user_id) + ', planet_id: ' + str(self.planet_id)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "planet": self.planet.serialize()
        }