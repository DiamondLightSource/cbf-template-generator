from __future__ import division, print_function

from dls_template_generator import dls_template_generator

class i24_template_generator(dls_template_generator):
  def __init__(self, beamline, data_collection_info, mode='pin'):

    assert mode in ('tray', 'pin')

    if mode == 'pin':
      common = {'goniometer':{'axes':{
        'omega':{'axis':(0,1,0), 'depends_on':'.'}
      }}, 'detector':{'name':'DECTRIS PILATUS3 6M', 'axes':{
        'z':{'axis':(0,0,-1), 'depends_on':'.'}
      }, 'fast':(1,0,0), 'slow':(0,-1,0)}}
    elif mode == 'tray':
      common = {'goniometer':{'axes':{
        'omega':{'axis':(-1,0,0), 'depends_on':'.'}
      }}, 'detector':{'name':'DECTRIS PILATUS3 6M', 'axes':{
        'z':{'axis':(0,0,-1), 'depends_on':'.'}
      }, 'fast':(1,0,0), 'slow':(0,-1,0)}}
    else:
      # we cannot get to here anyway...
      raise RuntimeError, 'unknown mode %s' % mode

    self.recursive_update(common, data_collection_info)
    dls_template_generator.__init__(self, beamline, common)

    return
