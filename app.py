from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
import AuthDatabase


class Test(Resource):
    def get(self):
        AuthDatabase.auth_admin()

        return 2

    def post(self):
        return 3



app = Flask(__name__)

api = Api(app)
api.add_resource(Test, "/Tests")

if __name__ == '__main__':
    app.run()
