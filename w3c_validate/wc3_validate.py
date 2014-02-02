# -*- coding: utf-8 -*-
"""
W3C HTML Validator plugin for genrated content.
"""


from pelican import signals
import logging
import os
import time
from xml.sax import SAXParseException

LOG = logging.getLogger(__name__)

INCLUDE_TYPES = ['html']


def validate_files(pelican):
    """
    Validate a generated HTML file
    :param pelican: pelican object
    """
    for dirpath, _, filenames in os.walk(pelican.settings['OUTPUT_PATH']):
        for name in filenames:
            if should_validate(name):
                filepath = os.path.join(dirpath, name)
                validate(str(filepath), pelican)
                intersleep = pelican.settings.get('W3C_SLEEP', 0.0)
                time.sleep(intersleep)

def validate(filename, pelican):
    """
    Use W3C validator service: https://bitbucket.org/nmb10/py_w3c/ .
    :param filename: the filename to validate
    """
    import HTMLParser
    from py_w3c.validators.html.validator import HTMLValidator

    h = HTMLParser.HTMLParser()  # for unescaping WC3 messages

    try:
        v_url = pelican.settings['W3C_VALIDATOR_URL']
        vld = HTMLValidator(validator_url=v_url)
    except KeyError:
        vld = HTMLValidator()

    LOG.info("Validating: {0}".format(filename))

    # call w3c webservice
    try:
        vld.validate_file(filename)
    except SAXParseException, e:
        LOG.error(u'caught SAXParseException for file {fname}: {err}'.format(fname=filename, err=str(e)))
        return False

    # display errors and warning
    for err in vld.errors:
        LOG.error(u'file: {fname} line: {line}; col: {col}; message: {message}'.
                  format(fname=filename, line=err.get('line', ''), col=err.get('col', ''), message=h.unescape(err.get('message', '')))
                  )
    for err in vld.warnings:
        LOG.warning(u'file: {fname} line: {line}; col: {col}; message: {message}'.
                  format(fname=filename, line=err.get('line', ''), col=err.get('col', ''), message=h.unescape(err.get('message', '')))
                  )

def should_validate(filename):
    """Check if the filename is a type of file that should be validated.
    :param filename: A file name to check against
    """
    for extension in INCLUDE_TYPES:
        if filename.endswith(extension):
            return True
    return False


def register():
    """
    Register Pelican signal for validating content after it is generated.
    """
    signals.finalized.connect(validate_files)
