from wampify.core.wampify import Wampify
from wampify.core.story import *


wampify = Wampify(
    settings={
        'debug': False,
        'wamp': {
            'domain': 'com.example',
            'url': 'ws://127.0.0.1:8080/private',
            'session': {
                'realm': 'example',
                'show_registered': True,
                'show_subscribed': True
            }
        }
    }
)


async def background_task():
    print('im here')


@wampify.register
async def asap():
    story = get_current_story()
    story.background_tasks.add(background_task)
    print('background task pushed to queue')


if __name__ == '__main__':
    wampify.run()

