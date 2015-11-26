import os
from datetime import timedelta, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_perf_project.settings')
import django
django.setup()

from django.utils import timezone

from django_perf_project.apps.ormperf.models import Question, Choice
from django_perf_project.apps.botbotperf.models import ChatBot, Channel, Log


def create_questions_and_choices():
    d0 = timezone.datetime(2015, 10, 21, tzinfo=timezone.utc)
    for i in range(1000):
        q = Question(
            question_text="foo bar %d" % i, pub_date=d0 + timedelta(seconds=i))
        q.save()
        for k in range(3):
            c = Choice(
                question=q, choice_text="aaaaaaaaaaaa %d %d" % (i, k), votes=i)
            c.save()

def populate_botbot(slug, start_date):
    chatbot = ChatBot.objects.create(
        is_active=True, server="irc.example.net:6697",
        nick="foo", password="bar",slug="thechatbot")
    channel = Channel.objects.create(
        chatbot=chatbot,
        status=Channel.ACTIVE,
        slug=slug,
        is_public=True)

    for d in [start_date - timedelta(days=1),
              start_date,
              start_date + timedelta(days=1)]:
        for i in range(500):
            Log.objects.create(
                bot=chatbot, channel=channel,
                timestamp=d + timedelta(seconds=i*10),
                nick=u"foo{0}".format(i % 2),
                text=u"message {0}".format(i),
                command="PRIVMSG",)


if __name__ == '__main__':
    create_questions_and_choices()
    populate_botbot("pypy", date(2015, 4, 1))
