from __future__ import division, print_function

header_boiler_plate = '''###CBF: VERSION 1.1
# Auto-generated full CBF image header template
# DECTRIS translation table
@ Exposure_time     _expt_
@ Exposure_period   _expp_
@ Omega             _omega_
@ Omega_increment   _domega_
@ Chi               _chi_
@ Chi_increment     _dchi_
@ Phi               _phi_
@ Phi_increment     _dphi_
@ Timestamp         _timestamp_
@ Count_cutoff      _cutoff_
@ Compression_type  _compress_
@ X_dimension       _wide_
@ Y_dimension       _high_
@ Wavelength        _wave_
--- End of preamble
# All subsequent lines will appear in the header
# Generated at %s
'''

detector_id_name_axes_table = {
  'i03':('PILATUS3-60-0126', 'DECTRIS PILATUS3 6M',
         'PILATUS3 6M, S/N 60-0126', 3),
  'i04':('PILATUS2-60-0100', 'DECTRIS PILATUS 6M',
         'PILATUS 6M Prosport+, S/N 60-0100 Diamond', 3),
  'i19-1':('PILATUS2-24-0107', 'DECTRIS PILATUS 2M',
           'PILATUS 2M, S/N 24-0107 Diamond', 4)
}

def goniometer(beamline_id, data_collection_info):
  '''Return list of name, vector for either
  (i) canonical values if named or
  (ii) have a guess based on the beamline id
  (iii) actual vectors if in data collection info.'''

  if 'goniometer_axes' in data_collection_info:
    return data_collection_info['goniometer_axes']
  if 'goniometer_type' in data_collection_info:
    if data_collection_info['goniometer_type'].lower() == 'smargon':
      return [('GON_OMEGA', (1,0,0)),
              ('GON_CHI', (0,0,-1)),
              ('GON_PHI', (1,0,0))]
    if data_collection_info['goniometer_type'].lower() == 'minikappa':
      raise RuntimeError('mini kappa axes need to come from somewhere')

  # hard coded goniometers where these are unlikely to change - i19-1, i19-2,
  # i24 (though latter needs to know whether we are in pin or plate mode)

  if beamline_id == 'i19-1':
    return [('GON_OMEGA', (1,0,0)),
            ('GON_PHI', (0.5774,-0.8165,0))]
  if beamline_id == 'i19-2':
    return [('GON_OMEGA', (1,0,0)),
            ('GON_KAPPA', (0.642788,-0.766044,0)),
            ('GON_PHI', (1,0,0))]
  if beamline_id == 'i24':
    assert 'goniometer' in data_collection_info
    if data_collection_info['goniometer'] == 'vertical':
      return [('GON_OMEGA', (0,1,0))]
    elif data_collection_info['goniometer'] == 'horizontal':
      return [('GON_OMEGA', (1,0,0))]
    raise RuntimeError('Unknown i24 goniometer %s' %
                       data_collection_info['goniometer'])

  return [('GON_OMEGA', (1,0,0))]

