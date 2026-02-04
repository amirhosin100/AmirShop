from redis import Redis
from django.conf import settings



class SetIpMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        redis_settings = settings.CACHES['default']

        addr = redis_settings['LOCATION'].split('//')[1].split(':')
        host = addr[0]
        port = addr[1]

        self.redis = Redis(
            host=host,
            port=port,
            decode_responses=True,
        )

    def __call__(self, request):

        self.redis.sadd(":user_ips",request.META['REMOTE_ADDR'])
        response = self.get_response(request)

        return response
