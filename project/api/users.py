from flask import Blueprint, jsonify, request, render_template
from sqlalchemy import exc

from project.api.models import User
from project.api.utils import is_admin, authenticate
from project import db

users_blueprint = Blueprint('users', __name__, template_folder='./templates')
auth_blueprint = Blueprint('auth', __name__)


@users_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
        })


@users_blueprint.route('/users', methods=['POST'])
@authenticate
def add_user(resp):
    if not is_admin(resp):
        response_object = {
            'status': 'error',
            'message': 'You do not have permission to do that.'
        }
        return jsonify(response_object), 401
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400
    username = post_data.get('username')
    email = post_data.get('email')
    password = post_data.get('password')
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            db.session.add(User(username=username, email=email, password=password))
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': f'{email} was added!'
            }
            return jsonify(response_object), 201
        else:
            response_object = {
                'status': 'fail',
                'message': 'Sorry. That email already exists.'
            }
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400


@users_blueprint.route('/users/<user_id>', methods=['GET'])
def get_single_user(user_id):
    """Get single user details."""
    response_object = {
        'status': 'fail',
        'message': 'User does not exist'
    }
    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'username': user.username,
                    'email': user.email,
                    'created_at': user.created_at
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404


@users_blueprint.route('/users', methods=['GET'])
@authenticate
def get_all_users(resp):
    """Get all users."""
    acting_user_id = resp
    if not is_admin(acting_user_id):
        response_object = {
            'status': 'error',
            'message': 'You do not have permissions to delete users.'
        }
        return jsonify(response_object), 401
    users = User.query.order_by(User.created_at.desc()).all()
    users_list = []
    for user in users:
        user_object = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at
        }
        users_list.append(user_object)
    response_object = {
        'status': 'success',
        'data': {
            'users': users_list
        }
    }
    return jsonify(response_object), 200


#@users_blueprint.route('/users/<user_id>', methods=['DELETE'])
#@authenticate
@users_blueprint.route('/users/<user_id>', methods=['DELETE'])
@authenticate
def delete_user(resp, user_id):
    response_object = {
        'status': 'fail',
        'message': 'Generic error message. Contact your sysadmin.'
    }
    acting_user_id = resp
    if not is_admin(acting_user_id):
        response_object = {
            'status': 'error',
            'message': 'You do not have permissions to delete users.'
        }
        return jsonify(response_object), 401
    # else:
    #     print("He has permission.")
    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            response_object = {
                'status': 'fail',
                'message': 'User does not exist'
            }
            return jsonify(response_object), 404
        else:
            db.session.delete(user)
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'User {} has been deleted.'.format(user.username)
            }
            return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload .'
        }
        return jsonify(response_object), 400
    except ValueError:
        return jsonify(response_object), 404

    response_object = {
        'status': 'fine',
        'message': 'Deleting user {}'.format(user.username)
    }
    return jsonify(response_object), 200

@users_blueprint.route('/users/<user_id>', methods=['PUT'])
@authenticate
def modify_user(resp, user_id):
    response_object = {
        'status': 'fail',
        'message': 'Generic error message. Contact your sysadmin.'
    }
    acting_user_id = resp
    # admin can modify anyone, and every user can modify him/herself
    if not (is_admin(acting_user_id) or acting_user_id == resp):
        response_object = {
            'status': 'error',
            'message': 'You do not have permission to modify this user.'
        }
        return jsonify(response_object), 401
    # if either field is null, we will get an IntegrityError and roll back
    # on db.session.commit()
    post_data = request.get_json()
    new_username = post_data.get('username')
    new_email = post_data.get('email')
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400
    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            response_object = {
                'status': 'fail',
                'message': 'User does not exist'
            }
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'message': 'Fields modified:'
            }
            if user.username == new_username and user.email == new_email:
                response_object['message'] = 'No fields modified.'
                # This doesn't matter, 204 returns no headers
                return jsonify(response_object), 204
            else:
                if user.username != new_username:
                    user.username = new_username
                    response_object['message'] += ' username'
                if user.email != new_email:
                    user.email = new_email
                    response_object['message'] += ' email'
                db.session.commit()
                return jsonify(response_object), 200
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400
    except (exc.IntegrityError, ValueError) as e:
        db.session.rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return jsonify(response_object), 400




