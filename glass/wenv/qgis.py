"""
Start QGIS Sessions
"""


def get_qgis_app():
    """ Start one QGIS application.

    :returns: Handle to QGIS app.
    :rtype: QgsApplication

    If QGIS is already running the handle to that app will be returned.
    """

    QGIS_PATH = '/usr/bin/qgis'

    try:
        from qgis.core import QgsApplication
    except ImportError:
        return None
    
    QgsApplication.setPrefixPath(QGIS_PATH)

    QGIS_APP = QgsApplication([], False)

    QGIS_APP.initQgis()
    
    return QGIS_APP

