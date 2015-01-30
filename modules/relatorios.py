# coding=utf-8
from csv import DictWriter

from gluon import current, URL, A


__author__ = 'diogomartins'


class DictUnicodeProxy(object):
        def __init__(self, d):
            self.d = d
        def __iter__(self):
            return self.d.__iter__()
        def get(self, item, default=None):
            i = self.d.get(item, default)
            if isinstance(i, unicode):
                return i.encode('latin1')
            return i


def salvar(content, headers, filename):
    with open(current.request.folder + 'static/' + filename + '.csv', 'w') as outfile:
        writer = DictWriter(outfile, headers)
        writer.writeheader()
        for p in content:
            writer.writerow(DictUnicodeProxy(p))
        return A("Baixar relatório", _href=URL('static', 'deferidos.csv?attachment'))