import threading
import time

import core.session

''' Periodically checks if sessions are alive '''
class Extant(object):

    def __init__(self, shell):
        self.shell = shell
        self.check_alive_timer = None
        self.check()

    def check(self):
        if self.check_alive_timer is not None:
            self.check_alive_timer.cancel()

        self.check_alive_timer = threading.Timer(1.0, self.check)
        self.check_alive_timer.daemon = True
        self.check_alive_timer.start()

        now = time.time()

        max_delta = 10

        for stager in self.shell.stagers:
            for session in stager.sessions:
                delta = now - session.last_active
                #delta = datetime.timedelta(seconds=int(delta))

                if session.status == core.session.Session.ALIVE:
                    if delta > max_delta:
                        self.shell.play_sound('TIMEOUT')
                        session.set_dead()
                else:
                    if delta < max_delta:
                        self.shell.play_sound('RECONNECT')
                        session.set_reconnect()

        # Job repeater
        remove_jobs = []

        for rjob in self.shell.repeatjobs:
            if self.shell.repeatjobs[rjob][0] > 0:
                self.shell.repeatjobs[rjob][0] = self.shell.repeatjobs[rjob][0]- 1
                continue

            zombie = [o.value for o in self.shell.repeatjobs[rjob][6].options if o.name == "ZOMBIE"][0]
            self.shell.repeatjobs[rjob][7].dispatch(self.shell.repeatjobs[rjob][2], self.shell.repeatjobs[rjob][3], False, zombie)
            self.shell.repeatjobs[rjob][0] = self.shell.repeatjobs[rjob][4]

            if self.shell.repeatjobs[rjob][1] == 0:
                continue
            if self.shell.repeatjobs[rjob][1] > 2:
                self.shell.repeatjobs[rjob][1] = self.shell.repeatjobs[rjob][1] - 1
                continue

            remove_jobs.append(rjob)

        if remove_jobs:
            tmp = dict(self.shell.repeatjobs)
            for r in remove_jobs:
                del tmp[r]
            self.shell.repeatjobs = tmp