import shutil
import uuid
from flask import jsonify, request
from app import app, render_template, db
import os
from models.models import Product, Category, TempImage

TEMP_FOLDER = os.path.join('static', 'temp')
PRODUCT_FOLDER = os.path.join('static', 'upload/product')
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.config['PRODUCT_FOLDER'] = PRODUCT_FOLDER


@app.route("/admin/ProductGet")
def product_get():
    products = Product.query.all()
    categories = Category.query.all()
    category_lookup = {category.id: category.name for category in categories}
    products_dict = [
        {
            'id': product.id,
            'name': product.name,
            'code': product.code,
            'price': product.price,
            'cost': product.cost,
            'qty': product.current_stock,
            'category_name': category_lookup.get(product.category_id, 'Unknown Category'),
            'image': product.image,

        } for product in products
    ]

    return jsonify({'products': products_dict})


@app.route("/admin/product/list")
def product_list():
    module = {
        'main': 'Products',
        'mainLink': 'product_list',
        'purpose': 'List',
        'purposeLink': 'product_list',
    }
    products = Product.query.all()
    return render_template("admin/product/list.html", module=module,
                           products=products)


@app.route('/admin/product/add', methods=['GET', 'POST'])
def product_add():
    module = {
        'main': 'Products',
        'mainLink': 'product_list',
        'purpose': 'Add',
        'purposeLink': 'product_add',
    }

    if request.method == 'POST':
        form = request.get_json()

        if form is None:
            return jsonify({"message": "No data provided"}), 400

        name = form.get('name')
        code = form.get('code')
        category_id = form.get('category')
        qty = form.get('qty')
        cost = form.get('cost')
        price = form.get('price')
        image_id = form.get('image_id')
        image_record = TempImage.query.get(image_id)
        image = None

        if image_record:
            image_name = image_record.name

            temp_file_path = os.path.join(app.config['TEMP_FOLDER'], image_name)

            final_file_path = os.path.join(app.config['PRODUCT_FOLDER'], image_name)

            shutil.copy(temp_file_path, final_file_path)

            image = image_name

        category = Category.query.get(category_id)
        if category is None:
            return jsonify({"message": "Invalid category ID"}), 400

        new_product = Product(
            name=name,
            code=code,
            category_id=category.id,
            current_stock=qty,
            cost=cost,
            price=price,
            image=image
        )

        db.session.add(new_product)
        db.session.commit()

        return jsonify({'status': True, 'message': 'Product added successfully'})

    categories = Category.query.all()
    categories_id = [{'id': category.id, 'name': category.name} for category in categories]

    return render_template("admin/product/add.html", module=module, categories=categories,
                           categories_id=categories_id)


@app.route('/admin/product/edit', methods=['GET', 'POST'])
def edit_product():
    product_id = request.args.get('id')
    product = Product.query.get(product_id)

    product_data = {
        'id': product.id,
        'name': product.name,
        'code': product.code,
        'price': product.price,
        'cost': product.cost,
        'qty': product.current_stock,
        'category_id': product.category_id,
        'image': product.image,
    }

    temp_image = None
    if product.image:
        temp_image = TempImage.query.filter_by(name=product.image).first()

    if product is None:
        return jsonify({'error': 'Product not found'}), 404

    if request.method == 'POST':
        data = request.get_json()

        product.name = data.get('name')
        product.code = data.get('code')
        product.category_id = data.get('category')
        product.current_stock = data.get('qty')
        product.cost = data.get('cost')
        product.price = data.get('price')
        image_id = data.get('image_id')
        image_record = TempImage.query.get(image_id)

        if image_record:
            image_name = image_record.name

            temp_file_path = os.path.join(app.config['TEMP_FOLDER'], image_name)

            final_file_path = os.path.join(app.config['PRODUCT_FOLDER'], image_name)

            shutil.copy(temp_file_path, final_file_path)

            product.image = image_name

        try:
            db.session.commit()
            return jsonify({'message': 'Product updated successfully!'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    product_data['image_id'] = temp_image.id if temp_image else None

    module = {
        'main': 'Products',
        'mainLink': 'product_list',
        'purpose': 'Edit',
        'purposeLink': 'edit_product',
        'id': product_id
    }

    categories = Category.query.all()
    categories_id = [{'id': category.id, 'name': category.name} for category in categories]

    return render_template("admin/product/edit.html", product=product_data, module=module,
                           categories_id=categories_id, categories=categories)


@app.route('/admin/product/delete', methods=['POST'])
def delete_product():
    product_id = request.get_json().get('id')

    product = Product.query.get(product_id)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'status': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
