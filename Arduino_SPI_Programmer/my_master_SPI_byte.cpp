//*************************************************************
// my_master_SPI_byte.cpp
//*************************************************************
// Codigo para maestro SPI con la siguiente configuracion:
//  - La unidad de transferencias SPI es de 8 bits (un byte).
//  - La frecuencia de la senal SCK es de 191 Hz
//  - Las señales SCK y CS son activas en bajo (cero voltios).
//  - El primer flanco útil de la señal SCK, sea ascendente o descendente, 
//    es el segundo flanco a partir de que baja la señal CS.
//*************************************************************
// Universidad Autonoma Metropolitana
// Programador: Gerardo Laguna
// Fecha: 19 octubre 2026
//************************************************************
// A partir del código de Nick Gammon "bitBangedSPI",
// referido en la página web:
// https://www.gammon.com.au/forum/threads/10892.html?id=10892
// y disponible en el repositorio GitHub:
// https://github.com/nickgammon/bitBangedSPI
//************************************************************
#include "my_master_SPI_byte.h"

//Globales
const uint8_t cs =  8; 
const uint8_t mosi= 7; 
const uint8_t miso= 6; 
const uint8_t sck= 5;


void init_spi(void)
{
    pinMode (cs, OUTPUT);
    pinMode (mosi, OUTPUT);
    pinMode (miso, INPUT);
    pinMode (sck, OUTPUT);

    digitalWrite(cs, HIGH);
    digitalWrite(sck, HIGH);
    digitalWrite(mosi, HIGH);
}

void cs_enable(void)
{
    // enable Slave Select
    digitalWrite(cs, LOW); 
}

void cs_disable(void)
{
    // disable Slave Select
    digitalWrite(cs, HIGH); 
}

void ini_spi_transfer(void)
{
    // enable Slave Select
    digitalWrite(cs, LOW); 
}

void end_spi_transfer(void)
{
    // clock low
    digitalWrite (sck, LOW);
    //stop bit
    digitalWrite (mosi, LOW); 
    // delay between the last fall and last rise of clock
    delayMicroseconds (SCK_HALF_PERIOD);
    // disable Slave Select
    digitalWrite(cs, HIGH); 
    // SCK to high
    digitalWrite(sck, HIGH); 
}

// SPI Byte transfer
uint8_t spi_byte_transfer (uint8_t c)
{       
  // loop for each bit of a byte 
  for (byte bit = 0; bit < 8; bit++) 
  {
    // clock low
    digitalWrite (sck, LOW);

    // set up MOSI on falling edge of SCK (sampled by slave on rising edge)
    if (c & 0x80)
          digitalWrite (mosi, HIGH);
    else
          digitalWrite (mosi, LOW);

    // finished with MS bit, get read to receive next bit      
    c <<= 1;
    // delay between fall and rise of clock
    delayMicroseconds (SCK_HALF_PERIOD);
 
    // clock high
    digitalWrite (sck, HIGH);
 
    // delay between rise and fall of clock
    delayMicroseconds (SCK_HALF_PERIOD);

    // read MISO
    c |= digitalRead (miso) != 0;
 

  }  // end of for loop, for each bit
   
    return c;
}  // end of transfer  

