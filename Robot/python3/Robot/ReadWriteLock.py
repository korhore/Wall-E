'''
Created on 10.04.2020
Updated on 10.04.2020
@author: reijo.korhonen@gmail.com

Lock class to protect all methods handling Sensation cache.
This from O'Reilly. We need read and write lock solution and this is it.

'''

import threading

'''
Lock class to protect all methods handling Sensation cache.
This from O'Reilly. We need read and write lock solution and this is it.
'''
    
class ReadWriteLock:
    """ A lock object that allows many simultaneous "read locks", but
    only one "write lock." """
    
    def __init__(self):
        self._read_ready = threading.Condition(threading.Lock(  ))
        self._readers = 0
    
    def acquireRead(self):
        """ Acquire a read lock. Blocks only if a thread has
        acquired the write lock. """
        self._read_ready.acquire(  )
        try:
            self._readers += 1
        finally:
            self._read_ready.release(  )
    
    def releaseRead(self):
        """ Release a read lock. """
        self._read_ready.acquire(  )
        try:
            self._readers -= 1
            if not self._readers:
                    self._read_ready.notifyAll(  )
        finally:
            self._read_ready.release(  )
    
    def acquireWrite(self):
        """ Acquire a write lock. Blocks until there are no
        acquired read or write locks. """
        self._read_ready.acquire(  )
        while self._readers > 0:
            self._read_ready.wait(  )
    
    def releaseWrite(self):
        """ Release a write lock. """
        self._read_ready.release(  )    
