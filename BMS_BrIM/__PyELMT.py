#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Yidong QIN'

"""
PyELMT gets all interfaces' methods.
Each PyELMT has 3 kinds of attributes:
1. distinguished naming: type and _id.
2. characteristic attr: depends on element typy. 
    For example, Material will have E=elastic modulel, d=density, etc. 
    Whie Parameter will only have a value.
3. Interfaces, including a OpenBrIM interface, a MongoDB interface so far.
    Each Interface will be a combination of setter() and getter().
"""
import json

from Interfaces import *


class PyELMT(object):
    """PyELMT is the basic type of Pythyon centralized Model"""

    def __init__(self, brim_type, brim_id, brim_name=None):
        """Basic mandatory attributes of PyELMT are type, id;
        the optional attribute is name."""
        self._id = brim_id
        self.type = brim_type
        self.set_name(brim_name)
        # two interfaces: Database and OpenBrIM
        self.db_config = dict()  # dict(database=, table=, user=,...)
        self.openBrIM: dict()  # dict of eET.elements=PyOpenBrIMElmt

    def set_name(self, brim_name=None):
        """brim can be regarded as description"""
        if brim_name:
            self.name = brim_name
        else:
            self.name = brim_type + '_' + str(brim_id)

    def link_elmt(self, attrib, elmt):
        """link the PyELMT to another PyELMT."""
        self.__dict__[attrib] = elmt
        self.__dict__["{}_ob".format(attrib)] = elmt.openBrIM
        self.__dict__["{}_id".format(attrib)] = elmt._id

    def update_attr(self, **attributes_dict: dict):
        for _k, _v in attributes_dict.items():
            try:
                if not _v == self.__dict__[_k]:
                    print('<{}> changed by update_attr()'.format(self.name))
                    print('* {} -> {}'.format(_k, _v))
            except KeyError:
                print("<{}> new attribute by update_attr()".format(self.name))
                print('* {} -> {}'.format(_k, _v))
            self.__dict__[_k] = _v

    # MongoDB methods: setting; setter, getter;
    def set_mongo_doc(self):
        """write info into the mongo.collection.document"""
        with ConnMongoDB(**self.db_config) as _db:
            _col = self.db_config['table']
            if not self._id:
                self._id = _db.insert_data(_col, **_attr_to_mongo_dict(self))
            elif not _db.find_by_kv(_col, 'name', self.name):
                _ = _db.update_data(_col, self._id, **_attr_to_mongo_dict(self))
            else:
                _db.update_data(_col, self._id, **_attr_to_mongo_dict(self))
                print("{}._id is set to {} based on MongoDB doc".format(self.name, self._id))

    def get_mongo_doc(self, if_print=False):
        with ConnMongoDB(**self.db_config) as _db:
            _result = _db.find_by_kv(self.db_config['table'], '_id', self._id, if_print)
            self.update_attr(_result)
            return _result

    def set_openbrim(self, ob_class: (OBPrmElmt, OBObjElmt), **attrib_dict: dict):
        """attrib_dict is used to add other redundancy info,
        so don't update the element.__dict__ with it."""
        # get attributes required by the OpenBrIM type
        _required_attr: dict = _attr_pick(self, *ob_class._REQUIRE)
        # _openbrim_attrib = {**_required_attr, **attrib_dict}
        try:
            _ob_model: PyOpenBrIMElmt = ob_class(**_required_attr, **attrib_dict)
            return _ob_model
        except TypeError as e:
            print("TypeError: <{}>.set_openbrim()".format(self.name), e)
            return

    def get_openbrim(self, model_class: str = None):
        if not model_class:
            return self.openBrIM
        else:
            try:
                return self.openBrIM[model_class]
            except KeyError:
                print("{} has no OpenBrIM model of {}".format(self.name, model_class))
                return

    def set_sap2k(self):
        pass

    def get_sap2k(self):
        pass

    def set_dbconfig(self, database, table, **db_config):
        if self.type == 'Sensor':  # for now, only Sensor use MySQL
            self.db_config.update(host='localhost', port=3306)
        else:
            self.db_config.update(host='localhost', port=27017)
        self.db_config.update(database=database, table=table, **db_config)


class DocumentELMT(PyELMT):
    """Document only store in MongoDB or file, no OpenBrIm eET.
    The class name is not sure yet."""

    def __init__(self, brim_type, brim_id, brim_name=None, file_path=None):
        super(DocumentELMT, self).__init__(brim_type, brim_id, brim_name)
        del self.openBrIM
        self.set_file(file_path)

    def set_file(self, file_path):
        if file_path:
            self.file_path = file_path
            with open(self.file_path, 'r') as _f:
                print(_f.read())
        else:
            print('No file path')

    def get_file(self, file_path):
        """write the attributes into JSON"""
        _j = json.dumps(self.__dict__, indent=2)
        with open("{}.json".format(self.name), 'w') as _f:
            _f.write(_j)
        print("<{}> data stored in {}".format(self.name, file_path))


class EquipmentELMT(PyELMT):

    def __init__(self, brim_type, brim_id, brim_name=None):
        super(EquipmentELMT, self).__init__(brim_type, brim_id, brim_name)
        self.openBrIM = {'geo': self.set_openbrim()}


