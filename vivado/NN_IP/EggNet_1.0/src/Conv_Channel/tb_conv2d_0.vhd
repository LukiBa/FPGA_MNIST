library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.textio.all;
use ieee.std_logic_textio.all;
use work.kernel_pkg.all;
use work.Conv2D_0;

entity tb_conv2d_0 is
end tb_conv2d_0;

architecture beh of tb_conv2d_0 is
	constant BIT_WIDTH_IN : integer := 8;
	constant BIT_WIDTH_OUT : integer := 8;
	constant INPUT_CHANNELS : integer := 1;
	constant OUTPUT_CHANNELS : integer := 16;
	constant CLK_PERIOD : time := 10 ns; -- 100MHz
	constant IMG_WIDTH : integer := 28;
	constant IMG_HEIGHT : integer := 28;
	constant BATCH_SIZE : integer := 3;
	constant INPUT_ARRAY_SIZE : integer := IMG_WIDTH * IMG_HEIGHT * BATCH_SIZE;
	
	type t_pixel_array is array (0 to INPUT_ARRAY_SIZE - 1) of integer;
	type t_kernel_array is array (0 to KERNEL_SIZE - 1) of t_pixel_array;
	
	signal s_Clk_i, s_n_Res_i, s_Valid_i, s_Valid_o : std_logic;
	signal s_X_i : std_logic_vector(BIT_WIDTH_IN*INPUT_CHANNELS*KERNEL_SIZE - 1 downto 0);
	signal s_Y_o : unsigned(OUTPUT_CHANNELS*BIT_WIDTH_OUT - 1 downto 0);
	signal sim_ended : std_logic := '0';
	
	file kernel_file : text;
	constant char_num : string(1 to 10) := "0123456789";
	
begin
  
	uit : entity work.Conv2D_0
	generic map(
		BIT_WIDTH_IN,
		BIT_WIDTH_OUT,
		INPUT_CHANNELS,
		OUTPUT_CHANNELS
	) port map( --default generics
		Clk_i => s_Clk_i,
		n_Res_i => s_n_Res_i,
		Valid_i => s_Valid_i,
		Valid_o => s_Valid_o,
		X_i => s_X_i,
		Y_o => s_Y_o
	);
  
	-- Generates the clock signal
	clkgen : process
	begin
		if sim_ended = '0' then
			s_Clk_i <= '0';
			wait for CLK_PERIOD/2;
			s_Clk_i <= '1';
			wait for CLK_PERIOD/2;
		else
			wait;
		end if;
	end process clkgen;

	-- Generates the reset signal
	reset : process
	begin -- process reset
		s_n_Res_i <= '0';
		wait for 55 ns;
		s_n_Res_i <= '1';
		wait;
	end process; 
	
	get_output : process(s_Clk_i, sim_ended)
		variable K : integer := 0;
		type t_output_array is array(0 to OUTPUT_CHANNELS - 1) of t_pixel_array;
		variable output : t_output_array;
		variable output_line : line;
        variable file_name_out : string(1 to 23) := "tmp/conv2d_output00.txt";
	begin
		if s_Valid_o = '1' and rising_edge(s_Clk_i) then
			--report integer'image(K);
			for I in 0 to OUTPUT_CHANNELS - 1 loop
				output(I)(K) := to_integer(s_Y_o((I+1)*BIT_WIDTH_OUT - 1 downto I*BIT_WIDTH_OUT));
			end loop;
			K := K + 1;
		elsif sim_ended = '1' then
			for J in 0 to OUTPUT_CHANNELS - 1 loop
				file_name_out(18) := char_num(J/10 + 1);
				file_name_out(19) := char_num(J mod 10 + 1);
				file_open(kernel_file, file_name_out, write_mode);
				for I in 0 to INPUT_ARRAY_SIZE - 1 loop
					write(output_line, output(J)(I));
					writeline(kernel_file, output_line);
				end loop;
				file_close(kernel_file);
			end loop;
		end if;	
	end process;

	set_input : process
	    variable kernel_input : t_kernel_array;
        variable input_line : line;
        variable output_line : line;
        variable input_int : integer;
        variable file_name : string(1 to 21) := "tmp/conv2d_input0.txt";
		variable K : integer := 0;
	begin
		
		for I in 0 to KERNEL_SIZE - 1 loop
			file_name(17) := char_num(I+1);
            file_open(kernel_file, file_name, read_mode);
			K := 0;
            while not endfile(kernel_file) loop
                readline(kernel_file, input_line);
                read(input_line, input_int);
				kernel_input(I)(K) := input_int;
				K := K + 1;
            end loop;
            file_close(kernel_file);
		end loop;
		
		s_X_i <= (others => '0');
		s_Valid_i <= '0';
		wait until rising_edge(s_n_Res_i);
		for J in 0 to INPUT_ARRAY_SIZE - 1 loop
			wait until rising_edge(s_Clk_i);
			s_Valid_i <= '1';
			for I in 0 to KERNEL_SIZE - 1 loop
				s_X_i((I+1)*BIT_WIDTH_IN - 1 downto I*BIT_WIDTH_IN) <= std_logic_vector(to_unsigned(kernel_input(I)(J), BIT_WIDTH_IN));
			end loop;
		end loop;
		wait until rising_edge(s_Clk_i);
		s_Valid_i <= '0';
		s_X_i <= (others => '0');
		wait until rising_edge(s_Clk_i);
		wait until rising_edge(s_Clk_i);
		sim_ended <= '1';
		wait;
	end process;
end beh;