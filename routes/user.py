import shutil
import uuid
from werkzeug.security import generate_password_hash
from flask import jsonify, request, flash, redirect, url_for, json
from app import app, render_template, db
import os
from models.models import User, TempImage

TEMP_FOLDER = os.path.join('static', 'temp')
PROFILE_FOLDER = os.path.join('static', 'upload/profile')
app.config['TEMP_FOLDER'] = TEMP_FOLDER
app.config['PROFILE_FOLDER'] = PROFILE_FOLDER


@app.route("/admin/userGet")
def user_get():
    users = User.query.all()
    users_dict = [
        {
            'id': user.id,
            'name': user.name,
            'code': user.code,
            'email': user.email,
            'phone': user.phone,
            'gender': user.gender,
            'role': user.role,
            'status': user.status,
            'address': user.address,
            'profile': user.profile
        } for user in users
    ]

    return jsonify({'users': users_dict})


@app.route("/admin/user/list")
def user_list():
    module = {
        'main': 'Users',
        'mainLink': 'user_list',
        'purpose': 'List',
        'purposeLink': 'user_list',
    }
    users = User.query.all()
    return render_template("admin/users/list.html", module=module, users=users)


@app.route('/admin/user/add', methods=['GET', 'POST'])
def user_add():
    module = {
        'main': 'Users',
        'mainLink': 'user_list',
        'purpose': 'Add',
        'purposeLink': 'user_add',
    }

    profile = None

    if request.method == 'POST':
        # Extract JSON data from the request
        form = request.get_json()

        if form is None:
            return jsonify({"message": "No data provided"}), 400
        # Extract form data
        name = form.get('name')
        password = form.get('password')
        code = form.get('code')
        gender = form.get('gender')
        email = form.get('email')
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"message": "Email is already taken"}), 400
        phone = form.get('phone')
        role = form.get('role')
        status = form.get('status')
        address = form.get('address')
        image_id = form.get('image_id')

        image_record = TempImage.query.get(image_id)

        if image_record:
            image_name = image_record.name

            temp_file_path = os.path.join(app.config['TEMP_FOLDER'], image_name)

            final_file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)

            shutil.copy(temp_file_path, final_file_path)

            profile = image_name

        # Create a new User object
        new_user = User(
            name=name,
            password=password,  # Make sure to hash the password before saving
            code=code,
            gender=gender,
            email=email,
            phone=phone,
            role=role,
            status=status,
            address=address,
            profile=profile
        )

        # Add and commit the new user to the database
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'status': True})

    return render_template("admin/users/add.html", module=module)


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


@app.route('/admin/upload-temp-image/create', methods=['POST'])
def upload_temp_image():
    if request.files['image']:
        file = request.files['image']
        # Save the file
        uuid_name = str(uuid.uuid4())  # Generate a unique ID for the image
        filename = uuid_name + os.path.splitext(file.filename)[1]
        file_path = os.path.join(app.config['TEMP_FOLDER'], filename)
        # Save the file to the specified path
        file.save(file_path)

        # Create a new TempImage instance
        new_image = TempImage(name=filename)

        # Add the new image to the session and commit
        db.session.add(new_image)
        db.session.commit()

        # Get the ID of the newly inserted image
        image_id = new_image.id

        print(image_id)

        return jsonify({'image_id': image_id})


@app.route('/admin/user/edit', methods=['GET', 'POST'])
def edit_user():
    user_id = request.args.get('id')
    user = User.query.get(user_id)
    temp_image = None
    if user.profile:
        temp_image = TempImage.query.filter_by(name=user.profile).first()

    if user is None:
        return jsonify({'error': 'User not found'}), 404

    if request.method == 'POST':
        data = request.get_json()
        user.name = data.get('name')
        user.password = data.get('password')
        user.code = data.get('code')
        user.gender = data.get('gender')
        user.email = data.get('email')
        user.phone = data.get('phone')
        user.role = data.get('role')
        user.status = data.get('status')
        user.address = data.get('address')
        image_id = data.get('image_id')
        image_record = TempImage.query.get(image_id)

        if image_record:
            image_name = image_record.name

            # Construct the full path to the temporary image file
            temp_file_path = os.path.join(app.config['TEMP_FOLDER'], image_name)

            # Construct the full path to the final upload folder
            final_file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)

            # Move the image from the temporary folder to the final folder
            shutil.copy(temp_file_path, final_file_path)

            # You can now set 'profile' to the new file path or name
            user.profile = image_name

        try:
            db.session.commit()
            return jsonify({'message': 'User updated successfully!'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    user_data = {column.name: getattr(user, column.name) for column in User.__table__.columns}
    user_data['image_id'] = temp_image.id if temp_image else None

    module = {
        'main': 'Users',
        'mainLink': 'user_list',
        'purpose': 'Edit',
        'purposeLink': 'edit_user',
        'id': user_id
    }

    return render_template("admin/users/edit.html", user=user_data, module=module)


@app.route('/admin/user/delete', methods=['POST'])
def delete_user():
    # Get the user ID from the request
    user_id = request.get_json().get('id')

    # Find the user by ID
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    try:
        # Delete the user from the database
        db.session.delete(user)
        db.session.commit()
        return jsonify({'status': True}), 200
    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        return jsonify({'error': str(e)}), 500


@app.route('/admin/users/check-email', methods=['GET'])
def check_email():
    email = request.args.get('email')

    if not email:
        return jsonify({'status': False, 'message': 'Email is required'}), 400

    # Check if the email exists in the database
    user = User.query.filter_by(email=email).first()

    if user:
        return jsonify({'status': False, 'message': 'Email already exists'}), 200  # Email exists
    else:
        return jsonify({'status': True, 'message': 'Email is available'}), 200  # Email is available


def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