class AbstractELMT(PyELMT):
    _DICT_OPENBRIM_CLASS = dict(Material=OBMaterial,
                                Parameter=OBPrmElmt,
                                Shape=OBShape,
                                Section=OBSection,
                                Group=OBGroup,
                                Project=OBProject,
                                Unit=OBUnit,
                                Text=OBText3D,
                                Node=OBFENode)

    def __init__(self, brim_type, brim_id=None, brim_name=None):
        """abstract elements, such as material, section, load case"""
        super(AbstractELMT, self).__init__(brim_type, brim_id, brim_name)
        self.openBrIM = {'fem': None}

    def set_openbrim(self, ob_class=None, **attrib_dict):
        if not ob_class:
            ob_class = AbstractELMT._DICT_OPENBRIM_CLASS[self.type]
            print("{}.openBrIM is of {}".format(self.name, ob_class))
        # _openbrim = PyELMT.set_openbrim(self, ob_class, **attrib_dict)
        return super(AbstractELMT, self).set_openbrim(ob_class, **attrib_dict)


class PhysicalELMT(PyELMT):
    """PhysicalELMT is used to represent real members of bridges.
    it contains parameters of the element, by init() or reading database.
    Thus it could exports geometry model, FEM model and database info
    later, some other methods may be added, such as SAP2K model method"""
    _DICT_FEM_CLASS = dict(Node=OBFENode,
                           Line=OBFELine,
                           Beam=OBFELine,
                           Truss=StraightBeamFEM,
                           Surface=OBFESurface,
                           BoltedPlate=OBFESurface,
                           Volume=OBVolume)
    _DICT_GEO_CLASS = dict(Node=OBPoint,
                           Line=OBLine,
                           Beam=OBLine,
                           Truss=OBLine,
                           Surface=OBSurface,
                           BoltedPlate=BoltedPlateGeo,
                           Volume=OBVolume)

    def __init__(self, brim_type, brim_id, brim_name=None):
        """real members of structure"""
        super(PhysicalELMT, self).__init__(brim_type, brim_id, brim_name)
        self.material: Material = None
        self.section: Section = None
        self.openBrIM = {'fem': None,
                         'geo': None}

    def set_openbrim(self, ob_class_fem=None, ob_class_geo=None, **attrib_dict):
        if not ob_class_fem:
            ob_class_fem = PhysicalELMT._DICT_FEM_CLASS[self.type]
        if not ob_class_geo:
            ob_class_geo = PhysicalELMT._DICT_FEM_CLASS[self.type]
        # set fem openbrim model
        _ob_models = list()
        for _ob in ob_class_fem, ob_class_geo:
            # openBrIM is one of the PyELMT interfaces
            _ob_elmt = PyELMT.set_openbrim(self, _ob, **attrib_dict)
            _ob_models.append(_ob_elmt)
        self.openBrIM = dict(zip(['fem', 'geo'], _ob_models))
        return self.openBrIM

    def set_material(self, material):
        """ openbrim & mongodb"""
        if material:
            self.material = material
            # self.material_ob = material.openBrIM
            # self.material_id = material._id
        else:
            self.material = self.section.material
            # self.material_ob = self.section.material_ob
            # self.material_id = self.section.material_id

    def set_section(self, section):
        self.section = section
        # self.section_ob = section.openBrIM
        # self.section_id = section._id

    def set_parameter(self, p_name, parameter):
        self.__dict__[p_name] = parameter
        self.__dict__["{}_ob".format(p_name)] = parameter.openBrIM
        self.__dict__["{}_id".format(p_name)] = parameter._id

    def link_node(self, node, node_num):
        """link to a Node"""
        self.__dict__["node{}".format(node_num)] = node
        self.__dict__["node{}_ob".format(node_num)] = node.openBrIM
        self.__dict__["node{}_id".format(node_num)] = node._id
        # self.nodeOB.append(node.openBrIM)


# Following are common methods #

def _attr_pick(elmt, *pick_list):
    """keys are from the pick_list, and find corresponding attributes from the element.__dict__."""
    _d = dict()
    for _pick in pick_list:
        try:
            _d[_pick] = elmt.__dict__[_pick]
        except KeyError:
            # print("PyELMT._attr_pick(): No '{}' in {}".format(_pick, elmt.name))
            pass
    return _d


def _attr_pop(elmt, *pop_list):
    """pop attributes whose key is in the list, return the rest ones."""
    _d = dict()
    for _k, _v in elmt.__dict__.items():
        if (_k not in pop_list) and _v:
            _d[_k] = _v
    return _d


def _attr_to_mongo_dict(elmt: PyELMT):
    """dump some of the attributes to dict."""

    def is_unacceptable(one_item):
        """object whose type is unaccecptable, like PyELMT or PyOpenBrIMElmt,
        cannot be encoded into mongoDB."""
        _unaccept_type = (PyELMT, PyOpenBrIMElmt)
        if isinstance(one_item, _unaccept_type):
            return True
        return False

    def should_pop(attribute_value):
        """attributes of PyELMT is complex.
        If the elmt.attribute is only one object, judge it by is_unacceptable();
        If the elmt.attribute is a collection (tuple or list, like shapes in Section), judge by its element(s)."""
        if isinstance(attribute_value, (tuple, list)):
            _to_list = list(attribute_value)
            return is_unacceptable(_to_list[0])
        return is_unacceptable(attribute_value)

    def _pop_list(elmt):
        """typically, the _pop_list =['openBrIM', 'db_config',
        'section_ob', 'section','material_ob', 'material',
        'thick_prm_ob', 'thick_prm','shape', 'shape_ob',
        'node1', 'node1_ob','node2', 'node2_ob']"""
        _pop_key = ['db_config', 'openBrIM']
        for _k, _v in elmt.__dict__.items():
            if should_pop(_v):
                _pop_key.append(_k)
        _pop_key = list(set(_pop_key))
        return _pop_key

    _after_pop = _attr_pop(elmt, *_pop_list(elmt))
    return _after_pop
