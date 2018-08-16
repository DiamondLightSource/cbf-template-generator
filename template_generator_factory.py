from __future__ import division, print_function

from dls_template_generator import dls_template_generator
from i19_1_template_generator import i19_1_template_generator

def template_generator_factory(beamline, data_collection_info):

  if beamline == 'ixx':
    return dls_template_generator(beamline, data_collection_info)

  if beamline == 'i19-1':
    return i19_1_template_generator(beamline, data_collection_info)

if __name__ == '__main__':
  example_dc_info = {'detector':{'distance_mm':187.5}}

  import sys
  generator = template_generator_factory(sys.argv[1], example_dc_info)
  print(generator())
