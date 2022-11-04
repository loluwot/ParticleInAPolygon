from collections import defaultdict
import PySimpleGUI as sg
from utils import *
import math

pi = math.pi
RADIUS = 2
SNAP = 5

sg.theme('DarkAmber')
layout = [[sg.Graph(canvas_size=(400, 400), 
            graph_bottom_left=(-105,-105), 
            graph_top_right=(105,105), 
            background_color='white', 
            key='graph',
            enable_events=True, drag_submits=True, motion_events=True)], 
            [sg.Button('Enable Line',button_color=('white', 'green'), key='line'), sg.Button('Enable Erase', button_color=('white', 'green'), key='erase')],
            [sg.Button('Analyze', key='analyze')]]

window = sg.Window('Window Title', layout,  element_justification='c')
graph = window['graph']
# positions = dict()
# last_pos = None
# dragging = False
# selected = None
net_state = defaultdict(lambda: None, {"last_pos":None, "dragging":False, "selected":None, 'positions':dict()})
toggle = {'line':False, 'erase':False}
toggle_states = {'line':[{'button_color':('white', 'green'), 'name':'Enable Line'}, {'button_color':('white', 'red'), 'name':'Disable Line'}],
                 'erase':[{'button_color':('white', 'green'), 'name':'Enable Erase'}, {'button_color':('white', 'red'), 'name':'Disable Erase'}]}

def draw_point_handling(event, values):
    global net_state, graph
    mouse = values['graph']
    if event == 'graph':
        if net_state['last_pos'] is None:
            net_state['last_pos'] = mouse
        elif not net_state['dragging'] and net_state['last_pos'] != mouse:
            net_state['selected'] = get_point(net_state['last_pos'], net_state['positions'], dist=RADIUS+SNAP)
            net_state['old_selected'] = net_state['selected']
            if net_state['selected'] is not None:
                net_state['dragging'] = True
        if net_state['dragging']:
            graph.delete_figure(net_state['selected'])
            del net_state['positions'][net_state['selected']]
            net_state['selected'] = graph.draw_circle(mouse, RADIUS, line_color='red', fill_color='red')
            net_state['positions'][net_state['selected']] = mouse
            keys = list(net_state['lines'].keys())
            for key in keys:
                # print(key, old_selected)
                if net_state['old_selected'] in key:
                    other = key[1 - key.index(net_state['old_selected'])]
                    graph.delete_figure(net_state['lines'][key])
                    new_key = tuple(sorted([other, net_state['selected']]))
                    del net_state['lines'][key]
                    net_state['lines'][new_key] = graph.draw_line(net_state['positions'][net_state['selected']], net_state['positions'][other])
            net_state['old_selected'] = net_state['selected']
    if event == 'graph+UP':
        if mouse != (None, None) and not net_state['dragging']:
            circ = graph.draw_circle(mouse, RADIUS, line_color='red', fill_color='red')
            net_state['positions'][circ] = mouse
            print(circ, mouse)
        net_state['last_pos'], net_state['dragging'], net_state['selected'] = None, False, None


def erase_point_handling(event, values):
    global net_state, graph
    mouse = values['graph']
    if event == 'graph':
        if net_state['last_pos'] is None:
            net_state['last_pos'] = mouse
        elif not net_state['dragging'] and net_state['last_pos'] != mouse:
            net_state['dragging'] = True
            net_state['drag_rect'] = graph.draw_rectangle(net_state['last_pos'], mouse)
        if net_state['dragging']:
            graph.delete_figure(net_state['drag_rect'])
            net_state['drag_rect'] = graph.draw_rectangle(net_state['last_pos'], mouse)
    if event == 'graph+UP':
        if mouse != (None, None):
            if not net_state['dragging']:
                net_state['selected'] = get_point(mouse, net_state['positions'], dist=RADIUS+SNAP)
                if net_state['selected'] is not None:
                    graph.delete_figure(net_state['selected'])
                    del net_state['positions'][net_state['selected']]
                    keys = list(net_state['lines'].keys())
                    for key in keys:
                        if net_state['selected'] in key:
                            graph.delete_figure(net_state['lines'][key])
                            del net_state['lines'][key]
                    
            else:
                graph.delete_figure(net_state['drag_rect'])
                keys = list(net_state['lines'].keys())
                for circ, point in get_points_in_rect([net_state['last_pos'], mouse], net_state['positions']):
                    graph.delete_figure(circ)
                    del net_state['positions'][circ]
                    for key in keys:
                        if circ in key:
                            graph.delete_figure(net_state['lines'][key])
                            del net_state['lines'][key]
        net_state['last_pos'], net_state['dragging'], net_state['selected'] = None, False, None

