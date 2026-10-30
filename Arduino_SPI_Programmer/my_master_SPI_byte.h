//*************************************************************
// my_master_SPI_byte.h
//*************************************************************
// Cabecera para my_master_SPI_byte.cpp
//*************************************************************
// Universidad Autonoma Metropolitana
// Programador: Gerardo Laguna
// Fecha: 13 octubre 2026
//************************************************************

#ifndef __MY_MASTER_SPI_BYTE_H
#define __MY_MASTER_SPI_BYTE_H

#include <Arduino.h>

#define SCK_HALF_PERIOD 2617 //Microseconds (F_sck = 191 Hz)

void init_spi(void);
void cs_enable(void);
void cs_disable(void);
void ini_spi_transfer(void);
void end_spi_transfer(void);
uint8_t spi_byte_transfer (uint8_t c);


#endif  /* __MY_MASTER_SPI_BYTE_H */