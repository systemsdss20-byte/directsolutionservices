#activate_this = 'C:/Appdirect/venvapp/Scripts/activate_this.py'
# execfile(activate_this, dict(__file__=activate_this))
#exec(open(activate_this).read(), dict(__file__=activate_this))

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('C:/Appdirect/venvapp/Lib/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('C:/Appdirect/Direct')
sys.path.append('C:/Appdirect/Direct/Direct')

os.environ['DJANGO_SETTINGS_MODULE'] = 'Direct.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Direct.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
