from __future__ import division, print_function

from template_generator import template_generator

def template_generator_factory(beamline, data_collection_info):

  if beamline == 'ixx':
    return template_generator(beamline, data_collection_info)

if __name__ == '__main__':
  generator = template_generator_factory('ixx', { })
  print(generator())
