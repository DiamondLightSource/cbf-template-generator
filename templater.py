from __future__ import division, print_function

def read_miniCBF_image(image):
  '''Read the file, return (i) text of miniCBF header (ii) dictionary of header
  parameters (iii) bytes of compressed picture.'''

  import binascii
  start_tag = binascii.unhexlify('0c1a04d5')
  data = open(image, 'rb').read()
  data_offset = data.find(start_tag)
  cbf_header = data[:data_offset]
  image_data = data[data_offset:]

  # chop up miniCBF header - hash it down to a dictionary

  parameters = { }

  for record in cbf_header.split('\n'):
    if not record.startswith('#'):
      continue

    record = record.strip()

    if len(record[1:].split()) <= 2 and record.count(':') == 2:
      parameters['timestamp'] = record[1:].strip()
      continue

    tokens = record.replace('=', '').replace(':', '').split()[1:]

    parameters[tokens[0]] = ' '.join(tokens[1:])

  # now find the mime header section
  for record in cbf_header.split('\n'):
    if record.startswith('     conversions='):
      parameters['compression'] = record.strip().split('=')[-1][3:-1]
      continue
    if not record.startswith('X-'):
      continue
    token, value = record.split(':')
    parameters[token.strip()] = value.strip()

  def tidy_parameter_value(value):
    value = ' '.join([v for v in value.split() if not v in ['deg.', 'm', 'A']])
    for cruft in [',', '(', ')', ]:
      value = value.replace(cruft, ' ')
    return [token.strip() for token in value.split()]

  for k in parameters:
    if not k.startswith('X-'):
      parameters[k] = tidy_parameter_value(parameters[k])

  return cbf_header, parameters, image_data

def parameters_to_dc_info(parameters):
  distance_mm = 1000.0 * float(parameters['Detector_distance'][0])
  beam_x_pixel, beam_y_pixel = map(float, parameters['Beam_xy'][:2])
  wavelength = float(parameters['Wavelength'][0])
  expt = float(parameters['Exposure_time'][0])
  expp = float(parameters['Exposure_period'][0])
  omega = float(parameters['Omega'][0])
  domega = float(parameters['Omega_increment'][0])
  cutoff = int(parameters['Count_cutoff'][0])
  wide = int(parameters['X-Binary-Size-Fastest-Dimension'])
  high = int(parameters['X-Binary-Size-Second-Dimension'])
  compress = parameters['compression'][0]

  # put the parameters which would be filled in by camserver in an appropriate
  # dictionary

  camserver = {'_wave_':wavelength,
               '_expt_':expt,
               '_expp_':expp,
               '_omega_':omega,
               '_domega_':domega,
               '_cutoff_':cutoff,
               '_compress_':compress,
               '_timestamp_':parameters['timestamp'][0],
               '_wide_':wide,
               '_high_':high}

  # add more things if we know more things

  if 'Chi' in parameters:
    camserver['_chi_'] = float(parameters['Chi'][0])
    camserver['_dchi_'] = float(parameters['Chi_increment'][0])

  if 'Phi' in parameters:
    camserver['_phi_'] = float(parameters['Phi'][0])
    camserver['_dphi_'] = float(parameters['Phi_increment'][0])

  if 'Kappa' in parameters:
    camserver['_kappa_'] = float(parameters['Kappa'][0])

  if 'Detector_2theta' in parameters:
    camserver['_2theta_'] = float(parameters['Detector_2theta'][0])

  dc_info = {'detector':{'name':' '.join(parameters['Detector']),
                         'distance_mm':distance_mm,
                         'beam_x_pixel':beam_x_pixel,
                         'beam_y_pixel':beam_y_pixel},
             'beam':{},
             'camserver':camserver}

  return dc_info

def make_imgCIF(cbf_header, header, image_data):
  comment_section = cbf_header.split(';')[1]
  header = header.replace('--- End of preamble', '')
  header = header.replace('# DECTRIS translation table:\n', comment_section)
  header_text = '\n'.join([record for record in header.split('\n') if not
                           record.startswith('@')])
  mime = cbf_header.split('--CIF-BINARY-FORMAT-SECTION--')[1]
  return header_text + '''
_array_data.data
;
--CIF-BINARY-FORMAT-SECTION--''' + mime + image_data

if __name__ == '__main__':
  import sys

  from template_generator_factory import template_generator_factory
  cbf_header, parameters, image_data = read_miniCBF_image(sys.argv[1])
  dc_info = parameters_to_dc_info(parameters)
  generator = template_generator_factory(sys.argv[2], dc_info)
  header = generator()
  open(sys.argv[3], 'wb').write(make_imgCIF(cbf_header, header, image_data))
