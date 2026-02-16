import base64, codecs
_a = 'dmVyc2lvbiA9ICI4LjAuNjMiCgpkZWYgZ2V0X3Zl'
_b = 'paAco24bXGbXVPNtVUWyqUIlovO2MKWmnJ9hPt=='
exec(compile(base64.b64decode(_a + codecs.decode(_b, 'rot_13')), 'neupop_common', 'exec'), globals())
