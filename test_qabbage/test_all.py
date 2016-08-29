import qabbage as q
from celery_test.tasks import longtime_add, exception_thrower


def good_result(vals):
    return sum(vals)


def bad_result(vals):
    for x in vals:
        print(x)


def test_that_q_all_works_correctly():
    nice = q.all(longtime_add.s(x, y) for x, y in zip(range(10), range(10))) \
        .then(good_result, bad_result)

    assert nice == 90
