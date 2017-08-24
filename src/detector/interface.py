import abc

class ObjectDetector(metaclass=abc.ABCMeta):

  @abc.abstractmethod
  def __init__():
    pass

  @abc.abstractmethod
  def detect_objects(self, images):
    pass

