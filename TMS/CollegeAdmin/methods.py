def sendBackgroundTask(celeryTaskMethod, *args):
    celeryTaskMethod.delay(*args)
