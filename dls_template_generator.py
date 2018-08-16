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

  def header(self):
    import datetime
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    gi = self.goniometer_info()
    di = self.detector_info()

    header = '''###CBF: VERSION 1.1
# Template auto generated at %s
# DECTRIS translation table:
@ Exposure_time     _expt_
@ Exposure_period   _expp_
@ Omega             _omega_
@ Omega_increment   _domega_
@ Timestamp         _timestamp_
@ Count_cutoff      _cutoff_
@ Compression_type  _compress_
@ X_dimension       _wide_
@ Y_dimension       _high_
@ Wavelength        _wave_
''' % date_str

    if 'chi' in gi['axes']:
      header += '''@ Chi               _chi_
@ Chi_increment     _dchi_
'''

    if 'phi' in gi['axes']:
      header += '''@ Phi               _phi_
@ Phi_increment     _dphi_
'''

    if 'kappa' in gi['axes']:
      header += '''@ Kappa               _kappa_
@ Kappa_increment     _dkappa_
'''

    if '2theta' in di['axes']:
      header += '''@ Detector_2theta   _2theta_
'''

    header += '''--- End of preamble
'''

    return header

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

    # other homeless header junk - not sure about the structure being
    # ideal here, perhaps worth refactoring?

    gi = self.goniometer_info()
    di = self.detector_info()

    header += '''
loop_
_diffrn_measurement.diffrn_id
_diffrn_measurement.id
_diffrn_measurement.number_of_axes
_diffrn_measurement.method
_diffrn_measurement.sample_detector_distance
 %s GONIOMETER %d rotation %.2f
''' % (self._beamline, len(gi['axes']), di['distance_mm'])

    header += '''
loop_
_diffrn_radiation_wavelength.id
_diffrn_radiation_wavelength.wavelength
_diffrn_radiation_wavelength.wt
 WAVELENGTH1 _wave_ 1
'''

    return header
