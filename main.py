from __init__ import create_app
from flask_apscheduler import APScheduler

app = create_app()
aps = APScheduler()


class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': 'routes:sync_data',
            'args': (),
            'trigger': 'cron',
            'day': '*',
            'hour': '*',
            'minute': '0,10,20,30,40,50',
            'second': '0'
        },
        {
            'id': 'job2',
            'func': 'routes:sync_data_wallet',
            'args': (),
            'trigger': 'cron',
            'day': '*',
            'hour': '*',
            'minute': '0',
            'second': '0'
        }
    ]
    SCHEDULER_API_ENABLED = True


app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

if __name__ == '__main__':
    app.run(use_reloader=False)

