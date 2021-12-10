from wampify.core.wampify import Wampify
from wampify.core.wamp import WAMPBSession
from wampify.core.story import get_current_story
from wampify.service.client_imc import client_imc
from pydantic import BaseModel


class TestA(BaseModel):

    def test(self, a, b: int, c = None, d: int = None):
        return {
            'a': a,
            'b': b,
            'c': c,
            'd': d
        }


instance = TestA()

async def updata_client_store(data):
    story = get_current_story()
    available = ('en', 'ru', 'kz')
    default = 'en'
    requested = data.get('language', default)
    if not requested in available:
        requested = default
    client_imc[story.client] = {
        'language': requested
    }


async def stest():
    story = get_current_story()
    print(f'client_imc {story.client_imc}')


class CustomWAMPSession(WAMPBSession):

    def onChallenge(self, challenge):
        return 'secret'


# 'RC.error.debug': True,
# 'RC.error.domain': 'com.example',
# 'WAMP.domain': 'com.example',
# 'WAMP.session.factory': CustomWAMPSession,
# 'WAMP.session.realm': 'test',
# 'WAMP.session.authid': 'private',
# 'WAMP.session.authmethods': ['ticket'],

application = Wampify(
    settings={
        'debug': True,
        'wamp': {
            'domain': 'com.example.test',
            'session': {
                'factory': CustomWAMPSession,
                'realm': 'test',
                'authid': 'private',
                'authmethods': ['ticket'],
            }
        }
    }
)




application.add_subscribe('store', updata_client_store)

application.add_register('rtest', instance.test)
application.add_subscribe('stest', stest)


session_factory = application.wamp.session_factory
