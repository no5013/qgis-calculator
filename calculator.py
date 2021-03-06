# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Calculator
                                 A QGIS plugin
 calculator
                              -------------------
        begin                : 2017-11-14
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Karnthep T.
        email                : karnthep.t@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QFileInfo, QVariant
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from qgis.core import QgsVectorLayer, QgsField, QgsMapLayerRegistry, QgsFeature, QgsGeometry, QgsPoint
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from calculator_dialog import CalculatorDialog
import os.path
import csv
import math

class Calculator:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Calculator_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Calculator')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Calculator')
        self.toolbar.setObjectName(u'Calculator')

        #path เริ่มต้น
        self.path = '/'

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Calculator', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = CalculatorDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        #เชื่อมปุ่มกับช่องคำสั่งเปิด File browser
        self.dlg.pushButton.clicked.connect(self.select_output_file)
        self.dlg.pushButton_2.clicked.connect(self.select_output_file_2)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Calculator/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'calculate'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Calculator'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #คำสั่งเลือกไฟล์สำหรับ site data
    def select_output_file(self):
        #เปิดไฟล์ Browse
        #ช่องแรกช่างแม่ง ช่องสองชื่อTitle ช่องสามPathเริ่มต้น(ตอนแรกเป็น '/' สร้างไว้ข้างบน) ช่องสี่เลือกสกุลไฟล์
        #เลือกไฟล์เสร็จเก็บเข้าตัวแปล filenames
        filename = QFileDialog.getOpenFileName(self.dlg, "Select tab files  ",self.path, '*.csv')

        #เช็คว่ามีไฟล์รึเปล่า
        if(len(filename) > 0):
            #save path ก่อนหน้า
            self.path = QFileInfo(filename).path();
            self.dlg.lineEdit.setText(filename)

    #คำสั่งเลือกไฟล์สำหรับ workbook
    def select_output_file_2(self):
        #เปิดไฟล์ Browse
        #ช่องแรกช่างแม่ง ช่องสองชื่อTitle ช่องสามPathเริ่มต้น(ตอนแรกเป็น '/' สร้างไว้ข้างบน) ช่องสี่เลือกสกุลไฟล์
        #เลือกไฟล์เสร็จเก็บเข้าตัวแปล filenames
        filename = QFileDialog.getOpenFileName(self.dlg, "Select tab files  ",self.path, '*.csv')

        #เช็คว่ามีไฟล์รึเปล่า
        if(len(filename) > 0):
            #save path ก่อนหน้า
            self.path = QFileInfo(filename).path();
            self.dlg.lineEdit_2.setText(filename)

    # หาช่อง pci ที่มีค่ามากที่สุด
    def get_max_pci(self, row):
        # เช็คว่ามีค่า lat long หรือเปล่า ถ้าไม่มีส่ง False
        if(row[3] != "" and row[4] != ""):
            max = None
            max_id = None
            # วนลูปหาสัญญาณค่ามากสุด
            for i in range(5, len(row)):
                if(row[i] != ""):
                    if((max is None) or (int(row[i]) > int(max))):
                        max = row[i]
                        max_id = i
            # ถ้าใน message นั้นมีค่าสัญญาณซัก pci ส่งเลขช่อง pci ที่มีค่ามากที่สุดกลับไป
            if(max != None):
                return max_id

        return False

    # แก้ชื่อ column pci ใน workbook จาก
    def format_pci_header(self, headers):
        format_headers = headers
        for i in range(5, len(headers)):
            splited = headers[i].split('_')
            format_headers[i] = splited[len(splited)-1]
        return format_headers

    # หาเสาสัญญาณที่ใกล้จากจุดที่สุด ค่าที่ต้องใส่คือ
    # pci: เลข pci
    # lat_p, long_p: ไว้หาเสาร์สัญญาณที่ห่างจากจุดน้อยที่สุด
    # antenna_list: list ของเสาสัญญาณทั้งหมด
    def find_antenna(self, pci_id, lat_p, long_p, antenna_list):
        min_distance = None
        min_distance_antenna = None
        for antenna in antenna_list:
            if str(antenna[4]) == str(pci_id):
                distance = self.distance_between_point(float(antenna[2]), float(antenna[1]), lat_p, long_p)
                if(min_distance is None or distance < min_distance):
                    min_distance = distance
                    min_distance_antenna = antenna

        if min_distance_antenna != None:
            return min_distance_antenna
        else:
            error_text = 'Cannot find antenna with pci' + pci_id + ' in the site_data'
            print(error_text)
            raise ValueError(error_text)

    # สูตรหาค่า rsrp
    # area_type
    # 0 = urban
    # 1 = sub_urban
    # 2 = rural
    def calculate_rsrp(self, lat_ant, long_ant, height_ant, freq, lat_p, long_p, area_type):
        distance = self.distance_between_point(lat_ant, long_ant, lat_p, long_p)
        ah = (1.11*math.log10(freq)-0.7)*1-(1.56*math.log10(freq)-0.8)
        lu = 46.3+(33.9*math.log10(freq))-13.82*math.log10(height_ant)+((44.9-6.55*math.log10(1))*math.log10(distance))
        pl = lu-ah

        # ถ้าเป็น sub_urban หรือ rural ให้ลบค่าเพิ่ม
        if(area_type == 1):
            pl = pl - 2*math.pow(math.log10(freq/28),2) - 5.4
        elif(area_type == 2):
            pl = pl - 4.78*math.pow(math.log10(freq),2) + 18.33*math.log10(freq) - 40.98

        rsrp = 18.228787 - pl
        return rsrp

    # หาจุดระหว่าง2จุดของ lat และ long
    def distance_between_point(self,lat_ant,long_ant,lat_p,long_p):
        a = math.pow(math.sin(math.fabs(lat_p-lat_ant)*math.pi/180/2),2)+math.cos(lat_ant*math.pi/180)*math.cos(lat_p*math.pi/180)*math.pow(math.sin(math.fabs(long_p-long_ant)*math.pi/180/2),2)
        c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = 6371*c
        return distance

    def run(self):
        """Run method that performs all the real work"""
        # เคลียร์combobox
        self.dlg.comboBox.clear()
        # นำชื่อไฟล์ไปใส่ comboBox
        self.dlg.comboBox.addItems(["Urban", "Sub_Urban", "Rural"])

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            print("Calculating...")
            # สร้าง layer เปล่ามา
            calculatedLayer = QgsVectorLayer("Point", "Calculated", "memory")
            pr = calculatedLayer.dataProvider()
            calculatedLayer.startEditing()
            # เพิ่ม column PDSL-LTE_UE_RSRP ที่มีค่าเป็นตัวเลข(double คือเลขทศนิยม)
            pr.addAttributes([QgsField("PDSL-LTE_UE_RSRP", QVariant.Double)])

            # ดึง path site data มา
            site_data_file = self.dlg.lineEdit.text()
            # ดึง path workbook มา
            workbook_file = self.dlg.lineEdit_2.text()
            # ดูว่าค่าเป็นพื้นที่ประเภทไหน
            area_type = self.dlg.comboBox.currentIndex()

            # เช็คว่าไฟล์ไม่ว่างเปล่า
            if site_data_file!="" and workbook_file!="":
                # เปิดไฟล์ site data ขึ้นมา
                f = open(site_data_file, 'rt')
                reader = csv.reader(f)
                # ประกาศตัวแปรว่างเปล่า ไว้เก็บข้อมูลเสา
                antenna_data = []
                # นำข้อมูลที่อยู่ใน csv ในแต่ละแถว(row) มาใส่ตัวแปร antenna_data ที่เราประกาศเอาไว้ข้างบน
                for row in reader:
                    antenna_data.append(row)

                # เปิดไฟล์ workbook ขึ้นมา
                f = open(workbook_file, 'rt')
                reader = csv.reader(f)

                # ประกาศตัวแปรว่างเปล่า ที่จะไว้เก็บชื่อ column
                headers = []
                # ประกาศตัวแปรว่างเปล่า ที่จะไว้เพิ่มจุดที่จะปรากฏบน layer
                features = []
                # ประกาศตัวแปร index ไว้เพื่อนับจำนวนแถวของข้อมูล เพื่อเช็คว่าถ้าข้อมูลแถวที่ 0 แถวนั้นคือชื่อหัวตารางนั่นเอง
                index = 0
                for row in reader:
                    # ถ้าเป็นข้อมูลแถวที่ 0
                    if(index == 0):
                        # นำชื่อหัวตารางไปแปลงแล้วนำมาใส่ตัวแปร header ที่ประกาศไว้ข้างบน
                        headers = self.format_pci_header(row)
                    else:
                        # นำข้อมูลในแถวไปหาเลขช่องที่มีค่า
                        pci_id = self.get_max_pci(row)
                        # ถ้าข้อมูลในแถวมี lat long และมีค่าใน pci ซัก pci นึง
                        if(pci_id != False):
                            # ไปหาข้อมูลเสา
                            antenna = self.find_antenna(headers[pci_id], float(row[4]), float(row[3]), antenna_data)
                            # คำนวณ rsrp
                            print(headers[pci_id])
                            print(antenna)
                            rsrp = self.calculate_rsrp(float(antenna[2]), float(antenna[1]), float(antenna[3]), float(antenna[6]), float(row[4]), float(row[3]), area_type)
                            # สร้างจุดว่างเปล่าขึ้นมา
                            feature = QgsFeature()
                            # ใส่ค่า X Y ให้จุด
                            feature.setGeometry(QgsGeometry.fromPoint(QgsPoint(float(row[3]), float(row[4]))))
                            # ใส่ค่า rsrp ที่เราคำนวณไว้ให้จุด
                            feature.setAttributes([rsrp])
                            # นำจุดที่เราสร้างไว้ข้างบนไปใส่ตัวแปรที่เราประกาศไว้ข้างบน เพื่อที่จะรอเพิ่มใส่ใน layer ที่เดียว
                            features.append(feature)
                    # ไว้บอกเฉยๆว่าเราวนลูปไปกี่รอบแล้ว
                    index+=1

                # พอเราคำนวณครบทุกจุดแล้ว เราก็เอาจุดที่เราสร้างมา Add ใส่ layer ที่เดียว
                pr.addFeatures(features)

                # บอก layer ว่าเราเพิ่งเพิ่มจุดไป อัพเดทตัวเองด้วย
                calculatedLayer.commitChanges()
                calculatedLayer.updateExtents()

                # Add layer ที่เราเพิ่งสร้างไปในโปรแกรม qgis
                QgsMapLayerRegistry.instance().addMapLayer(calculatedLayer)
                print("Finished!")
            else:
                print("Please browse files!!!")
