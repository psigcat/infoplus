# -*- coding: utf-8 -*-
"""
/***************************************************************************
 InfoPlus - A QGIS plugin to enhance identify features
                             -------------------
        begin                : 2015-07-31
        copyright            : (C) 2015 by David Erill
        email                : daviderill79@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load InfoPlus class from file InfoPlus.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .info_plus import InfoPlus
    return InfoPlus(iface)
