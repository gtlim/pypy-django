from django.test import TestCase


class PerfoTestCase(TestCase):

    def setUp(self):
        self.iterations = [10, 1e2-10, 1e3-1e2,
                           1e4-1e3, 1e5-1e4, 1e6-1e5,
                           1e7-1e6]
        self.small_iterations = self.iterations[0:5]
        self.xsmall_iterations = self.iterations[0:4]

    def report_run(self, name, nb_iteration,
                   total_duration, last_iteration_duration):
        print u"{0:e}s avg per iteration for {1} (iterations={2}) -- last operation: {3:e}s".format((total_duration + last_iteration_duration)/nb_iteration, name, nb_iteration, last_iteration_duration)
