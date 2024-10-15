from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(255), nullable=False)  # Hash the password later
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    gender = db.Column(db.Integer, nullable=False)  # 0 for Female, 1 for Male
    role = db.Column(db.Integer, nullable=False)  # 0 for User, 1 for Admin
    status = db.Column(db.Integer, nullable=False)  # 1 for Active, 0 for Inactive
    address = db.Column(db.Text, nullable=True)
    profile = db.Column(db.String(100), nullable=True)


class TempImage(db.Model):
    __tablename__ = 'temp_image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationship to Product
    products = db.relationship('Product', back_populates='category')


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(100), nullable=False)

    # Foreign key to Category (update the column name to 'category')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

    cost = db.Column(db.Numeric(10, 2), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    current_stock = db.Column(db.Integer, default=0)

    # Relationship to Category (update if necessary)
    category = db.relationship('Category', back_populates='products')

