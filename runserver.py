import os
from dotenv import load_dotenv
from waitress import serve
from Direct.wsgi import application

load_dotenv()

# documentation: https://docs.pylonsproject.org/projects/waitress/en/stable/api.html

if __name__ == '__main__':
    host = os.getenv('RUNSERVER_HOST')
    port = int(os.getenv('RUNSERVER_PORT'))
    threads = int(os.getenv('WAITRESS_THREADS', '20'))
    serve(application, host=host, port=port, threads=threads)