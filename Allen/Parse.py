from neuromllite import *

import random
import opencortex.utils.color as occ

import neuroml.loaders as loaders
import neuroml.writers as writers

import math

import csv
import sys


def rotate(x, y, theta):

    x_ = x * math.cos(theta) - y * math.sin(theta)
    y_ = x * math.sin(theta) + y * math.cos(theta)

    return x_, y_

def get_oriented_cell(cell_file, theta_z, theta_x):
    
    new_ref = "ROTATED_"+cell_file.split('.')[0]

    doc = loaders.NeuroMLLoader.load(cell_file)
    print("Loaded morphology file from: "+cell_file)

    doc.cells[0].id = new_ref


    print("Orienting %s radians around z axis, %s radians around x axis"%(theta_z, theta_x))


    for segment in doc.cells[0].morphology.segments:

        if segment.proximal:

            segment.proximal.x, segment.proximal.y = rotate(segment.proximal.x, segment.proximal.y, theta_z)
            segment.proximal.y, segment.proximal.z = rotate(segment.proximal.y, segment.proximal.z, theta_x)

        segment.distal.x, segment.distal.y = rotate(segment.distal.x, segment.distal.y, theta_z)
        segment.distal.y, segment.distal.z = rotate(segment.distal.y, segment.distal.z, theta_x)


    new_cell_file = new_ref+'.cell.nml'

    writers.NeuroMLWriter.write(doc,new_cell_file)
    
    return new_ref, new_cell_file

