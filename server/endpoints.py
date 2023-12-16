# In endpoints.py
from http import HTTPStatus
from flask import Flask, request
from flask_restx import Resource, Api, fields
import werkzeug.exceptions as wz
import data.users as us

app = Flask(__name__)
api = Api(app)

DEFAULT = 'Default'
MENU = 'menu'
MAIN_MENU_EP = '/MainMenu'
MAIN_MENU_NM = "MTA Route Planner"
HELLO_EP = '/hello'
HELLO_RESP = 'hello'
USERS_EP = '/users'
BUSES_EP = '/bus_routes'
ADDRESSES_EP = '/addresses'
ADDRESS_MENU_EP = '/address_menu'
ADDRESS_MENU_NM = 'Address Menu'
DEL_USER_EP = f'{USERS_EP}/delete'  # Adjusted endpoint for deleting users
USER_MENU_EP = '/user_menu'
USER_MENU_NM = 'User Menu'
TYPE = 'Type'
DATA = 'Data'
TITLE = 'Title'
RETURN = 'Return'
HOME_ADDR_EP = '/home_address'
ROUTE_EP = '/routes'

user_model = api.model('User', {
    'username': fields.String(required=True, description='Username'),
    'account_id': fields.String(required=True, description='Account ID'),
})

add_home_address_model = api.model('AddHomeAddress', {
    'username': fields.String(required=True, description='Username'),
    'home_address': fields.String(required=True, description='Home Address'),
})

route_model = api.model('Route', {
    'starting_point': fields.String(required=True, description='Starting Point'),
    'ending_point': fields.String(required=True, description='Ending Point'),
})


@api.route('/hello')
class HelloWorld(Resource):
    """
    The purpose of the HelloWorld class is to have a simple test to see if the
    app is working at all.
    """
    def get(self):
        """
        A trivial endpoint to see if the server is running.
        It just answers with "hello world."
        """
        return {'hello': 'world'}


@api.route('/addresses')
class Addresses(Resource):
    """
    This class supports fetching a list of all addresses.
    """
    def get(self):
        """
        This method returns all addresses.
        """
        # Fetch the latest user data from the database
        users_data = us.get_users_as_dict()

        return {
            us.HOME: [user.get(us.HOME, '') for user in users_data],
        }


@api.route('/endpoints')
class Endpoints(Resource):
    """
    This class will serve as live, fetchable documentation of what endpoints
    are available in the system.
    """
    def get(self):
        """
        The `get()` method will return a list of available endpoints.
        """
        endpoints = sorted(rule.rule for rule in api.app.url_map.iter_rules())
        return {"Available endpoints": endpoints}


@api.route('/MainMenu')
class MainMenu(Resource):
    """
    This will deliver our main menu.
    """
    def get(self):
        """
        Gets the main game menu.
        """
        return {TITLE: 'MTA Route Planner',
                RETURN: '/users'}


@api.route('/user_menu')
class UserMenu(Resource):
    """
    This will deliver our user menu.
    """
    def get(self):
        """
        Gets the user menu.
        """
        return {
            TITLE: 'User Menu',
            RETURN: '/MainMenu',
        }


@api.route('/users')
class Users(Resource):
    """
    This class supports fetching a list of all users.
    """
    def get(self):
        """
        This method returns all users.
        """
        return {
            TYPE: DATA,
            TITLE: 'Current Users',
            DATA: us.get_users_as_dict(),
            RETURN: '/MainMenu',
        }


@api.route('/users/<username>')
class GetUserByUsername(Resource):
    """
    Gets a user by username.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, username):
        """
        Gets a user by username.
        """
        try:
            user = us.get_user_by_username(username)
            if user:
                return {
                    TYPE: DATA,
                    TITLE: f'User Details for {username}',
                    DATA: user,
                    RETURN: '/MainMenu',
                }
            else:
                raise wz.NotFound(f'User with username {username} not found.')
        except ValueError as e:
            raise wz.InternalServerError(f'Error: {str(e)}')


@api.route('/users/delete/<username>')
class DelUser(Resource):
    """
    Deletes a user by username.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def delete(self, username):
        """
        Deletes a user by username.
        """
        try:
            us.del_user(username, True)
            return {username: 'Deleted'}
        except ValueError as e:
            raise wz.NotFound(f'{str(e)}')


@api.route('/add_user')
class AddUser(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.BAD_REQUEST, 'Bad Request')
    @api.expect(user_model)
    def post(self):
        """
        Adds a new user.
        """
        try:
            # Print received parameters for debugging
            data = request.json
            username = data.get('username')
            print(f"Received request: username={username}")
            # Call the add_user function
            account_id = us.gen_account_id()
            us.add_user(username, account_id)

            return {'message': 'User created successfully'}
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.BAD_REQUEST


@api.route('/users/account/<account_id>')
class GetUserByAccountId(Resource):
    """
    Gets a user by account ID.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, account_id):
        """
        Gets a user by account ID.
        """
        try:
            user = us.get_user_by_account_id(account_id)
            if user:
                return {
                    TYPE: DATA,
                    TITLE: f'User Details for Account ID {account_id}',
                    DATA: user,
                    RETURN: '/MainMenu',
                }
            else:
                raise wz.NotFound(f'User with account ID {account_id} not found.')
        except ValueError as e:
            raise wz.InternalServerError(f'Error: {str(e)}')


@api.route('/users/home_address')
class AddHomeAddress(Resource):
    """
    Adds a home address to a user.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.BAD_REQUEST, 'Bad Request')
    @api.expect(add_home_address_model)  # Use the same modified model for this endpoint
    def post(self):
        """
        Adds a home address to a user.
        """
        try:
            # Get data from the request
            data = request.json
            username = data.get('username')
            home_address = data.get('home_address')

            # Call the add_home_address function
            us.add_home_address(username, home_address)

            return {'message': 'Home address added successfully'}
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.BAD_REQUEST


@api.route('/users/home_address/<username>')
class GetHomeAddress(Resource):
    """
    Gets the home address of a user by username.
    """
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.NOT_FOUND, 'Not Found')
    def get(self, username):
        """
        Gets the home address of a user by username.
        """
        try:
            user = us.get_user_by_username(username)
            if user:
                home_address = us.get_home_address(user)
                return {
                    TYPE: DATA,
                    TITLE: f'Home Address for {username}',
                    DATA: {'home_address': home_address},
                    RETURN: '/MainMenu',
                }
            else:
                raise wz.NotFound(f'User with username {username} not found.')
        except ValueError as e:
            raise wz.InternalServerError(f'Error: {str(e)}')


@api.route('/add_route')
class AddRoute(Resource):
    @api.response(HTTPStatus.OK, 'Success')
    @api.response(HTTPStatus.BAD_REQUEST, 'Bad Request')
    @api.expect(route_model)
    def post(self):
        """
        Adds a new route.
        """
        try:
            # Print received parameters for debugging
            data = request.json
            starting_point = data.get('starting_point')
            ending_point = data.get('ending_point')
            print(f"Received request: starting_point={starting_point}, ending_point={ending_point}")
            # Call the add_route function
            route_id = routes.gen_route_id()
            routes.add_route(starting_point, ending_point, route_id)

            return {'message': 'Route created successfully'}
        except ValueError as e:
            return {'message': str(e)}, HTTPStatus.BAD_REQUEST


if __name__ == '__main__':
    app.run(debug=True)
