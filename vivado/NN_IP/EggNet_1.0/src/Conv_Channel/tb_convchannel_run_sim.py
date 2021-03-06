# %% public imports
import os 
import shutil
import subprocess
import filecmp
import numpy as np
import matplotlib.pyplot as plt 

# %% import custom modules
import vhdl_testbench as tb 

# %% Helper function to split array into n roughly equal parts
def chunk_array(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

# %% Quantization function for floating point weights
def quantize(a):
    return min(max(int(a/0.002),-128), 127)

# %% Pooling function
    
def pool(CO, file_name_pool_in, file_name_pool_out, width):
    buffer = np.ndarray((2,width), dtype=int)
    for i in range(0, CO):
        i_str = str(i)
        if len(i_str) == 1:
            i_str = "0" + i_str
        file_name_in_current = file_name_pool_in.replace("{I}", i_str)
        file_name_out_current = file_name_pool_out.replace("{I}", i_str)
        pool_input_file = open(file_name_in_current, "r")
        pool_output_file = open(file_name_out_current, "w")
        
        buf_i = 0
        buf_j = 0
        
        for line in pool_input_file:
            buffer[buf_j][buf_i] = int(line)
            if buf_i != width - 1:
                buf_i += 1
            elif buf_j != 1:
                buf_j += 1
                buf_i = 0
            else:
                for x in range(0, int(width/2)):
                    vals = [buffer[0][x*2], buffer[0][x*2+1], buffer[1][x*2], buffer[1][x*2+1]]
                    max_val = max(vals)
                    pool_output_file.write(str(max_val) + "\n")
                buf_i = 0
                buf_j = 0
        
        pool_input_file.close()
        pool_output_file.close()

# %% parameters
KEEP_TEMPORARY_FILES = True
KERNEL_SIZE = 3
NUMBER_OF_TEST_BLOCKS = 3
CI_L1 = 1
CO_L1 = 16
CI_L2 = 16
CO_L2 = 32

IMG_WIDTH = 28
IMG_HIGTH = 28
BLOCK_SIZE = IMG_WIDTH*IMG_HIGTH

l1_weights_file_name = "../../../../../net/np/k_3_conv2d_1_0.txt"
l2_weights_file_name = "../../../../../net/np/k_8_conv2d_2_0.txt"

# %% create tmp folder, delete folder if not tmp exists and create new one
if os.path.isdir('tmp'):
    shutil.rmtree('tmp')
    
try : os.mkdir('tmp')
except : print("Error creating tmp folder!")

# %% create test data file
image_data = tb.gen_testdata(BLOCK_SIZE,NUMBER_OF_TEST_BLOCKS, CI_L1)

# %% generate test vectors 
l1_test_vectors = tb.get_vectors_from_data(image_data,IMG_WIDTH,IMG_HIGTH,NUMBER_OF_TEST_BLOCKS)

# %% generate test kernels 
l1_test_kernels = tb.get_Kernels(l1_test_vectors,IMG_WIDTH)

# %% calculate Layer 1 output as new memory controller input 
l1_weights_file = open(l1_weights_file_name, 'r')
l1_weights = np.array(list(map(quantize, np.loadtxt(l1_weights_file)))).reshape((3,3,CI_L1,CO_L1))
l1_weights_file.close()

l1_weights_reshaped = np.ndarray((CO_L1,CI_L1,3,3))
for i in range(0, CI_L1):
    for j in range(0, CO_L1):
        for x in range(0,KERNEL_SIZE):
            for y in range(0,KERNEL_SIZE):
                l1_weights_reshaped[j][i][y][x] = l1_weights[x][y][i][j]
                
l1_msb = np.ones(CO_L1,dtype=np.int32)*15
l1_features = tb.conv_2d(l1_test_kernels,l1_weights_reshaped,l1_msb)
tb.write_features_to_file(l1_features,layernumber=1)

conv2d0_input_files = [None]*KERNEL_SIZE*KERNEL_SIZE
for i in range(0, KERNEL_SIZE*KERNEL_SIZE):
    conv2d0_input_files[i] = open("tmp/conv2d_0_input" + str(i) + ".txt", "w")
    
for i in range(0, NUMBER_OF_TEST_BLOCKS):
    for j in range(0, IMG_WIDTH*IMG_HIGTH):
        for c in range(0, CI_L1):
            for x in range(0, KERNEL_SIZE):
                for y in range(0, KERNEL_SIZE):
                    num = y + x*KERNEL_SIZE
                    conv2d0_input_files[num].write(str(l1_test_kernels[i][j][x][y][c]) + "\n")
    
for i in range(0, KERNEL_SIZE*KERNEL_SIZE):
    conv2d0_input_files[i].close()


# %% Run test and compare output

print("Compiling and running conv2d0 testbench...")

subprocess.call("run_conv2d_0.bat")

file_name_sim = "tmp/conv2d_0_output{I}.txt"
file_name_emu = "tmp/feature_map_L1_c{I}.txt"

for i in range(0, CO_L1):
    i_str = str(i)
    if len(i_str) == 1:
        i_str = "0" + i_str
    file_name_sim_current = file_name_sim.replace("{I}", i_str)
    file_name_emu_current = file_name_emu.replace("{I}", str(i))
    if filecmp.cmp(file_name_sim_current, file_name_emu_current) != True:
        print("Simulation and emulation output not the same for conv2d0, channel " + str(i))
        exit

print("Simulation and emulation output the same for conv2d0")

# %% Pooling after layer 1

pool(CO_L1, file_name_sim, "tmp/pool_output{I}.txt", IMG_WIDTH)

#New parameters after pooling
IMG_WIDTH //= 2
IMG_HIGTH //= 2
BLOCK_SIZE = IMG_WIDTH*IMG_HIGTH

# %% Get input for layer 2 from output of layer 1
file_name_in = "tmp/pool_output{I}.txt"

test_array = np.ndarray((CI_L2, NUMBER_OF_TEST_BLOCKS, BLOCK_SIZE), dtype=np.uint8)
    
for i in range(0, CI_L2):
    i_str = str(i)
    if len(i_str) == 1:
        i_str = "0" + i_str
    file_name_in_current = file_name_in.replace("{I}", i_str)
    data = np.loadtxt(file_name_in_current, dtype=np.uint8)
    test_array[i] = chunk_array(data, NUMBER_OF_TEST_BLOCKS)

test_array_reshaped = np.ndarray((NUMBER_OF_TEST_BLOCKS, BLOCK_SIZE, CI_L2), dtype=np.uint8)

for i in range(0, CI_L2):
    for j in range(0, BLOCK_SIZE):
        for k in range(0, NUMBER_OF_TEST_BLOCKS):
            test_array_reshaped[k][j][i] = test_array[i][k][j]

l2_test_kernels = np.ndarray((NUMBER_OF_TEST_BLOCKS,IMG_WIDTH*IMG_HIGTH, 3, 3, CI_L2), dtype=np.uint8)
l2_test_vectors = tb.get_vectors_from_data(test_array_reshaped,IMG_WIDTH,IMG_HIGTH,NUMBER_OF_TEST_BLOCKS)
l2_test_kernels = tb.get_Kernels(l2_test_vectors,IMG_WIDTH)

# %% calculate Layer 2 output as new memory controller input 
l2_weights_file = open(l2_weights_file_name, 'r')
l2_weights = np.array(list(map(quantize, np.loadtxt(l2_weights_file)))).reshape((3,3,CI_L2,CO_L2))
l2_weights_file.close()

l2_weights_reshaped = np.ndarray((CO_L2,CI_L2,3,3))
for i in range(0, CI_L2):
    for j in range(0, CO_L2):
        for x in range(0,KERNEL_SIZE):
            for y in range(0,KERNEL_SIZE):
                l2_weights_reshaped[j][i][y][x] = l2_weights[x][y][i][j]

l2_msb = np.ones(CO_L2,dtype=np.int32)*15
l2_features = tb.conv_2d(l2_test_kernels,l2_weights_reshaped,l2_msb)
tb.write_features_to_file(l2_features,layernumber=2)

# %% Write input files for conv2d1 testbench
conv2d1_input_files = [[0 for i in range(KERNEL_SIZE*KERNEL_SIZE)] for j in range(CI_L2)]
for i in range(0, CI_L2):
    for j in range(0, KERNEL_SIZE*KERNEL_SIZE):
        i_str = str(i)
        if len(i_str) == 1:
            i_str = "0" + i_str
        conv2d1_input_files[i][j] = open("tmp/conv2d_1_c" + i_str + "input" + str(j) + ".txt", "w")
    
for i in range(0, NUMBER_OF_TEST_BLOCKS):
    for j in range(0, IMG_WIDTH*IMG_HIGTH):
        for c in range(0, CI_L2):
            for x in range(0, KERNEL_SIZE):
                for y in range(0, KERNEL_SIZE):
                    num = y + x*KERNEL_SIZE
                    conv2d1_input_files[c][num].write(str(l2_test_kernels[i][j][x][y][c]) + "\n")
    
for i in range(0, CI_L2):
    for j in range(0, KERNEL_SIZE*KERNEL_SIZE):
        conv2d1_input_files[i][j].close()

# %% Run test and compare output for layer 2

print("Compiling and running conv2d1 testbench...")

subprocess.call("run_conv2d_1.bat")

file_name_sim = "tmp/conv2d_1_output{I}.txt"
file_name_emu = "tmp/feature_map_L2_c{I}.txt"

for i in range(0, CO_L2):
    i_str = str(i)
    if len(i_str) == 1:
        i_str = "0" + i_str
    file_name_sim_current = file_name_sim.replace("{I}", i_str)
    file_name_emu_current = file_name_emu.replace("{I}", str(i))
    if filecmp.cmp(file_name_sim_current, file_name_emu_current) != True:
        print("Simulation and emulation output not the same for conv2d1, channel " + str(i))
        exit

print("Simulation and emulation output the same for conv2d1")


# %% Pooling after layer 2

pool(CO_L2, file_name_sim, "tmp/dense_layer_input{I}.txt", IMG_WIDTH)

#New parameters after pooling
IMG_WIDTH //= 2
IMG_HIGTH //= 2
BLOCK_SIZE = IMG_WIDTH*IMG_HIGTH

# %% Get input for dense layer

file_nn = open("tmp/nn_input.txt", "w")

for i in range(0, CO_L2):
    i_str = str(i)
    if len(i_str) == 1:
        i_str = "0" + i_str
    file_name = "tmp/dense_layer_input{I}.txt"
    file_name = file_name.replace("{I}", i_str)
    input_file = open(file_name, "r")
    input_lines = input_file.readlines()
    input_lines_chunked = chunk_array(input_lines, NUMBER_OF_TEST_BLOCKS)
    file_nn.writelines(input_lines_chunked[0])
    input_file.close()
    
file_nn.close()

# %% Get output for dense layer

denselayer_1_file_name = "../../../../../net/np/k_14_dense_1_0.txt"
denselayer_2_file_name = "../../../../../net/np/k_17_dense_2_0.txt"

DL1_INPUT_NEURONS = 1568
DL1_OUTPUT_NEURONS = 32
DL2_INPUT_NEURONS = 32
DL2_OUTPUT_NEURONS = 10

dl1_weights_file = open(denselayer_1_file_name, 'r')
dl1_weights = np.array(list(map(quantize, np.loadtxt(dl1_weights_file)))).reshape((DL1_INPUT_NEURONS, DL1_OUTPUT_NEURONS))
dl1_weights_file.close()

dl2_weights_file = open(denselayer_2_file_name, 'r')
dl2_weights = np.array(list(map(quantize, np.loadtxt(dl2_weights_file)))).reshape((DL2_INPUT_NEURONS, DL2_OUTPUT_NEURONS))
dl2_weights_file.close()

file_nn = open("tmp/nn_input.txt", "r")
denselayer_input = np.loadtxt(file_nn, dtype=np.int32)
file_nn.close()

dl1_output = np.matmul(denselayer_input, dl1_weights)
dl1_test_output = dl1_output
dl1_output >>= 8
dl1_output = np.clip(dl1_output, a_min = 0, a_max = 255)
dl2_output = np.matmul(dl1_output, dl2_weights)
dl2_output >>= 8
dl2_output = np.clip(dl2_output, a_min = 0, a_max = 255)

# %% delete tmp folder 
if not KEEP_TEMPORARY_FILES:
    shutil.rmtree('tmp')
