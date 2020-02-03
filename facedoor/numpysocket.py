#makin 2019
import socket
import numpy as np
from io import BytesIO
from threading import Thread

def receive_np(port=8881,verbose=False):
    server_socket=socket.socket() 
    server_socket.bind(('',port))
    server_socket.listen(1)
    if verbose:print('waiting for a connection...')
    client_connection,client_address=server_socket.accept()
    if verbose:print('connected to ',client_address[0])
    ultimate_buffer=b''
    while True:
        receiving_buffer = client_connection.recv(1024)
        if not receiving_buffer: break
        ultimate_buffer+= receiving_buffer
    final_ndarray_data=np.load(BytesIO(ultimate_buffer))['frame']
    client_connection.close()
    server_socket.close()
    if verbose:print ('frame received')
    return final_ndarray_data

def send_np(ndarray_data, server_address='127.0.0.1',port=8881,verbose=False):
    if not isinstance(ndarray_data,np.ndarray):
        if verbose:print ('not a valid numpy ndarray_data')
        return
    client_socket=socket.socket()
    try:
        client_socket.connect((server_address, port))
        if verbose:print ('Connected to %s on port %s' % (server_address, port))
    except socket.error as e:
        if verbose:print ('Connection to %s on port %s failed: %s' % (server_address, port, e))
        return
    f = BytesIO()
    np.savez_compressed(f,frame=ndarray_data)
    f.seek(0)
    out = f.read()
    client_socket.sendall(out)
    client_socket.shutdown(1)
    client_socket.close()
    if verbose:print ('ndarray_data sent')

"""
asynchronously listening numpy ndarray and store data to current_data
using threading.Thread, which means runs in the same interpreter & process as the instantiator. instance.current_data can be accessed from the instantiator
"""
class AsyncReceiver(Thread):
    def __init__(self,parent=None, port=8881):
        super().__init__(parent)
        self.port = port
        self.daemon = True
        self.current_data = None #the data received can be read here
        self.countstamp = 0 #countstamp increased (+= 1) for each changes in current_data
        self.start()
    
    def run(self):
        while True:
            t = receive_np(self.port,verbose=True)
            self.current_data = t
            self.countstamp += 1
            print('received #{}'.format(self.countstamp))



if __name__=="__main__":
    import unittest
    import time
    class TestSendReceive(unittest.TestCase):
        def test_send(self):
            receiver = AsyncReceiver(port=9000)
            time.sleep(1)
            data = np.ndarray(shape=(4,), dtype=np.uint8, buffer=bytearray([1,2,3,4]))
            send_np(data,port=9000)
            time.sleep(1)
            self.assertEqual(receiver.current_data[0],1)
            self.assertEqual(receiver.current_data[3],4)
        
    unittest.main()