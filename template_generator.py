from __future__ import division, print_function

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
    return ''

  def goniometer(self):
    gi = self.goniometer_info()

    # construct dependency hierarchy, write out in orer from the ground up
    # purely because it is tidier to do it that way

    axes = gi['axes']

    inverse_depends_on = { }

    for a in axes:
      depends_on = axes[a]['depends_on']

      if not depends_on in inverse_depends_on:
        inverse_depends_on[depends_on] = [a]
      else:
        inverse_depends_on.append(a)

    def unroll(ido, k):
      result = [k]
      if not k in ido:
        return result
      for axis in ido[k]:
        result.extend(unroll(ido, axis))
      return result

    block = '''loop_
_diffrn_measurement_axis.measurement_id
_diffrn_measurement_axis.axis_id
'''

    for axis in unroll(inverse_depends_on, '.')[1:]:
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
    for axis in unroll(inverse_depends_on, '.')[1:]:
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

    for axis in unroll(inverse_depends_on, '.')[1:]:
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
    for axis in unroll(inverse_depends_on, '.')[1:]:
      x, y, z = axes[axis]['axis']
      block += '''GONIOMETER_%s rotation goniometer %s %f %f %f . . .
''' % (axis.upper(), axes[axis]['depends_on'], x, y, z)

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
