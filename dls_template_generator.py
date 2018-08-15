from __future__ import division, print_function

from template_generator import template_generator

class dls_template_generator(template_generator):
  def __init__(self, beamline, data_collection_info):
    template_generator.__init__(self, beamline, data_collection_info)
    return

  def header(self):
    import datetime
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    gi = self.goniometer_info()

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

    header += '''--- End of preamble
'''

    return header