def draw_line_handling(event, values):
    global net_state, graph
    mouse = values['graph']
    if event == 'graph':
        if net_state['last_pos'] is None:
            net_state['last_pos'] = mouse
        elif not net_state['dragging'] and net_state['last_pos'] != mouse:
            net_state['dragging'] = True
        # if net_state['dragging']:
        #     graph.delete_figure(net_state['selected'])
        #     del net_state['positions'][net_state['selected']]
        #     net_state['selected'] = graph.draw_circle(mouse, RADIUS, line_color='red', fill_color='red')
        #     net_state['positions'][net_state['selected']] = mouse
        #     pass
    if event == 'graph+UP':
        if mouse != (None, None) and not net_state['dragging']:
            if net_state['selected'] is None:
                net_state['selected'] = get_point(mouse, net_state['positions'], dist=RADIUS+SNAP)
            else:
                second_selected = get_point(mouse, net_state['positions'], dist=RADIUS+SNAP)
                if net_state['adj_list'] is None:
                    net_state['adj_list'] = defaultdict(list)
                net_state['adj_list'][net_state['selected']].append(second_selected)
                if net_state['lines'] is None:
                    net_state['lines'] = dict()
                selected_state = tuple(sorted([net_state['selected'], second_selected]))
                net_state['lines'][selected_state] = graph.draw_line(net_state['positions'][net_state['selected']], net_state['positions'][second_selected])
                if net_state['drag_line'] is not None:
                    graph.delete_figure(net_state['drag_line'])
                net_state['selected'] = None
        net_state['last_pos'], net_state['dragging'] = None, False
    
    if event == 'graph+MOVE':
        if net_state['selected'] is not None:
            if net_state['drag_line'] is not None:
                graph.delete_figure(net_state['drag_line'])    
            net_state['drag_line'] = graph.draw_line(net_state['positions'][net_state['selected']], mouse)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        window.close()
        import sys
        sys.exit(0)
    if event == 'analyze':
        # valid, *polygon_props = validate_polygon((net_state['positions'], net_state['adj_list']))
        polygon_nodes = validate_polygon((net_state['positions'], net_state['adj_list']))
        # if valid:
        break
    if event in toggle:
        toggle[event] = not toggle[event]
        state = toggle_states[event][toggle[event]]
        window.Element(event).Update(state['name'], button_color=state['button_color'])
    if toggle['erase']:
        erase_point_handling(event, values)
    else:
        if toggle['line']:
            draw_line_handling(event, values)
        else:
            draw_point_handling(event, values)
    mouse = values['graph']


import matplotlib.pyplot as plt
from matplotlib import cm

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

polygon = Polygon([net_state['positions'][i] for i in polygon_nodes])

sol = boundary_approx(30, polygon)
xx = np.linspace(-1, 1, 100)
yy = np.linspace(-1, 1, 100)
X, Y = np.meshgrid(xx, yy)
ax.plot_surface(X, Y, sol.n_sol(1)(X, Y)**2, cmap=cm.viridis, alpha=0.9,)
polygon.draw()
plt.show()

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        window.close()
        import sys
        sys.exit(0)