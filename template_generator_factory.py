from __future__ import division, print_function

def template_generator_factory(beamline, data_collection_info):

  # FIXME there is probably a much better way of doing this without needing to
  # always import all - though the list of beamlines is small so...

  if beamline == 'i02-1' or beamline.lower() == 'vmxm':
    from i02_1_template_generator import i02_1_template_generator
    return i02_1_template_generator(beamline, data_collection_info)

  if beamline == 'i03':
    from i03_template_generator import i03_template_generator
    return i03_template_generator(beamline, data_collection_info)

  if beamline == 'i04':
    from i04_template_generator import i04_template_generator
    return i04_template_generator(beamline, data_collection_info)

  if beamline == 'i19-1':
    from i19_1_template_generator import i19_1_template_generator
    return i19_1_template_generator(beamline, data_collection_info)

  if beamline == 'i19-2':
    from i19_2_template_generator import i19_2_template_generator
    return i19_2_template_generator(beamline, data_collection_info)

  if beamline == 'i24':
    from i24_template_generator import i24_template_generator
    return i24_template_generator(beamline, data_collection_info)

  raise RuntimeError('unknown beamline %s' % beamline)

if __name__ == '__main__':
  # this illustrates what we are expecting to be passed... much of the
  # information comes from camserver via MXSettings - which is picked up
  # with e.g. _wave_ in the template
  example_dc_info = {'detector':{'distance_mm':187.5,
                                 'beam_x_pixel':1234.5,
                                 'beam_y_pixel':1024.0},
                     'beam':{}}

  import sys
  try:
    generator = template_generator_factory(sys.argv[1], example_dc_info)
    print(generator())
  except Exception as e:
    print(e)
