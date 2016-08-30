"""
MIT License

Copyright (c) 2016 Alex Bielen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
from modulefinder import ModuleFinder
import importlib.util as imp_util

promise_inner_func_name = 'promise_inner_2kaB122'


def load_qabbage_modules(file_paths):
    """
    Loads any promise functions defined in a file.
    :return:
    """
    promises = []
    def filter_out_bad_path(path):
        return 'qabbage_setup' not in path


    for file_path in filter(filter_out_bad_path, file_paths):
        spec = imp_util.spec_from_file_location('anything', file_path)
        foo = imp_util.module_from_spec(spec)
        spec.loader.exec_module(foo)

        for name in dir(foo):
            if name[0:2] != '__' and name != 'promise':
                obj = getattr(foo, name)
                if hasattr(obj, '__call__') and promise_inner_func_name in obj.__name__:
                    promises.append((name, obj))

    return promises


def find_all_qabbage_tasks(globals, exclude_tests=True):
    """
    Walks the directory and finds all of the scripts that import
    qabbage tasks.

    :return: file paths with qabbage tasks
    """

    all_files = []
    qabbage_files = []

    for root, dirs, files in os.walk("."):
        path = root.split('/')
        for file in files:
            _, file_extension = os.path.splitext(file)
            if file_extension == '.py':
                all_files.append(os.path.join(*path, file))

    finder = ModuleFinder()
    for file in filter(lambda x: 'test_' not in x, all_files):
        finder.run_script(file)
        for name, mod in finder.modules.items():
            if name == 'qabbage':
                qabbage_files.append(file)

    promises = load_qabbage_modules(qabbage_files)

    return promises


class Registry(object):
    """
    Called by the promise decorator; stores paths to tasks that
    are defined outside of the tasks file.

    Should always be a singleton!
    """

    def __init__(self, registry_namespace):
        self.registry_namespace = registry_namespace

    def add_task(self, name, task):
        self.registry_namespace[name] = task
