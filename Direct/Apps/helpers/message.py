from django.http import JsonResponse, HttpResponse


class MessageResponse:
    def __init__(self, data={}, description=''):
        if data is None:
            data = {}
        self.data = data
        self.description = description

    def success(self):
        message = self.message(self.description, 'success')
        data = JsonResponse({'message': message, 'data': self.data})
        return self.result(data, 200)

    def warning(self):
        message = self.message(self.description, 'warning')
        data = JsonResponse({'message': message, 'data': self.data})
        return self.result(data, 400)

    def error(self):
        message = self.message(self.description, 'error')
        data = JsonResponse({'message': message, 'data': self.data})
        return self.result(data, 500)
    @staticmethod
    def message(description, type_message):
        return {'description': description, 'type': type_message}

    @staticmethod
    def result(response, status=200):
        return HttpResponse(response, content_type='application/json', status=status)

