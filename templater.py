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
    if not record.startswith('X-'):
      continue
    token, value = record.split(':')
    parameters[token.strip()] = value.strip()

  return cbf_header, parameters, image_data

if __name__ == '__main__':
  import sys

  cbf_header, parameters, image_data = read_miniCBF_image(sys.argv[1])

  print(parameters)
