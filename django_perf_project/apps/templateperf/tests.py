import inspect

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

        def f():
            self.render_template("child.html")
        self.run_benchmark(name, self.xsmall_iterations, f)

    def test_render_child_no_extends(self):
        name = inspect.currentframe().f_code.co_name[5:]

        def f():
            self.render_template("child_no_extends.html")
        self.run_benchmark(name, self.xsmall_iterations, f)

    def test_render_base(self):
        name = inspect.currentframe().f_code.co_name[5:]

        def f():
            self.render_template("base.html")
        self.run_benchmark(name, self.xsmall_iterations, f)

    def test_render_base_no_extends(self):
        name = inspect.currentframe().f_code.co_name[5:]

        def f():
            self.render_template("base_no_extends.html")
        self.run_benchmark(name, self.xsmall_iterations, f)
