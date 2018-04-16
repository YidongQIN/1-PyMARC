# import ClassPyOpenBrIM
from PyOpenBrIM import *

xx = PrmElmt("x_spacing", '108.3')
print(type(xx.value))
print(xx.value)
# TopChord_width = PrmElmt("TopChord_width", "6", ut="Length", role="Input")

'''
newproj = PyOpenBrIMElmt('new proj')
newproj.parse_xmlfile('xml file/test.xml')
# ShowTree(newproj)
unit1=Unit('first unit')
ShowTable(unit1)
mat1=Material('C4000Psi','Deck Concrete','Concrete')
mat1.mat_property(d='0.000002248', E=3604, a=0.000055, Fc28=4)
# mat1.show_mat()
point=[]
for i in range(4):
    point.append(Point(i,0,0))

shape1=Shape('s1',*point)
shape2=Shape('s2',*point)
shape2.show_sub()
shape2.is_cutout()
sec1=Section('sect',mat1,shape1,shape2)
ShowTree(sec1)
# point1=Point(0,0,0,'P1')
# point2=Point(10,0,0,'P2')
# point3=Point(20,0,0,'P2')
# point4=Point(30,0,0,'P2')
# line1=Line(point1)
# line1.attach_to(newproj)
# sur1=Surface(point1,point2,point3,point4,50,'mat1','name of surface')
# sur1.attach_to(newproj)
# par1=PrmElmt('par', 'value')
# par1.attach_to(newproj)
# newproj.save_project()
# ShowTree(newproj)

# print('---add sub nodes test---')
new_node = ObjElmt('Line', 'new node1', D='~ TEST ~ ', UC='test')
new_node2 = ObjElmt('Not Line', 'new_node2', D='~ ~ TEST ~ ~')
new_par = PrmElmt('test parameter', '666', '$$$$$$$$$$$', par_type='p_tag')
new_node2.sub(new_par)
newproj.sub(new_node2, new_node)
# newproj.show_info('Y','Y')
newproj.save_project()
ShowTree(newproj)
# print('---delete test---')
# newproj.save_project('before del.xml')
# newproj.del_all_sub()
# newproj.check_del_sub(T='Line')
# newproj.show_sub()
# newproj.save_project('after del.xml')
# newproj.check_del_sub('P',D='Density')
# newproj.save_project()
# newproj.show_info('','Y')
# print('--- change attribute test ---')
# newproj.show_sub()
# new_node2.update(D='this has been changed!')
# point1 = Point(1,2,0.2,'point1 has no name')
# print(point1.elmt.attrib)
# newproj.sub(point1)
# point1.show_self()
# newproj.check_del_sub('P',N='Fc28')
# newproj.show_sub()
# newproj.save_project()
# print('---search test---')
# newproj.findall_by_xpath('.//','Y')
# print('---find all sub by key&value test----')
# results=newproj.findall_by_attribute(N='test param')
# print(results)
# print(newproj.verify_attributes(T='Project'))
# ResultsTable(results)
'''''
