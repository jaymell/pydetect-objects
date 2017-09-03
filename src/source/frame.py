import datetime

class EncodedFrame:
  def __init__(self, camera_id, image, width, height, time=datetime.datetime.utcnow()):
    self.id = camera_id
    self._image = image
    self._time = time
    self.width = width
    self.height = height
    self.image_type = 'JPEG'

  @property
  def image(self):
    return self._image

  @image.setter
  def image(self, image):
    self._image = image

  @property
  def time(self):
    return self._time

  @time.setter
  def time(self, time):
    self._time = time

