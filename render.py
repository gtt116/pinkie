import os
import json

import jinja2


class BaseRender(object):

    def __init__(self, template):
        self._init_env()
        self._template = template

    def _init_env(self):
        pwd = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(pwd, 'template')
        loader = jinja2.FileSystemLoader(template_dir)
        self.env = jinja2.Environment(loader=loader)

    def render_to_file(self, file_name=None):
        if not file_name:
            file_name = 'build/%s' % self._template

        with file(file_name, 'w') as output:
            output.write(self.render_to_html())

    def get_template(self):
        return self.env.get_template(self._template)


class CounterRender(BaseRender):

    def __init__(self):
        super(CounterRender, self).__init__('count_stats.html')
        # Key is legend, value is data
        self.datas = {}

    def add_stats(self, legend, data):
        self.datas[legend] = json.dumps(data)

    def render_to_html(self):
        template = self.get_template()
        return template.render(datas=self.datas)


class CompareRender(BaseRender):

    def __init__(self):
        super(CompareRender, self).__init__('compare.html')
        self._legends = []
        self._means = []
        self._medians = []
        self._modes = []

    def add_stats(self, legend, mean, median, mode):
        self._legends.append(legend)
        self._means.append(mean)
        self._medians.append(median)
        self._modes.append(mode)

    def render_to_html(self):
        template = self.get_template()
        return template.render(legends=self._legends,
                               means=self._means,
                               medians=self._medians,
                               modes=self._modes)
