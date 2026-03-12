from waitress import serve
from Direct.wsgi import application

# documentation: https://docs.pylonsproject.org/projects/waitress/en/stable/api.html

if __name__ == '__main__':
    serve(application, host='10.1.10.200', port='8080', threads=20)
'''

from waitress.server import create_server
from Direct.wsgi import application


# import your flask app

class WaitressServer:

    def __init__(self, host, port):
        self.server = create_server(application, host=host, port=port)

    # call this method from your service to start the Waitress server
    def run(self):
        self.server.run()

    # call this method from the services stop method
    def stop_service(self):
        self.server.close()
'''
