library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.kernel_pkg.all;
use work.Kernel3x3;
USE ieee.math_real.log2;
USE ieee.math_real.ceil;

entity ConvChannel is
	generic(
		BIT_WIDTH_IN : integer := 8;
		KERNEL_WIDTH_OUT : integer := 16;
		BIT_WIDTH_OUT : integer := 8;
		N : integer := 2
	);
	port(
		Clk_i : in std_logic;
		n_Res_i : in std_logic;
		Valid_i : in std_logic;
		X_i : in std_logic_vector(N*BIT_WIDTH_IN*KERNEL_SIZE - 1 downto 0);
		Y_o : out signed(BIT_WIDTH_OUT - 1 downto 0)
	);
end ConvChannel;

architecture beh of ConvChannel is
	
	constant SUM_WIDTH : integer := KERNEL_WIDTH_OUT + integer(ceil(log2(real(N))));
	
	signal K_out : signed(N*KERNEL_WIDTH_OUT - 1 downto 0);
	
	type term_vector_t is array (integer range <>) of signed(SUM_WIDTH - 1 downto 0);
	signal term_vector : term_vector_t(0 to N-1);
	
	type kernel_array_t is array (0 to N-1) of weight_array_t;
	constant DEFAULT_KERNELS : kernel_array_t :=
		((90,80,70,60,50,40,30,20,10),
		 (10,20,30,40,50,60,70,80,90));
		 
	--This is replaced by a script:
	--constant KERNELS : kernel_array_t :=
	--({kernel_array})
	
	function ternary_adder_tree
	(
		input_term_vector   : term_vector_t
	)
	return signed is
		constant    N                           : natural                       := input_term_vector'length;
		constant    term_vector                 : term_vector_t(0 to (N - 1))   := input_term_vector;
		constant    LEFT_TREE_N                 : natural                       := ((N + 2) / 3);
		constant    MIDDLE_TREE_N               : natural                       := (((N - LEFT_TREE_N) + 1) / 2);
		constant    RIGHT_TREE_N                : natural                       := (N - LEFT_TREE_N - MIDDLE_TREE_N);
		constant    LEFT_TREE_LOW_INDEX         : natural                       := 0;
		constant    LEFT_TREE_HIGH_INDEX        : natural                       := (LEFT_TREE_LOW_INDEX + LEFT_TREE_N - 1);
		constant    MIDDLE_TREE_LOW_INDEX       : natural                       := (LEFT_TREE_HIGH_INDEX + 1);
		constant    MIDDLE_TREE_HIGH_INDEX      : natural                       := (MIDDLE_TREE_LOW_INDEX + MIDDLE_TREE_N - 1);
		constant    RIGHT_TREE_LOW_INDEX        : natural                       := (MIDDLE_TREE_HIGH_INDEX + 1);
		constant    RIGHT_TREE_HIGH_INDEX       : natural                       := (RIGHT_TREE_LOW_INDEX + RIGHT_TREE_N - 1);
    begin
		if (N = 1) then
			return term_vector(0);
		elsif (N = 2) then
			report integer'image(SUM_WIDTH);
			report integer'image(to_integer(term_vector(0)));
			report integer'image(to_integer(term_vector(1)));
			return term_vector(0) + term_vector(1);
		else
			return	 ternary_adder_tree(term_vector(LEFT_TREE_LOW_INDEX   to LEFT_TREE_HIGH_INDEX  ))
					+ternary_adder_tree(term_vector(MIDDLE_TREE_LOW_INDEX to MIDDLE_TREE_HIGH_INDEX))
					+ternary_adder_tree(term_vector(RIGHT_TREE_LOW_INDEX  to RIGHT_TREE_HIGH_INDEX ));
		end if;
	end function ternary_adder_tree;
	
	signal start_addition : std_logic := '0';

begin
	kernels : for I in 0 to N-1 generate
		krnl : entity Kernel3x3 generic map(
			BIT_WIDTH_IN,
			KERNEL_WIDTH_OUT,
			DEFAULT_KERNELS(I)
		) port map(
			Clk_i, 
			n_Res_i, 
			Valid_i, 
			X_i((I+1)*BIT_WIDTH_IN*KERNEL_SIZE - 1 downto I*BIT_WIDTH_IN*3*3), 
			K_out((I+1)*KERNEL_WIDTH_OUT - 1 downto I*KERNEL_WIDTH_OUT)
		); 
		term_vector(I) <= resize(K_out((I+1)*KERNEL_WIDTH_OUT - 1 downto I*KERNEL_WIDTH_OUT), SUM_WIDTH);
	end generate;
	
	adder : process(Clk_i, n_Res_i)
	begin
		if n_Res_i = '0' then
			Y_o <= (others => '0');
			start_addition <= '0';
		elsif rising_edge(Clk_i) then
			if start_addition = '1' then
				start_addition <= '0';
				Y_o <= ternary_adder_tree(term_vector)(SUM_WIDTH-1 downto SUM_WIDTH-BIT_WIDTH_OUT);
			end if;
			if Valid_i = '1' then
				start_addition <= '1';
			end if;
		end if;
	end process;
end beh;
