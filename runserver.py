import os
from dotenv import load_dotenv
from waitress import serve
from Direct.wsgi import application

load_dotenv()

# documentation: https://docs.pylonsproject.org/projects/waitress/en/stable/api.html

if __name__ == '__main__':
    host = os.getenv('RUNSERVER_HOST', '0.0.0.0')
    port = int(os.getenv('RUNSERVER_PORT', '8080'))
    threads = int(os.getenv('WAITRESS_THREADS', '20'))
    serve(application, host=host, port=port, threads=threads)
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
