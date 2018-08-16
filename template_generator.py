from __future__ import division, print_function

class template_generator(object):
  '''Base class for template generation - will need to override with useful
  parameters to create a custom imgCIF template for a given beamline.'''

  def __init__(self, beamline, data_collection_parameters):
    self._beamline = beamline
    self._data_collection_parameters = data_collection_parameters

    return

  def __call__(self):
    return '\n'.join([self.header(), self.source(), self.detector(),
                      self.goniometer(), self.scan(), self.tailer()])

  def header(self):
    return ''

  def source(self):
    return ''

  def detector(self):
    return ''

  def goniometer(self):
    return ''

  def scan(self):
    return ''

  def tailer(self):
    return ''

  # helper functions

  def goniometer_info(self):
    return self._data_collection_parameters['goniometer']
