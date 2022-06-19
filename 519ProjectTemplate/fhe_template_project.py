from distutils.command.build_scripts import first_line_re
from eva import EvaProgram, Input, Output, evaluate
from eva.ckks import CKKSCompiler
from eva.seal import generate_keys
from eva.metric import valuation_mse
import timeit
import networkx as nx
from random import random
import math

VERTEX_COUNT = 60
K = 5
P = 0.4

result = []

# Using networkx, generate a random graph
# You can change the way you generate the graph
def generateGraph(n, k, p):
    #ws = nx.cycle_graph(n)
    ws = nx.connected_watts_strogatz_graph(n,k,p)
    # print('graph', serializeGraphZeroOne(ws,1))
    return ws


def depth_first_search(connectivity, start):
    visited = []
    stack = [start]

    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.append(vertex)
            for neighbor in connectivity[vertex]:
                stack.append(neighbor)
    
    print('depth_first_search: ', visited)
    return visited

def prepare_connectivity_map(graph):
    graph_as_arr = graph[0]
    connectivity_map = {}

    for i in range(VERTEX_COUNT):
        connectivity_map[i] = []
        for j in range(VERTEX_COUNT):
            if graph_as_arr[i*VERTEX_COUNT+j] == 1:
                connectivity_map[i].append(j)

    print('connectivity_map: ', connectivity_map)

    return connectivity_map

def find_max_depth(connectivity_map):
    max_depth = 0
    for i in range(VERTEX_COUNT):
        if connectivity_map[i] == []:
            continue
        else:
            depth = 0
            visited = []
            stack = [i]
            while stack:
                vertex = stack.pop()
                if vertex not in visited:
                    visited.append(vertex)
                    for neighbor in connectivity_map[vertex]:
                        stack.append(neighbor)
                    depth += 1
            if depth > max_depth:
                max_depth = depth
    return max_depth


# Tarjan's algorithm for finding articulation points
def checkAP(graph):
    # print('graphDict', graph[1])
    # print('graphArr', graph[0])
    connectivity_map = prepare_connectivity_map(graph)
    
    max_depth = find_max_depth(connectivity_map)

    suspects = []

    for i in range(VERTEX_COUNT):
        omitted_connectivity_map = connectivity_map.copy()
        omitted_connectivity_map.pop(i)
        
        try:
            if len(depth_first_search(omitted_connectivity_map, 0)) < max_depth:
                suspects.append(i)
        except:
            pass

    articulation_points = []

    for i in range(len(suspects)):
        if len(connectivity_map[suspects[i]]) != 0:
            articulation_points.append(i)

    print('articulation points', articulation_points)
    
    


# If there is an edge between two vertices its weight is 1 otherwise it is zero
# You can change the weight assignment as required
# Two dimensional adjacency matrix is represented as a vector
# Assume there are n vertices
# (i,j)th element of the adjacency matrix corresponds to (i*n + j)th element in the vector representations
def serializeGraphZeroOne(GG,vec_size):
    n = GG.size()
    graphdict = {}
    g = []
    for row in range(n):
        for column in range(n):
            if GG.has_edge(row, column) or row==column: # I assumed the vertices are connected to themselves
                weight = 1
            else:
                weight = 0 
            g.append( weight  )  
            key = str(row)+'-'+str(column)
            graphdict[key] = [weight] # EVA requires str:listoffloat
    # EVA vector size has to be large, if the vector representation of the graph is smaller, fill the eva vector with zeros
    for i in range(vec_size - n*n): 
        g.append(0.0)
    return g, graphdict

# To display the generated graph
def printGraph(graph,n):
    for row in range(n):
        for column in range(n):
            print("{:.5f}".format(graph[row*n+column]), end = '\t')
        print() 

# Eva requires special input, this function prepares the eva input
# Eva will then encrypt them
def prepareInput(n, m):
    input = {}
    GG = generateGraph(n,3,0.5)
    graph, graphdict = serializeGraphZeroOne(GG,m)
    input['Graph'] = graph
    return input

def find_remaining_nodes(number_of_nodes, current_node):
    remaining_nodes = []

    for each in range(number_of_nodes):
        remaining_nodes.append(0)

    remaining_nodes[current_node] = 1

    return remaining_nodes

def visit_node(current):
    global visited_nodes
    global stack
    global results

    if not visited_nodes[current]:
        result.append(current)
        visited_nodes[current] = True
        dfs_stack.pop()
# This is the dummy analytic service
# You will implement this service based on your selected algorithm
# you can other parameters using global variables !!! do not change the signature of this function 
def graphanalticprogram(graph):
    reval = graph
    # dir(graph)
    # ['__add__', '__class__', '__delattr__', '__dict__', '__dir__', 
    # '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', 
    # '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', 
    # '__lshift__', '__lt__', '__module__', '__mul__', '__ne__', '__neg__', 
    # '__new__', '__pow__', '__radd__', '__reduce__', '__reduce_ex__', 
    # '__repr__', '__rmul__', '__rshift__', '__rsub__', '__setattr__', 
    # '__sizeof__', '__str__', '__sub__', '__subclasshook__', '__weakref__', 
    # 'program', 'term']
    
    # dir(graph.program)
