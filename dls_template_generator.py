from __future__ import division, print_function

from template_generator import template_generator

class dls_template_generator(template_generator):
  def __init__(self, beamline, data_collection_info):
    # prior knowledge - common things like detector x, y, z axes

    common = {'detector':{'name':'DECTRIS', 'fast':(1,0,0), 'slow':(0,-1,0),
      'axes':{
      'x':{'axis':(1,0,0), 'depends_on':'y'},
      'y':{'axis':(0,-1,0), 'depends_on':'z'},
      'z':{'axis':(0,0,-1), 'depends_on':'.'}
      }},
      'goniometer':{'axes':{
      'omega':{'axis':(1,0,0), 'depends_on':'.'}}}}

    self.recursive_update(common, data_collection_info)
    template_generator.__init__(self, beamline, common)
    return

  def source(self):
    '''Standard info as understood for Diamond single-crystal X-ray diffraction
    beam lines.'''

    header = '''_diffrn.id %s
_diffrn.crystal_id xtal
''' % self._beamline

    header += '''
loop_
_diffrn_source.diffrn_id
_diffrn_source.source
_diffrn_source.type
 %s synchrotron 'Diamond Light Source Beamline %s'
''' % (self._beamline, self._beamline.upper()) + '''
loop_
_diffrn_radiation.diffrn_id
_diffrn_radiation.wavelength_id
_diffrn_radiation.monochromator
_diffrn_radiation.polarizn_source_ratio
_diffrn_radiation.polarizn_source_norm
_diffrn_radiation.div_x_source
_diffrn_radiation.div_y_source
_diffrn_radiation.div_x_y_source
 %s WAVELENGTH1 'Si 111' 0.990 0.0 0.08 0.01 0.00
''' % self._beamline

    header += '''
loop_
_diffrn_radiation_wavelength.id
_diffrn_radiation_wavelength.wavelength
_diffrn_radiation_wavelength.wt
WAVELENGTH1 _wave_ 1
'''

    return header
