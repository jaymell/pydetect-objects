import abc

class DB(metaclass=abc.ABCMeta):

  @abc.abstractmethod
  def __init__(self, db):
    pass

  @abc.abstractmethod
  def put_record(self, record):
    pass
