# -*- coding: utf-8 -*-

import os 
import shutil
import numpy as np
import re

num_layers = 2
file_names = ["../../../../../net/np/k_3_conv2d_1_0.txt",
         "../../../../../net/np/k_8_conv2d_2_0.txt"]
    
def quantize(a):
    return min(max(int(a/0.002),-128), 127)

if __name__ == '__main__':
    num_input_channels = [None]*num_layers
    num_output_channels = [None]*num_layers
    kernel_arrays = [None]*num_layers
    kernel_strings = [None]*num_layers
    channel_strings = [None]*num_layers
    
# %% create tmp folder, delete folder if not tmp exists and create new one
    if os.path.isdir('channels'):
        shutil.rmtree('channels')
        
    try : os.mkdir('channels')
    except : print("Error creating temp channel folder!")
    
    for i in range(0, num_layers):
        file = open(file_names[i], 'r')
        def_line = file.readline()
        regex = re.compile("# \(3, 3, (.*?)\)\n")
        channel_def = list(map(int, regex.match(def_line).group(1).split(',')))
        num_input_channels[i] = channel_def[0]
        num_output_channels[i] = channel_def[1]
        kernel_arrays[i] = list(map(quantize, np.loadtxt(file)))
        kernel_arrays[i] = np.array(kernel_arrays[i]).reshape((3,3,num_input_channels[i], num_output_channels[i]))
        kernel_strings[i] = np.ndarray((num_input_channels[i], num_output_channels[i]), dtype=object)

        for x in range(0, num_input_channels[i]):
            for y in range(0, num_output_channels[i]):
                kernel_strings[i][x][y] = "(" + \
                str(kernel_arrays[i][0][0][x][y]) + ", " +\
                str(kernel_arrays[i][1][0][x][y]) + ", " +\
                str(kernel_arrays[i][2][0][x][y]) + ", " +\
                str(kernel_arrays[i][0][1][x][y]) + ", " +\
                str(kernel_arrays[i][1][1][x][y]) + ", " +\
                str(kernel_arrays[i][2][1][x][y]) + ", " +\
                str(kernel_arrays[i][0][2][x][y]) + ", " +\
                str(kernel_arrays[i][1][2][x][y]) + ", " +\
                str(kernel_arrays[i][2][2][x][y]) + ")"
        channel_strings[i] = []
        for y in range(0, num_output_channels[i]):
            channel_strings[i].append('')
            channel_strings[i][y] += '('
            for x in range(0, num_input_channels[i]):
                channel_strings[i][y] += str(x) + " => "
                channel_strings[i][y] += kernel_strings[i][x][y]
                if x != num_input_channels[i] - 1:
                    channel_strings[i][y] += ', '
            channel_strings[i][y] += ')'
        file.close()
        
    tp_file = open('conv_channel_template.vhd', 'r')
    tp_str = tp_file.read()
    i_convchan = 0
    for i in range(0, num_layers):
        for j in range(0,len(channel_strings[i])):
            tp_str_new = tp_str.replace("ConvChannelTemplate", "ConvChannel" + str(i_convchan))
            tp_str_new = re.sub("constant KERNELS : kernel_array_t :=[^\n]*\n", "constant KERNELS : kernel_array_t := " + channel_strings[i][j] + ";\n", tp_str_new)
            tp_str_new = re.sub("\tN : integer :=[^\n]*\n", "\tN : integer := " + str(num_input_channels[i]) + ";\n", tp_str_new)
            tp_file_new = open("channels/convchannel" + str(i_convchan) + ".vhd", 'w')
            tp_file_new.write(tp_str_new)
            tp_file_new.close()
            i_convchan += 1
    tp_file.close();
    
    tp_file = open('conv2d_template.vhd', 'r')
    tp_str = tp_file.read()
    entity_str = \
"\tconvchan{I}" + " : entity " + "ConvChannel{J} " + "port map(\n\
\t\tClk_i, n_Res_i,\n\
\t\tValid_i, Valid_o, Last_i, Last_o, Ready_i, Ready_o,\n\
\t\tX_i,\n\
\t\tY_o({I+1}*BIT_WIDTH_OUT - 1 downto {I}*BIT_WIDTH_OUT)\n\
\t); \n\n"
    i_convchan = 0
    for i in range(0, num_layers):
        use_str = ""
        i_convchan_old = i_convchan
        for y in range(0, num_output_channels[i]):
            use_str += "use work.ConvChannel" + str(i_convchan) + ";\n"
            i_convchan += 1
        i_convchan = i_convchan_old
        tp_str_new = tp_str.replace("use work.kernel_pkg.all;\n", "use work.kernel_pkg.all;\n" + use_str)
        tp_str_new = tp_str_new.replace("Conv2DTemplate", "Conv2D_" + str(i))
        tp_str_new = re.sub("INPUT_CHANNELS : integer := [^\n]*\n", "INPUT_CHANNELS : integer := " + str(num_input_channels[i]) + ";\n", tp_str_new)
        tp_str_new = re.sub("OUTPUT_CHANNELS : integer := [^\n]*\n", "OUTPUT_CHANNELS : integer := " + str(num_output_channels[i]) + "\n", tp_str_new)
        tp_str_new += "\narchitecture beh of " + "Conv2D_" + str(i) + " is\n begin\n"
        
        for y in range(0, num_output_channels[i]):
            entity_str_new = entity_str.replace("{J}", str(i_convchan))
            entity_str_new = entity_str_new.replace("{I}", str(y))
            entity_str_new = entity_str_new.replace("{I+1}", str(y+1))
            tp_str_new += entity_str_new
            i_convchan += 1
        
        tp_str_new += "end beh;"
        tp_file_new = open("conv2d_" + str(i) + ".vhd", 'w')
        tp_file_new.write(tp_str_new)
        tp_file_new.close()
    tp_file.close();