import shutil
import uuid

from flask import jsonify, request, flash, redirect, url_for, json
from app import app, render_template, db
import os
from models.models import User, TempImage, Category

TEMP_FOLDER = os.path.join('static', 'temp')
UPLOAD_FOLDER = os.path.join('static', 'upload/profile')
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/admin/categoryGet")
def category_get():
    categories = Category.query.all()
    category_dict = [
        {
            'id': category.id,
            'name': category.name,
            'description': category.description,
        } for category in categories
    ]
    return jsonify({'categories': category_dict})


@app.route("/admin/category/list")
def category_list():
    module = {
        'main': 'Users',
        'mainLink': 'category_list',
        'purpose': 'List',
        'purposeLink': 'category_list',
    }
    categories = Category.query.all()
    return render_template("admin/category/list.html", module=module, categories=categories)


@app.route('/admin/category/add', methods=['GET', 'POST'])
def category_add():
    module = {
        'main': 'Categories',
        'mainLink': 'category_list',
        'purpose': 'Add',
        'purposeLink': 'category_add',
    }

    if request.method == 'POST':
        form = request.get_json()

        if form is None:
            return jsonify({"message": "No data provided"}), 400

        # Extract form data for category
        name = form.get('name')
        description = form.get('description')

        # Create a new Category object
        new_category = Category(
            name=name,
            description=description
        )

        db.session.add(new_category)
        db.session.commit()

        return jsonify({'status': True})

    return render_template("admin/category/add.html", module=module)


@app.route('/admin/category/edit', methods=['GET', 'POST'])
def edit_category():
    category_id = request.args.get('id')
    category = Category.query.get(category_id)

    if category is None:
        return jsonify({'error': 'Category not found'}), 404  # Updated message

    if request.method == 'POST':
        data = request.get_json()
        category.name = data.get('name')
        category.description = data.get('description')

        try:
            db.session.commit()
            return jsonify({'message': 'Category updated successfully!'})  # Updated message
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    category_data = {column.name: getattr(category, column.name) for column in
                     Category.__table__.columns}

    module = {
        'main': 'Categories',  # Updated for categories
        'mainLink': 'category_list',
        'purpose': 'Edit',
        'purposeLink': 'edit_category',
        'id': category_id
    }

    return render_template("admin/category/edit.html", category=category_data, module=module)  # Updated template path


@app.route('/admin/category/delete', methods=['POST'])
def delete_category():
    # Get the category ID from the request
    category_id = request.get_json().get('id')

    # Find the category by ID
    category = Category.query.get(category_id)  # Changed User to Category

    if not category:
        return jsonify({'error': 'Category not found'}), 404  # Updated message

    try:
        # Delete the category from the database
        db.session.delete(category)
        db.session.commit()
        return jsonify({'status': True}), 200
    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        return jsonify({'error': str(e)}), 500

