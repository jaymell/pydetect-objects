import datetime

class DBRecord:
  def __init__(self, camera_id, time, detections):
    self.id = camera_id
    self.time = time
    self.detections = detections

  @property
  def time(self):
    return self._time

  @time.setter
  def time(self, time):
    epoch = datetime.datetime.utcfromtimestamp(0)
    self._time = (time - epoch).total_seconds() * 1000.0