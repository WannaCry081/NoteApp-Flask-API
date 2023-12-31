from App.models import UserModel, user_schema
from App.utils import jwt_is_blacklist, auth_required
from App import DB, BCRYPT

from flask_jwt_extended import jwt_required
from flask_restful import (
    Resource,
    reqparse,
    abort
)


class UserResource(Resource):
    def __init__(self):
        self.password_parser = reqparse.RequestParser()
        self.password_parser.add_argument("old_password", type=str, required=True)
        self.password_parser.add_argument("new_password", type=str, required=True)

        self.user_parser = reqparse.RequestParser()
        self.user_parser.add_argument("username", type=str)
        self.user_parser.add_argument("bio", type=str)

    @jwt_required() 
    @jwt_is_blacklist
    @auth_required
    def get(self, user_id : int):
        user : UserModel = UserModel.query.filter_by(id=user_id).first()
        schema = user_schema.dump(user)
        return {"user" : schema }, 200

    
    @jwt_required()
    @jwt_is_blacklist
    @auth_required
    def post(self, user_id : int):

        user : UserModel = UserModel.query.filter_by(id=user_id).first()
                
        data = self.password_parser.parse_args()

        if not BCRYPT.check_password_hash(user.password, data["old_password"]):
            abort(400, message="Incorrect Password")

        if len(data["old_password"]) < 6:
            abort(401, message="Password must at least be 6 characters long")
        
        user.password = BCRYPT.generate_password_hash(data["new_password"])
        DB.session.commit()
        return {"message" : "Updated password"}, 200
        
    
    @jwt_required()
    @jwt_is_blacklist
    @auth_required
    def put(self, user_id : int):
        
        user : UserModel = UserModel.query.filter_by(id=user_id).first()
        
        data = self.user_parser.parse_args()

        if data["username"]:
            if len(data["username"]) < 4:
                abort(401, message="Username must at least be 4 characters long")

            user.username = data["bio"]
        
        user.bio = data["bio"]
        DB.session.commit()
        return {"message" : "Updated Profile"}, 200


    @jwt_required()
    @jwt_is_blacklist
    @auth_required
    def delete(self, user_id : int):

        user : UserModel = UserModel.query.filter_by(id=user_id).first()        
        DB.session.delete(user)
        DB.session.commit()
        return {"message" : f"User '{user.username}' successfully deleted"}, 200

