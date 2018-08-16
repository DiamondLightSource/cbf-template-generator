from __future__ import division, print_function

def unroll(inverted_depends_on, k):
  result = [k]
  if not k in inverted_depends_on:
    return result
  for axis in inverted_depends_on[k]:
    result.extend(unroll(inverted_depends_on, axis))
  return result

class template_generator(object):
  '''Base class for template generation - will need to override with useful
  parameters to create a custom imgCIF template for a given beamline.'''

  def __init__(self, beamline, data_collection_parameters):
    self._beamline = beamline
    self._data_collection_parameters = data_collection_parameters

    return

  def __call__(self):
    return '\n'.join([self.header(), self.source(), self.detector(),
                      self.goniometer(), self.scan(), self.tailer()]).strip()

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

    block = '''
loop_
_diffrn_radiation_wavelength.id
_diffrn_radiation_wavelength.wavelength
_diffrn_radiation_wavelength.wt
WAVELENGTH1 _wave_ 1
'''

    return block

  def detector(self):

    # other homeless header junk - not sure about the structure being
    # ideal here, perhaps worth refactoring?

    gi = self.goniometer_info()
    di = self.detector_info()

    block = '''
loop_
_diffrn_measurement.diffrn_id
_diffrn_measurement.id
_diffrn_measurement.number_of_axes
_diffrn_measurement.method
_diffrn_measurement.sample_detector_distance
 %s GONIOMETER %d rotation %.2f
''' % (self._beamline, len(gi['axes']), di['distance_mm'])

    # now proper detector things

    axes = di['axes']

    inverse_depends_on = { }

    for a in axes:
      depends_on = axes[a]['depends_on']

      if not depends_on in inverse_depends_on:
        inverse_depends_on[depends_on] = [a]
      else:
        inverse_depends_on.append(a)

    unrolled = unroll(inverse_depends_on, '.')[1:]

    block += '''
loop_
_diffrn_detector.diffrn_id
_diffrn_detector.id
_diffrn_detector.type
_diffrn_detector.number_of_axes
 %s DETECTOR '%s' %d
''' % (self._beamline, di['name'], len(di['axes']))

    block += '''
loop_
_diffrn_detector_axis.detector_id
_diffrn_detector_axis.axis_id
'''
    for axis in unrolled:
      block += '''DETECTOR DET_%s
''' % axis.upper()

    block += '''
loop_
_diffrn_detector_element.id
_diffrn_detector_element.detector_id
 ELEMENT1 DETECTOR

loop_
_diffrn_data_frame.id
_diffrn_data_frame.detector_element_id
_diffrn_data_frame.array_id
_diffrn_data_frame.binary_id
 FRAME1 ELEMENT1 ARRAY1 1

loop_
_diffrn_scan.id
_diffrn_scan.frame_id_start
_diffrn_scan.frame_id_end
_diffrn_scan.frames
 SCAN1 FRAME1 FRAME1 1
'''

    # classification of goniometer axes - unlikely to become wrong

    detector_rotations = ['2theta']

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
'''

    for axis in unrolled:
      if axis in detector_rotations:
        block += '''SCAN1 DET_%s _%s_ 0.0 0.0 0.0 0.0 0.0
''' % (axis.upper(), axis)
      elif axis == 'z':
        block += '''SCAN1 DET_Z 0.0 0.0 0.0 %f 0.0 0.0
''' % di['distance_mm']
      else:
        block += '''SCAN1 DET_%s 0.0 0.0 0.0 0.0 0.0 0.0
''' % (axis.upper())

    block += '''
loop_
_diffrn_scan_frame_axis.frame_id
_diffrn_scan_frame_axis.axis_id
_diffrn_scan_frame_axis.angle
_diffrn_scan_frame_axis.displacement
'''

    for axis in unrolled:
      if axis in detector_rotations:
        block += '''FRAME1 DET_%s _%s_ 0.0
''' % (axis.upper(), axis)
      elif axis == 'z':
        block += '''FRAME1 DET_Z 0.0 %f
''' % di['distance_mm']
      else:
        block += '''FRAME1 DET_%s 0.0 0.0
''' % (axis.upper())

    block += '''
loop_
_axis.id
_axis.type
_axis.equipment
_axis.depends_on
_axis.vector[1] _axis.vector[2] _axis.vector[3]
_axis.offset[1] _axis.offset[2] _axis.offset[3]
'''
    for axis in unrolled:
      x, y, z = axes[axis]['axis']
      depends = axes[axis]['depends_on']
      if depends != '.':
        depends = 'DET_%s' % depends.upper()
      if axis in detector_rotations:
        block += '''DET_%s rotation detector %s %f %f %f . . .
''' % (axis.upper(), depends, x, y, z)
      else:
        block += '''DET_%s translation detector %s %f %f %f . . .
