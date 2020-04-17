
import re

# https://stackoverflow.com/questions/1175208
def camel_to_snake(name):
  name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
  return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower().replace('__', '_')

class NetworkBuildException(Exception):
  node_id = None
  
  def __init__(self, node_id=None):
    super().__init__()
    self.node_id = node_id

edge_key = lambda id1, id2: tuple(sorted([id1, id2]))

