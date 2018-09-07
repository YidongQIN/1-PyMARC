__author__ = 'Yidong QIN'

'''
Sensors definition in OpenBrIM
The sensors' _data are in the PC in Mason's Lab, in MySQL.
I am thinking to use MongoDB to replace it.
'''

import matplotlib.pyplot as plt
import numpy as np

from BMS_BrIM.PyELMT import *


class Sensor(OBObjElmt):
    # base_node: FENode

    def __init__(self, sensor_id, sensor_type, des: str, database_config: dict):
        super(Sensor, self).__init__('Sensor', sensor_id, D=des)
        self.id = sensor_id
        self.type = sensor_type
        self.name = '{}_{}'.format(sensor_type, sensor_id)
        _dbconfig = dict(database_config)
        try:
            self.datpath = _dbconfig.pop('path')
            # fileName is from the Server Setting JSON
        except KeyError:
            print('For the sensor <{}>,a "path" item is required in the config dictionary'.format(self.name))
        self.db_config = _dbconfig  # user, passwd, host, database, port
        self.x, self.y, self.z, self.dx, self.dy, self.dz = self.get_install()
        self.width, self.length, self.thick = self.get_dimension()
        self.unitid, self.channel = self.get_unit_info()
        self.datpath = self.get_backup_filename()
        self.base_node = None

    def mysql_read(self, id_name, table, *columns, fetch_type='ALL', with_des=False):
        try:
            with ConnMySQL(**self.db_config) as _db:
                _db.select(id_name, self.id, self.db_config['database'], table, *columns)
                _result = _db.fetch(fetch_type, with_des)
                print("SQL result is:\n  {}".format(_result))
                return _result
        except TypeError as e:
            print('<{}> Type Error\n  {}'.format(self.name, e))
        except BaseException as e:
            print('<{}> Error\n  {}'.format(self.name, e))
            raise e

    def mysql_write(self, id_name, table, *data):
        if self.mysql_read(id_name, table):
            self.mysql_update(id_name, table, *data)
        else:
            self.mysql_insert(table, *data)

    def mysql_insert(self, table, *data):
        """first check if exist, then update or insert"""
        try:
            with ConnMySQL(**self.db_config) as _db:
                return _db.insert(table, *data)
        except TypeError as e:
            print('<{}> Type Error\n  {}'.format(self.name, e))
        except BaseException as e:
            print('<{}> Error\n  {}'.format(self.name, e))
            raise e

    def mysql_update(self, id_name, table, *data):
        """update the records of the element"""
        try:
            with ConnMySQL(**self.db_config) as _db:
                _condition = '{}={}'.format(id_name, self.id)
                _db.update(table, *data, condition=_condition)
                return
        except BaseException as e:
            raise e

    def read_db_one(self, tbname, *col_names):
        db = ConnMySQL(**self.db_config)
        sql = 'select {} from bridge_test.{} where sensorID ={}'.format(", ".join(col_names), tbname, self.id)
        db.query(sql)
        info = db.fetch_row()
        db.close()
        return info

    def print_dbinfo(self, tbname, *col_names):
        info = self.read_db_one(tbname, *col_names)
        for i in range(len(info)):
            print('{}: {}'.format(col_names[i], info[i]))

    def plot_dat(self):
        print('Dat backup file of <{}> is {}'.format(self.name, self.datpath))
        DatProc('Sensor _data of {}'.format(self.name), self.datpath)

    def get_install(self):
        return self.read_db_one('sensorchannelinstallation',
                                'PositionX', 'PositionY', 'PositionZ',
                                'DirectionX', 'DirectionY', 'DirectionZ')

    def get_manufac(self):
        return self.read_db_one('sensor', 'manufacturerName', 'modelNumber')

    def get_dimension(self):
        return self.read_db_one('sensor',
                                'dimension1', 'dimension2', 'dimension3')

    def get_unit_info(self):
        return self.read_db_one('sensorchannelinstallation',
                                'wirelessUnitId', 'channelID')

    def get_backup_filename(self):
        """fileName is U{unitID}_{ChannelID}.dat"""
        return '{}\\U{}_{}.dat'.format(self.datpath, self.unitid, self.channel)

    def get_channel_setting(self):
        # return self.read_db_one()
        pass

    def geom(self):
        """ OpenBrIM geometry model"""
        if not (self.x, self.y, self.z):
            print('Sensor <{}> _position required'.format(self.name))
        if not (self.dx, self.dy, self.dz):
            print('Sensor <{}> direction required'.format(self.name))

    def set_base_node(self, fenode):
        if isinstance(fenode, OBFENode):
            self.base_node = fenode
        else:
            print('{}.base_node is not a FENode'.format(self.name))

    def fem(self):
        """FEM model. For sensor, it's just a node."""
        node = OBFENode(self.x, self.y, self.z, self.name)
        # not sure if realizable?
        # when create a FEM, cannot insert the node into this _position
        # because it will change the node number and element
        return node


class Temperature(Sensor):
    def __init__(self, tp_id, des, database_config):
        super(Temperature, self).__init__(tp_id, 'Temperature', des, database_config)

    def geom(self):
        super(Temperature, self).geom()
        tp = OBSurface(OBPoint(-self.length / 2, -self.width / 2),
                       OBPoint(self.length / 2, -self.width / 2),
                       OBPoint(self.length / 2, self.width / 2),
                       OBPoint(-self.length / 2, self.width / 2),
                       thick_prm_ob=1,
                       material_ob='Sensor_Temperature',
                       name=self.name)
        tp.set_attrib(Color='#DC143C')
        tp.move_to(self.x, self.y, self.z)
        tp.rotate_angle(self.dx, self.dy, self.dz)
        return tp

    def fem(self):
        pass


