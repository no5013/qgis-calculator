# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Calculator
                                 A QGIS plugin
 calculator
                             -------------------
        begin                : 2017-11-14
        copyright            : (C) 2017 by Karnthep T.
        email                : karnthep.t@gmail.com
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
    """Load Calculator class from file Calculator.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .calculator import Calculator
    return Calculator(iface)
