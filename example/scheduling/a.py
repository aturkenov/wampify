from wampify import Wampify, scheduler


wampify = Wampify(
    debug=False,
    urip='com.example',
    router={ 'url': 'ws://localhost:8000/private' },
    wamps={
        'realm': 'master',
        'authid': 'a',
        'show_registered': True,
        'show_subscribed': True
    }
)


scheduler.mount(wampify)


def a():
    print('a')


async def b():
    print('b')


wampify.schedule.every(2).seconds.do(a)
wampify.schedule.every(3).seconds.do(b)


if __name__ == '__main__':
    wampify.run()
