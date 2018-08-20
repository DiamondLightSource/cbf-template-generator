from __future__ import division, print_function

from dls_template_generator import dls_template_generator

class i04_template_generator(dls_template_generator):
  def __init__(self, beamline, data_collection_info):

    # if data_collection_info is missing informtion, add it - do this by
    # having a dictionary of prior results which will get overwritten by
    # info in update()

    common = {'goniometer':{'axes':{
      'omega':{'axis':(1,0,0), 'depends_on':'.'},
      'chi':{'axis':(0,0,-1), 'depends_on':'omega'},
      'phi':{'axis':(1,0,0), 'depends_on':'chi'}
      }}, 'detector':{'name':'DECTRIS PILATUS 6M', 'axes':{
        'z':{'axis':(0,0,-1), 'depends_on':'.'}
      }, 'fast':(0,1,0), 'slow':(1,0,0)}}

    self.recursive_update(common, data_collection_info)
    dls_template_generator.__init__(self, beamline, common)

    return
