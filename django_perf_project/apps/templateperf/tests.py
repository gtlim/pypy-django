import inspect
import time

from django.template import loader, RequestContext
from django_perf_project.apps.core.tests import PerfoTestCase


class TemplatePerfTest(PerfoTestCase):

    def setUp(self):
        super(TemplatePerfTest, self).setUp()
        self.params = {'title': 'title', 'range': range(100)}

    def render_template(self, template_name):
        tmpl = loader.get_template(template_name)
        ctx = RequestContext({}, self.params)
        return tmpl.render(ctx)

    def test_render_child(self):
        name = inspect.currentframe().f_code.co_name[5:]
        print
        iteration = 0
        for n in self.small_iterations:
            start = time.time()
            for i in xrange(int(n)-1):
                iteration += 1
                self.render_template("child.html")
            duration = time.time() - start
            start = time.time()
            iteration += 1
            duration = time.time() - start
            self.render_template("child.html")
            last_operation = time.time() - start
            self.report_run(name, n, duration, last_operation)

    def test_render_child_no_extends(self):
        name = inspect.currentframe().f_code.co_name[5:]
        print
        iteration = 0
        for n in self.xsmall_iterations:
            start = time.time()
            for i in xrange(int(n)-1):
                iteration += 1
                self.render_template("child_no_extends.html")
            duration = time.time() - start
            start = time.time()
            iteration += 1
            duration = time.time() - start
            self.render_template("child_no_extends.html")
            last_operation = time.time() - start
            self.report_run(name, n, duration, last_operation)

    def test_render_base(self):
        name = inspect.currentframe().f_code.co_name[5:]
        print
        iteration = 0
        for n in self.xsmall_iterations:
            start = time.time()
            for i in xrange(int(n)-1):
                iteration += 1
                self.render_template("base.html")
            duration = time.time() - start
            start = time.time()
            iteration += 1
            duration = time.time() - start
            self.render_template("base.html")
            last_operation = time.time() - start
            self.report_run(name, n, duration, last_operation)

    def test_render_base_no_extends(self):
        name = inspect.currentframe().f_code.co_name[5:]
        print
        iteration = 0
        for n in self.xsmall_iterations:
            start = time.time()
            for i in xrange(int(n)-1):
                iteration += 1
                self.render_template("base_no_extends.html")
            duration = time.time() - start
            start = time.time()
            iteration += 1
            duration = time.time() - start
            self.render_template("base_no_extends.html")
            last_operation = time.time() - start
            self.report_run(name, n, duration, last_operation)
