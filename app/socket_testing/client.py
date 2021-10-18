import asyncio
import sys
import socketio
import time

sio = socketio.Client(logger=True, engineio_logger=True)


@sio.event
def connect():
    print('connected')


def test_response(args):
    print('on_test_response', args['data'])


@sio.on('test_send')
def test_send():
    print("test send")


@sio.event
def disconnect():
    print('disconnected')


def main(username):
    sio.connect('http://localhost:5000')
    # sio.connect('http://localhost:5000',
    #             headers={'X-Username': username})
    sio.wait()


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)