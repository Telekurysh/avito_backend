from flask import Flask
from flask_restx import Api, Resource
import app

api = Api(version='1.0', title='Сервис баннеров')
api.spec_path = 'api.yaml'

# Ресурсы API
@api.route('/user_banner')
class UserBanner(Resource):
    def get(self):
        return app.get_user_banner('user')


@api.route('/banner')
class Banner(Resource):
    def get(self):
        return app.get_banners('admin')

    def post(self):
        return app.create_banner('admin')


@api.route('/banner/<int:id>')
class BannerById(Resource):
    def get(self, id):
        return app.get_banners_with_filter(id, 'admin')

    def patch(self, id):
        return app.update_banner(id, 'admin')

    def delete(self, id):
        return app.delete_banner(id, 'admin')


if __name__ == '__main__':
    app.run(debug=True)
