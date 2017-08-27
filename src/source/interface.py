import abc

class Source(metaclass=abc.ABCMeta):

  @abc.abstractmethod
  def get_images(self, images):
    pass

