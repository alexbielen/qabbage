# Qabbage
Tools for making Celery and RabbitMQ a joy to work with in Python 3.5

Qabbage aims to make developing software with RabbitMQ and Celery as easy as possible. To that end, it includes
a more flexible Celery task discovery mechanism, a set of scaffolding tools, a python wrapper over `rabbitmqctl` and
a more modern async api based on Kriskowal's Q library for JavaScript.

### qabbage_setup.py

After installing qabbage, create the following file in the root directory of your Python project.


```python
# qabbage_setup.py
from celery import Celery

from qabbage.registry import find_and_register_qabbage_tasks
from qabbage.promise import promise_maker

app = Celery('qabbage_setup',
             broker='amqp://guest:password$@localhost/test',
             backend='rpc://',
             include=['qabbage_setup'])

promise = promise_maker(app)
tasks = find_and_register_qabbage_tasks(globals())


if __name__ == '__main__':
    app.start()
```
Set the broker connection string to your environment's own.

`qabbage_setup.py` is responsible for
        1) Defining a promise decorator that can be used anywhere throughout your project
        2) Finding and 'registering' the aforementioned promises so that they can be used as Celery tasks.


### promises
The promise decorator marks a function that can be sent to a queue and then processed by a separate worker process.
```python
# first_qabbage_promise.py
from fractions import gcd

from qabbage_setup import promise

@promise
def get_gcd(x, y):
    return gcd(x, y)
```
When `find_and_register_qabbage_tasks` runs in `qabbage_setup.py` it looks through all of the files in the project and
registers any qabbage promises in the `qabbage_setup.py` namespace. When Celery is run with `qabbage_setup.py` as a parameter
it is able to work with any promise defined in the project as though it was explictly registered with Celery.

###q.all
Now that we have a promise defined we can use qabbage to send it to the queue for processing.
```python
# send_to_queues.py
import qabbage as q

from first_qabbage_promise import get_gcd

def good_path(res):
    print(res)
    return res

def bad_path(err):
    print(err)

if __name__ == '__main__':
    result = q.all(get_gcd(x, y) for x, y in zip(range(1000), range(1000))).then(
        good_path, bad_path
    )

    print(result)
```
Lastly, start up your celery worker by navigating to the root directory of your project and running the following
from the command line.
`celery -A qabbage_setup worker --loglevel=info`

In a separate process from the Celery worker run:
`python send_to_queues.py`

Voila!