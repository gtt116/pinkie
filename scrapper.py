# -*-coding: utf8 -*-

import requests
import logging

logging.basicConfig()
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class Position(object):

    def __init__(self, raw_json):
        self.city = raw_json['city']
        self.company_id = raw_json['companyId']
        self.company_name = raw_json['companyName']
        self._salary = raw_json['salary']  # string, '3k-6k'
        self.position_id = raw_json['positionId']
        self.position_name = raw_json['positionName']

    def salary_range(self):
        if u'\u4ee5\u4e0a' in self._salary:
            # 4K以上
            tokens = self._salary.split(u'\u4ee5\u4e0a')
            floor = int(tokens[0].lower().replace('k', ''))
            ceil = floor
        else:
            # 3k-4k
            tokens = self._salary.split('-')

            if len(tokens) != 2:
                raise ValueError(self._salary.encode('utf8'))

            floor = int(tokens[0].lower().replace('k', ''))
            ceil = int(tokens[1].lower().replace('k', ''))

        return range(floor, ceil + 1)

    def __repr__(self):
        return '%s:%s' % (self.position_id, self.position_name)


class Stats(object):

    def __init__(self):
        # Key is salary, e.g. 3. unit is K.
        self._postions = {}

        # Init salarys, current max to 60
        for salary in xrange(1, 61):
            self._postions[salary] = 0

    def add_position(self, postion):
        for salary in postion.salary_range():
            count = self._postions.setdefault(salary, 0)
            count += 1
            self._postions[salary] = count

    def add_bulk_position(self, postion_list):
        for pos in postion_list:
            try:
                self.add_position(pos)
            except ValueError as ex:
                LOG.error(ex)

    def get_stats(self):
        return self._postions

    def to_csv(self, file_name=None):
        LOG.info("Dump to %s" % file_name)
        result = []
        for salary, count in self._postions.iteritems():
            line = '%s,%s\r\n' % (salary, count)
            result.append(line)

        if file_name:
            with file(file_name, 'w') as output:
                output.writelines(result)

        return result


class Lagou(object):

    def __init__(self, url='http://www.lagou.com/jobs/positionAjax.json'):
        self.url = url
        self._positions = []

    def process_keyword(self, keyword):
        # Get first page to indicate total page count.
        json_body = self._get_page(1, keyword)
        total_page_count = json_body['content']['totalPageCount']
        self._parse_page(json_body)
        # Get result pages
        for page in xrange(2, total_page_count + 1):
            json_body = self._get_page(page, keyword)
            self._parse_page(json_body)

    @property
    def positions(self):
        return self._positions

    def _data(self, page_number, kw):
        data_pattern = 'first=false&pn=%(pn)s&kd=%(kw)s&ps=20'
        data = data_pattern % {'pn': page_number, 'kw': kw}
        return data

    def _get_page(self, page_number, kw):
        data = self._data(page_number, kw)
        headers = {'Content-Type':
                   'application/x-www-form-urlencoded; charset=UTF-8'}
        response = requests.post(self.url, data, headers=headers)
        LOG.info("Loading %s" % data)
        return response.json()

    def _add_postion(self, position):
        self._positions.append(position)

    def _parse_page(self, json_body):
        for pos_json in json_body['content']['result']:
            pos = Position(pos_json)
            self._add_postion(pos)


def save_to_csv(kw, filename=None):
    if not filename:
        filename = kw
    stats = Stats()
    lagou = Lagou()
    lagou.process_keyword(kw)
    stats.add_bulk_position(lagou.positions)
    stats.to_csv('%s.csv' % filename.lower())


if __name__ == '__main__':
    save_to_csv('web前端', 'web')
    save_to_csv('运维开发工程师', 'devops')
    save_to_csv('Python')
    save_to_csv('Java')
    save_to_csv('Ruby')
    save_to_csv('Node.js')
