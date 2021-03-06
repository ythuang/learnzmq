"""

   Multithreaded Hello World server

   Author: Guillaume Aubert (gaubert) <guillaume(dot)aubert(at)gmail(dot)com>

"""
import time
import threading
import zmq
import msgpack

def worker_routine(worker_url, context):
    """ Worker routine """

    # Socket to talk to dispatcher
    socket = context.socket(zmq.REP)

    socket.connect(worker_url)

    while True:
        msg = msgpack.unpackb(socket.recv())
        print "Received: Client %d sent message #%d with text:[%s] " % ( msg['id'], msg['req_id'], msg['msg'])
        # do some 'work'
        time.sleep(1)
        msg['msg'] = "World"
        socket.send(msgpack.packb(msg))


def main():
    """ server routine """

    url_worker = "inproc://workers"
    url_client = "tcp://*:5555"

    # Prepare our context and sockets
    context = zmq.Context(1)

    # Socket to talk to clients
    clients = context.socket(zmq.ROUTER)
    clients.bind(url_client)

    # Socket to talk to workers
    workers = context.socket(zmq.DEALER)
    workers.bind(url_worker)

    # Launch pool of worker threads
    for i in range(5):
        thread = threading.Thread(target=worker_routine, args=(url_worker, context, ))
        thread.start()

    zmq.device(zmq.QUEUE, clients, workers)

    # We never get here but clean up anyhow
    clients.close()
    workers.close()
    context.term()


if __name__ == "__main__":
    main()

