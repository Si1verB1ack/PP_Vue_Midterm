import shutil
import uuid
from flask import jsonify, request
from app import app, render_template, db
import os
from models.models import Product, Category, TempImage  # Change import to Product

TEMP_FOLDER = os.path.join('static', 'temp')
PRODUCT_FOLDER = os.path.join('static', 'upload/product')
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.config['PRODUCT_FOLDER'] = PRODUCT_FOLDER


@app.route("/admin/product/list")  # Change route to product
def product_list():
    module = {
        'main': 'Products',  # Update to Products
        'mainLink': 'product_list',
        'purpose': 'List',
        'purposeLink': 'product_list',
    }
    products = Product.query.all()  # Get all products
    print(products)
    return render_template("admin/product/list.html", module=module,
                           products=products)  # Change template to product list


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

        # Extract form data for the product
        name = form.get('name')
        code = form.get('code')
        category_id = form.get('category')  # Assume this is the category ID
        qty = form.get('qty')
        cost = form.get('cost')
        price = form.get('price')
        image_id = form.get('image_id')
        image_record = TempImage.query.get(image_id)
        image = None

        if image_record:
            image_name = image_record.name

            # Construct the full path to the temporary image file
            temp_file_path = os.path.join(app.config['TEMP_FOLDER'], image_name)

            # Construct the full path to the final upload folder
            final_file_path = os.path.join(app.config['PRODUCT_FOLDER'], image_name)

            # Move the image from the temporary folder to the final folder
            shutil.copy(temp_file_path, final_file_path)

            # You can now set 'profile' to the new file path or name
            image = image_name

        # Fetch the Category object based on category_id
        category = Category.query.get(category_id)
        if category is None:
            return jsonify({"message": "Invalid category ID"}), 400

        # Create a new Product object
        new_product = Product(
            name=name,
            code=code,
            category_id=category.id,  # Assign the Category object
            current_stock=qty,
            cost=cost,
            price=price,
            image=image
        )

        # Add the new product to the database
        db.session.add(new_product)
        db.session.commit()

        return jsonify({'status': True, 'message': 'Product added successfully'})

    categories = Category.query.all()
    categories_id = [{'id': category.id, 'name': category.name} for category in categories]

    return render_template("admin/product/add.html", module=module, categories=categories,
                           categories_id=categories_id)


@app.route('/admin/product/edit', methods=['GET', 'POST'])
def edit_product():
    # Fetch the product ID from the query parameters
    product_id = request.args.get('id')
    product = Product.query.get(product_id)

    # Create a dictionary and manually add the attributes you want, excluding 'image_id'
    product_data = {
        'id': product.id,  # ID of the product
        'name': product.name,  # Name of the product
        'code': product.code,  # Name of the product
        'price': product.price,  # Selling price of the product
        'cost': product.cost,  # Timestamp of when the product was last updated
        'qty': product.current_stock,  # Current stock of the product
        'category_id': product.category_id,  # Category ID of the product
        'image': product.image,  # Category ID of the product
    }

    temp_image = None
    if product.image:
        temp_image = TempImage.query.filter_by(name=product.image).first()

    if product is None:
        return jsonify({'error': 'Product not found'}), 404  # Return 404 if product is not found

    if request.method == 'POST':
        # Parse incoming JSON data for the product updates
        data = request.get_json()

        # Update the product fields with the new values from the request
        product.name = data.get('name')
        product.code = data.get('code')
        product.category_id = data.get('category')  # Ensure category_id is sent as part of data
        product.current_stock = data.get('qty')  # Update current stock
        product.cost = data.get('cost')  # Update cost
        product.price = data.get('price')  # Update price
        image_id = data.get('image_id')
        image_record = TempImage.query.get(image_id)

        if image_record:
            image_name = image_record.name

            # Construct the full path to the temporary image file
            temp_file_path = os.path.join(app.config['TEMP_FOLDER'], image_name)

            # Construct the full path to the final upload folder
            final_file_path = os.path.join(app.config['PRODUCT_FOLDER'], image_name)

            # Move the image from the temporary folder to the final folder
            shutil.copy(temp_file_path, final_file_path)

            # You can now set 'profile' to the new file path or name
            product.image = image_name
        # Update image ID or path

        try:
            # Commit the changes to the database
            db.session.commit()
            return jsonify({'message': 'Product updated successfully!'})  # Return success message
        except Exception as e:
            # Catch any errors and return them
            return jsonify({'error': str(e)}), 500

    # Prepare product data to pass to the template for rendering
    product_data['image_id'] = temp_image.id if temp_image else None

    # Define the module details for the template
    module = {
        'main': 'Products',  # Update to reflect "Products"
        'mainLink': 'product_list',  # Link to the product list page
        'purpose': 'Edit',
        'purposeLink': 'edit_product',
        'id': product_id
    }

    categories = Category.query.all()
    categories_id = [{'id': category.id, 'name': category.name} for category in categories]

    # Render the edit product template with product data and module details
    return render_template("admin/product/edit.html", product=product_data, module=module,
                           categories_id=categories_id, categories=categories)


@app.route('/admin/product/delete', methods=['POST'])  # Change route to product
def delete_product():
    # Get the product ID from the request
    product_id = request.get_json().get('id')

    # Find the product by ID
    product = Product.query.get(product_id)  # Change Category to Product

    if not product:
        return jsonify({'error': 'Product not found'}), 404  # Updated message

    try:
        # Delete the product from the database
        db.session.delete(product)
        db.session.commit()
        return jsonify({'status': True}), 200
    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        return jsonify({'error': str(e)}), 500
