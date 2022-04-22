from wampify import Wampify, background_task
from wampify.story import *


wampify = Wampify(
    debug=False,
    preuri='com.example',
    router={ 'url': 'ws://127.0.0.1:8080/private' },
    wamps={
        'realm': 'example',
        'show_registered': True,
        'show_subscribed': True
    }
)


background_task.mount(wampify)


async def btask():
    print('im here')


@wampify.register
async def asap():
    story = get_current_story()
    story._background_tasks_.add(btask)
    print('background task pushed to queue')


if __name__ == '__main__':
    wampify.run()

