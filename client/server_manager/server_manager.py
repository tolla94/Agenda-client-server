from login_gateway import LoginGateway
from server_request_handler import ServerRequestHandler


class ServerManager:
    def __init__(self):
        self.server_url = "http://127.0.0.1:5000"

        self.login_gateway = LoginGateway(self.server_url)

        self.server_request_handler = ServerRequestHandler(self.server_url)

    def get_token(self, user):
        return self.login_gateway.get_token(user)

    def do_login(self, token):
        pass
