import pkg_resources
try:
    # this will be the mother module of our application
    __version__ = pkg_resources.get_distribution('pdf_classifier').version
except pkg_resources.DistributionNotFound:
    __version__ = 'local'