''' % (axis.upper(), depends, x, y, z)

    # now we add the beam centre and fast, slow axes explicitly
    if 'PILATUS' in di['name']:
      pixel_size = 0.172
    elif 'EIGER' in di['name']:
      pixel_size = 0.075

    offset_fast = pixel_size * di['beam_x_pixel']
    offset_slow = pixel_size * di['beam_y_pixel']

    dx, dy, dz = [-1 * offset_fast * di['fast'][j] +
             -1 * offset_slow * di['slow'][j] for j in range(3)]

    block += '''DET_SLOW translation detector DET_%s %f %f %f %f %f %f
''' % (axis.upper(), di['slow'][0], di['slow'][1], di['slow'][2], dx, dy, dz)
    block += '''DET_FAST translation detector DET_SLOW %f %f %f 0.0 0.0 0.0
''' % (di['fast'][0], di['fast'][1], di['fast'][2])

    # and pixel size block
    block += '''
loop_
_array_structure_list_axis.axis_set_id
_array_structure_list_axis.axis_id
_array_structure_list_axis.displacement
_array_structure_list_axis.displacement_increment
DET_FAST DET_FAST 0.0 %f
DET_SLOW DET_SLOW 0.0 %f
''' % (pixel_size, pixel_size)

    block += '''
loop_
_array_structure_list.array_id
_array_structure_list.index
_array_structure_list.dimension
_array_structure_list.precedence
_array_structure_list.direction
_array_structure_list.axis_set_id
ARRAY1 1 _wide_ 1 increasing DET_FAST
ARRAY1 2 _high_ 2 increasing DET_SLOW
'''

    return block

  def goniometer(self):
    gi = self.goniometer_info()

    # construct dependency hierarchy, write out in order from the ground up
    # purely because it is tidier to do it that way

    axes = gi['axes']

    inverse_depends_on = { }

    for a in axes:
      depends_on = axes[a]['depends_on']

      if not depends_on in inverse_depends_on:
        inverse_depends_on[depends_on] = [a]
      else:
        inverse_depends_on.append(a)

    unrolled = unroll(inverse_depends_on, '.')[1:]

    block = '''loop_
_diffrn_measurement_axis.measurement_id
_diffrn_measurement_axis.axis_id
'''

    for axis in unrolled:
      block += '''GONIOMETER GON_%s
''' % axis.upper()

    scannable_axes = ['omega', 'chi', 'phi']

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
'''
    for axis in unrolled:
      if axis in scannable_axes:
        block += '''SCAN1 GON_%s _%s_ _d%s_ _d%s_ 0.0 0.0 0.0
''' % (axis.upper(), axis, axis, axis)
      else:
        block += '''SCAN1 GON_%s _%s_ 0.0 0.0 0.0 0.0 0.0
''' % (axis.upper(), axis)

    block += '''
loop_
_diffrn_scan_frame_axis.frame_id
_diffrn_scan_frame_axis.axis_id
_diffrn_scan_frame_axis.angle
_diffrn_scan_frame_axis.displacement
'''

    for axis in unrolled:
      block += '''FRAME1 GON_%s _%s_ 0.0
''' % (axis.upper(), axis)

    block += '''
loop_
_axis.id
_axis.type
_axis.equipment
_axis.depends_on
_axis.vector[1] _axis.vector[2] _axis.vector[3]
_axis.offset[1] _axis.offset[2] _axis.offset[3]
'''
    for axis in unrolled:
      x, y, z = axes[axis]['axis']
      depends = axes[axis]['depends_on']
      if depends != '.':
        depends = 'GON_%s' % depends.upper()
      block += '''GON_%s rotation goniometer %s %f %f %f . . .
''' % (axis.upper(), depends, x, y, z)

    return block

  def scan(self):
    return '''
loop_
_diffrn_scan_frame.frame_id
_diffrn_scan_frame.frame_number
_diffrn_scan_frame.integration_time
_diffrn_scan_frame.exposure_time
_diffrn_scan_frame.scan_id
_diffrn_scan_frame.date
 FRAME1 1 _expt_ _expp_ SCAN1 _timestamp_
'''

  def tailer(self):
    return '''
loop_
_array_intensities.array_id
_array_intensities.binary_id
_array_intensities.linearity
_array_intensities.gain
_array_intensities.gain_esd
_array_intensities.overload
_array_intensities.undefined_value
ARRAY1 1 linear 1.0 . _cutoff_ -1

loop_
_array_structure.id
_array_structure.encoding_type
_array_structure.compression_type
_array_structure.byte_order
ARRAY1 "signed 32-bit integer" _compress_ little_endian
'''

  # helper functions

  def goniometer_info(self):
    return self._data_collection_parameters['goniometer']

  def detector_info(self):
    return self._data_collection_parameters['detector']

  def beam_info(self):
    return self._data_collection_parameters['beam']

  @staticmethod
  def recursive_update(original, overwrite):
    '''Recursive update original dictionary with contents of overwrite.'''
    import collections

    for k, v in overwrite.iteritems():
        if isinstance(v, collections.Mapping):
            original[k] = template_generator.recursive_update(
              original.get(k, {}), v)
        else:
            original[k] = v
    return original
