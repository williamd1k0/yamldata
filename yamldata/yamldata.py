
"""
MIT License

Copyright (c) 2016 William Tumeo

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
from zipfile import ZipFile
import yaml



def recursive_read(dicts:dict, path:list) -> dict:
    if path[0] in dicts:
        if len(path) <= 1:
            return dicts
        else:
            return recursive_read(dicts[path[0]], path[1:])

def recursive_read_last(dicts:dict, path:list) -> object:
    return recursive_read(dicts, path)[path[-1]]


def recursive_create(dicts:dict, path:list) -> dict:
    if not path[0] in dicts:
        dicts[path[0]] = dict()
    if len(path) <= 1:
        return dicts
    else:
        return recursive_create(dicts[path[0]], path[1:])


class ZipBackup(object):

    def __init__(self, path, backup_dir='.backup'):
        self.path = path
        self.backup_dir = backup_dir
        self.last_backup = None

    def new_backup(self) -> None:
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

        count = len(os.listdir(self.backup_dir))
        self.last_backup = os.path.join(self.backup_dir, "backup[{0}].zip".format(count))
        zf = ZipFile(self.last_backup, "w")
        for dirname, subdirs, files in os.walk(self.path):
            zf.write(dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename))
        zf.close()


class YamlData(object):

    def __init__(self, path, path_sp='/', data_sp='.', backup=None):
        self.path = path
        self.path_sp = path_sp
        self.data_sp = data_sp
        self.backup = backup if isinstance(backup, ZipBackup) else ZipBackup(path)

        if not os.path.exists(self.path):
            os.makedirs(self.path)


    def __repr__(self) -> str:
        path = []
        for dirname, subdirs, files in os.walk(self.path):
            path.append([dirname, subdirs, files])
        return str(path)

    
    def backup_data(self) -> None:
        self.backup.new_backup()


    def __getitem__(self, item:str) -> object:
        paths = item.split(self.path_sp)
        if len(paths) <= 1:
            return
        path = os.path.join(self.path, paths[-2]+'.yml')
        if len(paths) >= 3:
            path = os.path.join(self.path, '/'.join(paths[:-2]), paths[-2]+'.yml')

        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as data:
                data_dict = yaml.load(data.read())
                if not isinstance(data_dict, dict):
                    return None

            data_path = paths[-1].split(self.data_sp)
            return recursive_read_last(data_dict, data_path)
        return None


    def __setitem__(self, item:str, value:object) -> None:
        paths = item.split(self.path_sp)
        if len(paths) <= 1:
            return
        path = os.path.join(self.path, paths[-2]+'.yml')
        if len(paths) >= 3:
            path = '/'.join(paths[:-2])
            if not os.path.exists(os.path.join(self.path, path)):
                os.makedirs(os.path.join(self.path, path))
            path = os.path.join(self.path, path, paths[-2]+'.yml')
        
        data_dict = dict()
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as data:
                data_dict = yaml.load(data.read())
                if not isinstance(data_dict, dict):
                    data_dict = dict()

        data_path = paths[-1].split(self.data_sp)
        data_edit = recursive_create(data_dict, data_path)
        data_edit[data_path[-1]] = value

        with open(path, 'w', encoding='utf-8') as data:
            data.write(yaml.dump(data_dict, default_flow_style=False))



if __name__ == '__main__':

    data = YamlData('test')
    data['configs/env/python'] = 'python 3.4'
    data.backup_data()
    print(data)