## Instalar 
```
pip install python-dotenv
pip install djangorestframework
pip install markdown       # Markdown support for the browsable API.
pip install django-filter  # Filtering support
```
## Ejecutar para agregar el campo commission percentage a la base de datos
```
ALTER TABLE services 
ADD COLUMN commission_percentage DOUBLE NULL DEFAULT 0 AFTER cost;

```
[!NOTE]
Cambios realizados en models.py en la entidad Invoice_det de la app Procedure y en la plantilla invoice_details.html
Buscar en la base de datos los servicios que comienzen con 0