import asyncio
import sys
import socketio
import time

sio = socketio.Client()


@sio.event
def connect():
    print('connected')
    result = sio.call('sum', {'numbers': [1, 2]})
    print(result)


def test_response(args):
    print('on_test_response', args['data'])

def is_spy_response():
    print("is spy response")

def test_send():
    print("test send")


@sio.event
def disconnect():
    print('disconnected')


def main(username):
    sio.connect('http://localhost:5000')
    # sio.connect('http://localhost:5000',
    #             headers={'X-Username': username})
    time.sleep(2)
    # sio.on('propose_mission', test_response)
    sio.emit('test')
    sio.on('test_send', is_spy_response)
    # sio.emit('propose_mission', {'data': 'test'})


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)