class template_generator(object):
  def __init__(self, beamline_id, data_collection_info={}):
    assert beamline_id.lower() in ('i03', 'i04', 'i04-1', 'i23', 'i24',
                                   'i19-1', 'i19-2', 'vmxi', 'vmxm')

    self._data_collection_info = data_collection_info

    if 'crystal' in data_collection_info:
      self._crystal_id = data_collection_info['crystal']
    else:
      self._crystal_id = 'xtal'

    self._beamline_id = beamline_id.lower()

    return

  def boiler_plate(self):
    import datetime
    return header_boiler_plate % datetime.datetime.now().strftime(
      "%Y-%m-%d %H:%M")

  def diffrn(self):
    return '_diffrn.id %s\n_diffrn.crystal_id %s\n' % (self._beamline_id,
                                                       self._crystal_id)

  def beamline(self):
      return '''loop_
_diffrn_source.diffrn_id
_diffrn_source.source
_diffrn_source.type
 %s synchrotron 'Diamond Light Source Beamline %s'
''' % (self._beamline_id, self._beamline_id.upper()) + '''
loop_
_diffrn_radiation.diffrn_id
_diffrn_radiation.wavelength_id
_diffrn_radiation.monochromator
_diffrn_radiation.polarizn_source_ratio
_diffrn_radiation.polarizn_source_norm
_diffrn_radiation.div_x_source
_diffrn_radiation.div_y_source
_diffrn_radiation.div_x_y_source
 %s WAVELENGTH1 'Si 111' 0.8 0.0 0.08 0.01 0.00
''' % self._beamline_id

  def detector(self):

    detector_id, name, details, axes = detector_id_name_axes_table[
      self._beamline_id]

    block = '''# category DIFFRN_DETECTOR
loop_
_diffrn_detector.diffrn_id
_diffrn_detector.id
_diffrn_detector.detector
_diffrn_detector.type
_diffrn_detector.details
_diffrn_detector.number_of_axes
 %s %s PIXEL '%s' '%s' %d
''' % (self._beamline_id, detector_id, name, details, axes)

    if axes == 3:
      block += '''
loop_
_diffrn_detector_axis.detector_id
_diffrn_detector_axis.axis_id
 %s DET_X
 %s DET_Y
 %s DET_Z
''' % (detector_id, detector_id, detector_id)
      block += '''
loop_
_diffrn_scan_axis.scan_id
_diffrn_scan_axis.axis_id
_diffrn_scan_axis.angle_start
_diffrn_scan_axis.angle_range
_diffrn_scan_axis.angle_increment
_diffrn_scan_axis.displacement_start
_diffrn_scan_axis.displacement_range
_diffrn_scan_axis.displacement_increment
 SCAN1 DET_Z      0.0 0.0 0.0 %(distance).2f 0.0 0.0
 SCAN1 DET_Y      0.0 0.0 0.0 0.0 0.0 0.0
 SCAN1 DET_X      0.0 0.0 0.0 0.0 0.0 0.0
'''
    elif axes == 4:
      block += '''
loop_
_diffrn_detector_axis.detector_id
_diffrn_detector_axis.axis_id
 %s DET_2THETA
 %s DET_X
 %s DET_Y
 %s DET_Z
''' % (detector_id, detector_id, detector_id, detector_id)
      block += '''
loop_
_diffrn_scan_axis.scan_id
_diffrn_scan_axis.axis_id
_diffrn_scan_axis.angle_start
_diffrn_scan_axis.angle_range
_diffrn_scan_axis.angle_increment
_diffrn_scan_axis.displacement_start
_diffrn_scan_axis.displacement_range
_diffrn_scan_axis.displacement_increment
 SCAN1 DET_2THETA _2theta_ 0.0 0.0 0.0 0.0 0.0
 SCAN1 DET_Z      0.0 0.0 0.0 %(distance).2f 0.0 0.0
 SCAN1 DET_Y      0.0 0.0 0.0 0.0 0.0 0.0
 SCAN1 DET_X      0.0 0.0 0.0 0.0 0.0 0.0
'''

    block += '''
loop_
_diffrn_detector_element.id
_diffrn_detector_element.detector_id
 ELEMENT1 %s
''' % detector_id

    block += '''
loop_
_diffrn_data_frame.id
_diffrn_data_frame.detector_element_id
_diffrn_data_frame.array_id
_diffrn_data_frame.binary_id
 FRAME1 ELEMENT1 ARRAY1 1
'''

    return block

  def goniometer(self):
    pass

  def __repr__(self):
    return '\n'.join([self.boiler_plate(),
                      self.diffrn(),
                      self.beamline(),
                      self.detector()])

if __name__ == '__main__':
  import sys
  tg = template_generator(sys.argv[1], data_collection_info={
    'crystal':'unknown', 'wavelength':0.97963})
  print(tg)