def generate(reference, 
             only_areas_matching=None, 
             only_ids_matching=None,
             include_contra=False,
             include_connections=True,
             include_detailed_cells=False):

    colors = {}
    centres = {}
    pop_ids = []
    used_ids = {}
    names = {}
    areas = {}

    with open('nature13186-s2_1.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for w in reader:
            print w
            if w[0] != 'id':
                short = w[3].replace(', ','_')
                name = w[4].strip('"')
                names[short]=name

    with open('nature13186-s2_2.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for w in reader:
            print w
            if w[0] != 'ID':
                short = w[2].replace(', ','_')
                area = w[4].strip('"')
                areas[short]=area

    for n in names: print('%s: \t%s'%(n,names[n]))
    for a in areas: print('%s: \t%s'%(a,areas[a]))
    #exit()

    ################################################################################
    ###   Build a new network

    net = Network(id=reference)
    net.notes = "NOTE: this is only a quick demo!! Do not use it for your research assuming an accurate conversion of the source data!!! "

    #cell = Cell(id='dummycell', pynn_cell='IF_cond_alpha')
    #cell.parameters = { "tau_refrac":5, "i_offset":.1 }
    cell = Cell(id='dummycell', neuroml2_source_file='passiveSingleCompCell.cell.nml')
    
    
    net.cells.append(cell)

    net.synapses.append(Synapse(id='ampa', 
                                pynn_receptor_type='excitatory', 
                                pynn_synapse_type='cond_alpha', 
                                parameters={'e_rev':-10, 'tau_syn':2}))

    '''                            
    r1 = RectangularRegion(id='region1', x=0,y=0,z=0,width=1000,height=100,depth=1000)
    net.regions.append(r1)
    default_cell = Cell(id='L23PyrRS', neuroml2_source_file='TestSmall/L23PyrRS.cell.nml')
    net.cells.append(default_cell)
    p0 = Population(id='pop0', size=5, component=default_cell.id, properties={'color':'0 .8 0'})
    net.populations.append(p0)
    net.populations[0].random_layout = RandomLayout(region=r1.id)'''

    detailed_cells = ['AA0289'] if include_detailed_cells else []
    
    for dc in detailed_cells:
        
        ll = SingleLocation()
        ll.location = Location(x=0,y=0,z=0)
        orig_file='%s_active.cell.nml'%dc
        
        new_ref, new_cell_file = get_oriented_cell(orig_file, math.pi,math.pi/2)
        
        print("Translated %s to %s"%(orig_file, new_cell_file))

        mo = Cell(id=dc, neuroml2_source_file='%s_active.cell.nml'%dc)
        net.cells.append(mo)
        p1 = Population(id='pop_%s'%dc, 
                        size=1, 
                        component=mo.id, 
                        properties={'color':'.8 0 0'})
        p1.single_location=ll 
        net.populations.append(p1)
        
        mo = Cell(id=new_ref, neuroml2_source_file=new_cell_file)
        net.cells.append(mo)
        p1 = Population(id='pop_%s'%new_ref, 
                        size=1, 
                        component=new_ref, 
                        properties={'color':'0 0.8 0'})
        p1.single_location=ll 
        net.populations.append(p1)


    f = open('ABA12.tsv')
    for l in f:
        w = l.split()
        print w
        pre_id = w[0].replace('-','_').replace('/','_')
        if pre_id != '[0]':

            match = False
            if only_ids_matching==None:
                match = True
            else:
                for i in only_ids_matching:
                    if i=='*' or i in pre_id:
                        match = True


            if match:

                scale = 1000
                x0 = float(w[2])*scale
                all = [ (pre_id, x0)]
                if include_contra:
                    all = [ (pre_id, x0), ('CONTRA_%s'%pre_id, x0*-1)]

                for a in all:
                    id = a[0]
                    x = a[1]
                    centres[id] = (x,float(w[3])*scale,float(w[4])*scale)
                    colors[id] = w[1]

                    repl = id
                    name = names[w[0]]
                    short_name3 = w[0][:3]
                    short_name4 = w[0][:4]
                    short_name5 = w[0][:5]
                    short_name6 = w[0][:6]
                    short_name7 = w[0][:7]

                    if w[0] in areas:
                        area = areas[w[0]]  
                    elif short_name7 in areas:
                           area = areas[short_name7]  
                    elif short_name6 in areas:
                           area = areas[short_name6]  
                    elif short_name5 in areas:
                           area = areas[short_name5]  
                    elif short_name4 in areas:
                           area = areas[short_name4]  
                    elif short_name3 in areas:
                           area = areas[short_name3]  
                    else:
                        area = '???'

                    match = False
                    if only_areas_matching==None:
                        match = True
                    else:
                        for a in only_areas_matching:
                            if a in area:
                                match = True


                    if match:

                        p = centres[repl]
                        used_ids[id] = '_%s'%repl if repl[0].isdigit() else repl

                        region_name = name.split(',')[0].replace(' ','_')
                        region_name = used_ids[id]
                        r = RectangularRegion(id=region_name, x=p[0],y=p[1],z=p[2],width=1,height=1,depth=1)
                        net.regions.append(r)


                        color = '.8 .8 .8'
                        if 'Thalamus' in area:
                            color = occ.THALAMUS_2
                        if 'Isocortex' in area:
                            color = occ.L23_PRINCIPAL_CELL
                        if 'Olfactory' in area:
                            color = occ.L4_PRINCIPAL_CELL
                        if 'Cerebe' in area:
                            color = occ.L5_PRINCIPAL_CELL
                        if 'Hippocampal' in area:
                            color = occ.L6_PRINCIPAL_CELL

                        if '1' in id:
                            color = occ.THALAMUS_2
                        if '2_3' in id:
                            color = occ.L23_PRINCIPAL_CELL
                        if '4' in id:
                            color = occ.L4_PRINCIPAL_CELL
                        if '5' in id:
                            color = occ.L5_PRINCIPAL_CELL
                        if '6' in id:
                            color = occ.L6_PRINCIPAL_CELL


                        p0 = Population(id=used_ids[id], 
                                        size=1, 
                                        component=cell.id, 
                                        properties={'color':'%s'%(color),
                                                    'radius':50,
                                                    'name':name,
                                                    'area':area},
                                        random_layout = RandomLayout(region=r.id))

                        net.populations.append(p0)
                        pop_ids.append(id)

    #print centres.keys()


    if include_connections:
        with open('nature13186-s4_W_ipsi.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            indices = {}
            for w in reader:
                #print w
                if w[0]=='ROOT':
                    for i in range(len(w)):
                        indices[i]=w[i]
                    print indices
                else:
                    pre = w[0]
                    for i in range(len(w)):
                        if i!=0:
                            weight = float(w[i])
                            if weight>0:
                                post = indices[i]
                                print('Connection %s -> %s of %s'%(pre, post, weight))

                                if weight>0.0:

                                    if pre in used_ids and post in used_ids:
                                        print('Adding conn from %s -> %s of %s'%(pre, post, weight))


                                        ################################################################################
                                        ###   Add a projection

                                        net.projections.append(Projection(id='proj_%s_%s'%(used_ids[pre],used_ids[post]),
                                                                          presynaptic=used_ids[pre], 
                                                                          postsynaptic=used_ids[post],
                                                                          synapse='ampa',
                                                                          weight=weight,
                                                                          random_connectivity=RandomConnectivity(probability=1)))




    from neuromllite import Simulation
    #print(net)

    print(net.to_json())
    new_file = net.to_json_file('%s.json'%net.id)

    sim = Simulation(id='Sim_%s'%net.id,
                     network=new_file,
                     duration='1000',
                     dt='0.025',
                     recordTraces={'all':'*'})


    ################################################################################
    ###   Export to some formats
    ###   Try:
    ###        python Example1.py -graph2

    from neuromllite.NetworkGenerator import check_to_generate_or_run
    import sys

    check_to_generate_or_run(sys.argv, sim)


if __name__ == '__main__':
    
    if '-thal' in sys.argv:
        generate('Thalamus',only_areas_matching=['Thalamus'],
             include_contra=True,
             include_connections=True)
        
    elif '-olf' in sys.argv:
        generate('OlfactoryAreas',only_areas_matching=['Olfactory Areas'],
             include_contra=False,
             include_connections=True)
             
    elif '-mo' in sys.argv:
        generate('MCortex',only_ids_matching=['MO'],
             include_contra=False,
             include_connections=True)
             
    elif '-vis' in sys.argv:
        generate('VIS',only_ids_matching=['VIS'],
             include_contra=True,
             include_connections=True)
             
    elif '-cell' in sys.argv:
        generate('DetailedCell1',only_ids_matching=['*'],
             include_contra=True,
             include_connections=False,
             include_detailed_cells=True)
             
    elif '-test' in sys.argv:
        generate('DTest1',only_ids_matching=['VI'],
             include_contra=True,
             include_connections=False,
             include_detailed_cells=True)
    else:  
        generate('Full')
