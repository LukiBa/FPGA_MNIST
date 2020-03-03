/*
 * main.c
 *
 *  Created on: 3 Mar 2020
 *      Author: lukas
 */
#include "eggnet.h"
#include <stdio.h>
#include <unistd.h>
#include "dbg.h"
#include <pthread.h>

int main()
{
	network_t network;
	const char* ip_name = "NeuralNetwork";
	pthread_t tx_thread, rx_thread;

	pixel_t image[28*28];
	pixel_t*** rec_img = 0;

	srand(0);

	for (int i = 0; i < 28*28; i++) {
		image[i] = (rand() %  (255 + 1));
	}
	network.img_ptr = image;


	debug("**** Start main ****\n");
	debug("Initialize network...");

	CHECK(egg_init_network(ip_name, &network) == EGG_ERROR_NONE,"Error initializing Network");
	CHECK(print_network(&network) == EGG_ERROR_NONE,"Error printing Network");


	pthread_create(&tx_thread,NULL,egg_tx_img_thread,(void*) &network);
	pthread_create(&rx_thread,NULL,egg_rx_img_thread,(void*) &network);
	CHECK(read_layer(rec_img, &network, (uint8_t) 1),"Error reading layer using debugging interface");

	CHECK(egg_close_network(&network),"Error closing Network");
	return 0;

	error:
		egg_close_network(&network);
		return -1;

}
