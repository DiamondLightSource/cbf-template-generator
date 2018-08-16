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
                      self.goniometer(), self.scan(), self.tailer()])

  def header(self):
    return ''

  def source(self):
    return ''

  def detector(self):

    di = self.detector_info()

    axes = di['axes']

    inverse_depends_on = { }

    for a in axes:
      depends_on = axes[a]['depends_on']

      if not depends_on in inverse_depends_on:
        inverse_depends_on[depends_on] = [a]
      else:
        inverse_depends_on.append(a)

    unrolled = unroll(inverse_depends_on, '.')[1:]

    block = '''
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
      block += '''DETECTOR DETECTOR_%s
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
        block += '''SCAN1 DETECTOR_%s _%s_ 0.0 0.0 0.0 0.0 0.0
''' % (axis.upper(), axis)
      elif axis == 'z':
        block += '''SCAN1 DETECTOR_Z 0.0 0.0 0.0 %f 0.0 0.0
''' % di['distance_mm']
      else:
        block += '''SCAN1 DETECTOR_%s 0.0 0.0 0.0 0.0 0.0 0.0
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
        block += '''FRAME1 DETECTOR_%s _%s_ 0.0
''' % (axis.upper(), axis)
      elif axis == 'z':
        block += '''FRAME1 DETECTOR_Z 0.0 %f
''' % di['distance_mm']
      else:
        block += '''FRAME1 DETECTOR_%s 0.0 0.0
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
        depends = 'DETECTOR_%s' % depends.upper()
      if axis in detector_rotations:
        block += '''DETECTOR_%s rotation detector %s %f %f %f . . .
''' % (axis.upper(), depends, x, y, z)
      else:
        block += '''DETECTOR_%s translation detector %s %f %f %f . . .
''' % (axis.upper(), depends, x, y, z)



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
      block += '''GONIOMETER GONIOMETER_%s
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
        block += '''SCAN1 GONIOMETER_%s _%s_ _d%s_ _d%s_ 0.0 0.0 0.0
''' % (axis.upper(), axis, axis, axis)
      else:
        block += '''SCAN1 GONIOMETER_%s _%s_ 0.0 0.0 0.0 0.0 0.0
''' % (axis.upper(), axis)

    block += '''
loop_
_diffrn_scan_frame_axis.frame_id
_diffrn_scan_frame_axis.axis_id
_diffrn_scan_frame_axis.angle
_diffrn_scan_frame_axis.displacement
'''

    for axis in unrolled:
      block += '''FRAME1 GONIOMETER_%s _%s_ 0.0
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
        depends = 'GONIOMETER_%s' % depends.upper()
      block += '''GONIOMETER_%s rotation goniometer %s %f %f %f . . .
''' % (axis.upper(), depends, x, y, z)

    return block

  def scan(self):
    return ''

  def tailer(self):
    return ''

  # helper functions

  def goniometer_info(self):
    return self._data_collection_parameters['goniometer']

  def detector_info(self):
    return self._data_collection_parameters['detector']

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