class StrainGauge(Sensor):
    def __init__(self, sg_id, des, database_config):
        super(StrainGauge, self).__init__(sg_id, 'strainGauge', des, database_config)

    def geom(self):
        super(StrainGauge, self).geom()
        ss = OBSurface(OBPoint(-self.length / 2, -self.width / 2),
                       OBPoint(self.length / 2, -self.width / 2),
                       OBPoint(self.length / 2, self.width / 2),
                       OBPoint(-self.length / 2, self.width / 2),
                       thick_prm_ob=1,
                       material_ob='Sensor_StrainGauge',
                       name=self.name)
        ss.set_attrib(Color='#DC143C')
        ss.move_to(self.x, self.y, self.z)
        ss.rotate_angle(self.dx, self.dy, self.dz)
        return ss


class Accelerometer(Sensor):
    def __init__(self, ac_id, des, database_config):
        super(Accelerometer, self).__init__(ac_id, 'accelerometer', des, database_config)
        # self.name = 'AC{}'.format(ac_id)
        # self.id = ac_id

    def geom(self):
        super(Accelerometer, self).geom()
        ac = CubeGeo(self.width, self.length, self.thick)
        ac.set_attrib(Color='#DC143C')
        ac.move_to(self.x, self.y, self.z)
        ac.rotate_angle(self.dx, self.dy, self.dz)
        return ac


class Displacement(Sensor):
    def __init__(self, ds_id, des, database_config):
        super(Displacement, self).__init__(ds_id, 'Displacement', des, database_config)
        self.name = 'DS{}'.format(ds_id)
        self.id = ds_id

    def geom(self):
        super(Displacement, self).geom()
        line = OBLine(OBPoint(0, 0, 0), OBPoint(self.length, 0, 0),
                      section_ob=OBSection('', '', OBCircle('', 1)))
        box = CubeGeo(self.width, self.width, self.thick)
        box.move_to(self.length / 2, 0, -self.thick / 2)
        ds = OBGroup(self.name, line, box)
        ds.set_attrib(Color='#DC143C')
        ds.move_to(self.x, self.y, self.z)
        ds.rotate_angle(self.dx, self.dy, self.dz)
        return ds


class NetworkUnit(object):
    """DAQ"""

    def __init__(self, unitid, dbconfig, *sensorlist):
        self.id = unitid
        self.dbconfig = dbconfig
        self.sensorlist = sensorlist

    def get_unit_info(self):
        return self.read_db_one('wirelessUnit', 'type', 'modelNumber')

    def get_channel_install(self):
        return self.read_db_all('sensorchannelinstallation', 'sensorId', 'monitoredAxis', 'channelId')

    def read_db_one(self, tbname, *col_names):
        db = ConnMySQL(**self.dbconfig)
        sql = 'select {} from bridge_test.{} where wirelessUnitID ={}'.format(", ".join(col_names), tbname, self.id)
        db.query(sql)
        info = db.fetch_row()
        return info

    def read_db_all(self, tbname, *col_names):
        db = ConnMySQL(**self.dbconfig)
        sql = 'select {} from bridge_test.{} where wirelessUnitID ={}'.format(
            ", ".join(col_names), tbname, self.id)
        db.query(sql)
        info = db.fetch_all(True)
        return info


class Experiment(object):
    """specify a Experiment by recording task, procedure, _data, etc"""

    def __init__(self, exptid, bridgeid, dbconfig):
        """shown as Text3D"""
        self.id = exptid
        self.bridgeid = bridgeid
        self.dbconfig = dbconfig
        self.name = exptid

    def geom(self, x, y, z, size):
        return OBText3D(self.name, x, y, z, size)

    def get_expt_info(self):
        expt = self.read_db_one('experimentconfiguration', 'name', 'status')
        return expt

    def get_bridge_info(self):
        db = ConnMySQL(**self.dbconfig)
        sql = "select name, describe, material, structuralType from bridge_test.bridge where bridgeId ={}".format(
            self.bridgeid)
        db.query(sql)
        info = db.fetch_row()
        return info

    def read_db_one(self, tbname, *col_names):
        db = ConnMySQL(**self.dbconfig)
        sql = 'select {} from bridge_test.{} where experimentconfigurationId ={}'.format(", ".join(col_names), tbname,
                                                                                         self.bridgeid)
        db.query(sql)
        info = db.fetch_row()
        return info

    def read_db_all(self, tbname, *col_names):
        db = ConnMySQL(**self.dbconfig)
        sql = 'select {} from bridge_test.{} where experimentconfigurationId ={}'.format(", ".join(col_names), tbname,
                                                                                         self.id)
        db.query(sql)
        info = db.fetch_all(True)
        return info


class DatProc(object):
    """Get and process of sensor _data"""

    def __init__(self, title, file_path):
        """Get .dat file in a particular path"""
        self.title = title
        try:
            self.data = np.loadtxt(file_path)
        except OSError as e:
            print(e)
        self.plot()
        self.fourier()

    def plot(self):
        plt.plot(self.data)
        plt.xlabel('Sampling Point')
        plt.ylabel('Value')
        plt.title(self.title)
        plt.show()

    def fourier(self):
        sp = np.fft.fft(self.data)
        freq = np.fft.fftfreq(self.data.shape[-1])
        plt.plot(freq, sp.real, freq, sp.imag)
        plt.xlabel('Frequency')
        plt.ylabel('dB')
        plt.title('FFT of {}'.format(self.title))
        plt.show()