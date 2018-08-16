from __future__ import division, print_function

from dls_template_generator import dls_template_generator

def template_generator_factory(beamline, data_collection_info):

  if beamline == 'ixx':
    return dls_template_generator(beamline, data_collection_info)

if __name__ == '__main__':
  example_dc_info = {'goniometer':{'axes':{
    'omega':{'axis':(1,0,0), 'depends_on':'.'},
    'chi':{'axis':(0,-1,0), 'depends_on':'omega'},
    'phi':{'axis':(1,0,0), 'depends_on':'chi'}
    }
    }
    }

  generator = template_generator_factory('ixx', example_dc_info)
  print(generator())
