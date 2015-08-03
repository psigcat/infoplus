# -*- coding: utf-8 -*-
__author__ = 'David Erill'
__date__ = 'July 2015'
__copyright__ = '(C) 2015, David Erill'

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os
import sys

curpath = os.path.dirname(os.path.realpath(__file__))

# Adding so that our UI files can find resources_rc.py which is up one level.
sys.path.append(os.path.join(curpath, '..'))