#     ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__enter__', 
#     '__eq__', '__exit__', '__format__', '__ge__', '__getattribute__', '__gt__', 
#     '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__',
#     '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__',
#     '__sizeof__', '__str__', '__subclasshook__', '_make_dense_constant', 
#     '_make_input', '_make_left_rotation', '_make_output', '_make_right_rotation', 
#     '_make_term', '_make_uniform_constant', 'inputs', 'n', 'name', 
#     'outputs', 'set_input_scales', 'set_output_ranges', 'to_DOT', 'vec_size']
    
    global first_pass
    global node_count
    global dfs_stack
    global articulation_point_stack
    global visited
    global initialnode
    global current_node

    remaining_nodes = find_remaining_nodes(node_count, current_node)

    while True:
        if len(dfs_stack) == 0:
            if len(articulation_point_stack) == 0:
                print("articulation points are:", str(result))
                return graph

            else:
                visit_node(current_node)
        
        else:
            break

    return remaining_nodes
    
# Do not change this 
# the parameter n can be passed in the call from simulate function
class EvaProgramDriver(EvaProgram):
    def __init__(self, name, vec_size=4096, n=4):
        self.n = n
        super().__init__(name, vec_size)

    def __enter__(self):
        super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)

# Repeat the experiments and show averages with confidence intervals
# You can modify the input parameters
# n is the number of nodes in your graph
# If you require additional parameters, add them
def simulate(n):
    m = 4096*4
    # print("Will start simulation for ", n)
    config = {}
    config['warn_vec_size'] = 'false'
    config['lazy_relinearize'] = 'true'
    config['rescaler'] = 'always'
    config['balance_reductions'] = 'true'
    inputs = prepareInput(n, m)

    graphanaltic = EvaProgramDriver("graphanaltic", vec_size=m,n=n)
    with graphanaltic:
        graph = Input('Graph')
        reval = graphanalticprogram(graph)
        Output('ReturnedValue', reval)
    
    prog = graphanaltic
    prog.set_output_ranges(30)
    prog.set_input_scales(30)

    start = timeit.default_timer()
    compiler = CKKSCompiler(config=config)
    compiled_multfunc, params, signature = compiler.compile(prog)
    compiletime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    public_ctx, secret_ctx = generate_keys(params)
    keygenerationtime = (timeit.default_timer() - start) * 1000.0 #ms
    
    start = timeit.default_timer()
    encInputs = public_ctx.encrypt(inputs, signature)
    encryptiontime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    encOutputs = public_ctx.execute(compiled_multfunc, encInputs)
    executiontime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    outputs = secret_ctx.decrypt(encOutputs, signature)
    decryptiontime = (timeit.default_timer() - start) * 1000.0 #ms

    start = timeit.default_timer()
    reference = evaluate(compiled_multfunc, inputs)
    referenceexecutiontime = (timeit.default_timer() - start) * 1000.0 #ms
    
    # Change this if you want to output something or comment out the two lines below
    # for key in outputs:
        # print(key, float(outputs[key][0]), float(reference[key][0]))

    mse = valuation_mse(outputs, reference) # since CKKS does approximate computations, this is an important measure that depicts the amount of error

    return compiletime, keygenerationtime, encryptiontime, executiontime, decryptiontime, referenceexecutiontime, mse


if __name__ == "__main__":
    simcnt = 3 #The number of simulation runs, set it to 3 during development otherwise you will wait for a long time
    # For benchmarking you must set it to a large number, e.g., 100
    #Note that file is opened in append mode, previous results will be kept in the file
    resultfile = open("results.csv", "a")  # Measurement results are collated in this file for you to plot later on
    resultfile.write("NodeCount,PathLength,SimCnt,CompileTime,KeyGenerationTime,EncryptionTime,ExecutionTime,DecryptionTime,ReferenceExecutionTime,Mse\n")
    resultfile.close()
    
    print("Simulation campaing started:")
    for nc in range(36,40,4): # Node counts for experimenting various graph sizes
        n = nc
        resultfile = open("results.csv", "a") 
        for i in range(simcnt):
            #Call the simulator
            compiletime, keygenerationtime, encryptiontime, executiontime, decryptiontime, referenceexecutiontime, mse = simulate(n)
            res = str(n) + "," + str(i) + "," + str(compiletime) + "," + str(keygenerationtime) + "," +  str(encryptiontime) + "," +  str(executiontime) + "," +  str(decryptiontime) + "," +  str(referenceexecutiontime) + "," +  str(mse) + "\n"
            # print(res)
            # print("NodeCount:", n, "Simulation:", i)
            # print("CompileTime:", compiletime, "KeyGenerationTime:", keygenerationtime, "EncryptionTime:", encryptiontime, "ExecutionTime:", executiontime, "DecryptionTime:", decryptiontime, "ReferenceExecutionTime:", referenceexecutiontime, "Mse:", mse)
            # resultfile.write(res)
        resultfile.close()


exampleGraph = serializeGraphZeroOne(generateGraph(VERTEX_COUNT, K, P), 200)
checkAP(exampleGraph)