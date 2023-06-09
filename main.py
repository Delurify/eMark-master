import os
import glob
from website import create_app
from flask_apscheduler import APScheduler

#create app
app = create_app()

scheduler = APScheduler()

# This is to remove images or zipfiles that are submitted to the server
def job1():
    files = glob.glob("website/static/image/*")
    for f in files:
        os.remove(f)

    batches = glob.glob("website/static/image-batch/*")
    for f in batches:
        os.remove(f)

    zipfiles = glob.glob("website/static/zipfile/*")
    for f in zipfiles:
        os.remove(f)

if __name__ == '__main__':
    # run the server cleaning process every morning 4am
    scheduler.add_job(id='Job1', func=job1, trigger='cron', day='*', hour='4')
    scheduler.start()
    
    app.run(debug=True)
    