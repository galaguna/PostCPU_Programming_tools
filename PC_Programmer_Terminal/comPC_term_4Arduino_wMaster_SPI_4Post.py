#**************************************************************************************************
# Código comPC_term_4Arduino_wMaster_SPI_4Post.py
#**************************************************************************************************
# Transmite bytes a través de un puerto USB, emulando una UART
# (mediante chip CH340 de una tarjeta Arduino), para programar
# un microprocesador MPM (Máquina de Post Mejorada) mediante
# su interfaz SPI (la misma tarjeta Arduino opera como maestro SPI).
# El proyecto que debe estar programado en la tarjeta Arduino
# se denomina my_arduino_master_SPI_4Post.
#**************************************************************************************************
# Universidad Autónoma Metropolitana, Unidad Lerma
# Programador: Gerardo Laguna
# (A partir de códigos de ejemplo proporcionados por la IA del buscador de Google)
# 30 octubre de 2026
#**************************************************************************************************

import time
import serial

# Configura los parámetros del puerto
# Reemplaza 'COMx' por tu puerto (ej. '/dev/ttyUSB0' en Linux)
PUERTO = "COM4"
#PUERTO = "/dev/ttyUSB0"
BAUDIOS = 9600

def binseq_2bytes(secuencia_binaria):
#secuencia_binaria: Secuencia binaria
#Regresa:
#lista_de_bytes: la lista de bytes correspondientes a la secuencia binaria

    #Asegura que la longitud sea múltiplo de 8 (rellenando a la izquierda)
    if len(secuencia_binaria) % 8 != 0:
        faltantes = 8 - (len(secuencia_binaria) % 8)
        secuencia_binaria = secuencia_binaria.zfill(len(secuencia_binaria) + faltantes)

    #Segmenta cada 8 bits y convierte cada bloque a entero
    lista_de_bytes = [int(secuencia_binaria[i:i + 8], 2) for i in range(0, len(secuencia_binaria), 8)]
    return (lista_de_bytes)

def build_spi_bytes_4Post(rw,ram_rom,add,data):
#rw: 0 para Write y no cero para Read
#ram_rom: 0 para ROM y no cero para RAM
#add: Valor de dirección en el intervalo [0x000:0x3FF]
#data: Valor del dato en el intervalo [0x0:0xF]
#Regresa:
#spi_bytes: la lista de bytes que conforman la palabra SPI

    datab = format(data, 'b').zfill(4)
    addb = format(add, 'b').zfill(10)
    if rw==0:
        RDb= '0'
    else:
        RDb= '1'

    if ram_rom==0:
        RAMb= '0'
    else:
        RAMb= '1'

    spi_word = RDb+ RAMb +addb + datab
    print(f"Palabra SPI: {spi_word}")
    spi_bytes = binseq_2bytes(spi_word)
    print(f"Bytes SPI: {spi_bytes}")
    return(spi_bytes)


def comPC_serial_2Arduino_4PostSPI_Write(RAM_ROM,Data,ORG):
#RAM_ROM: 0 para escritura a RAM y 1 para escritura a ROM de sistema Post
#Data: lista de datos a escribir
#ORG: Dirección de origen (dirección inicial)

    N= len(Data)
    ADD= ORG

    try:
        # Inicializa y abre el puerto serie
        with serial.Serial(
            port=PUERTO,
            baudrate=BAUDIOS,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=3,
            dsrdtr=False,  # Desactiva control de flujo DSR/DTR
            rtscts=False  # Desactiva control de flujo RTS/CTS
        ) as ser:

            print(f"Conectado con éxito al CH340 en el puerto {PUERTO}")
            ser.dtr = False
            time.sleep(3)  # Pausa breve para estabilizar la conexión
            # Forzamos limpieza de posibles residuos en los buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()

            for i in range(N):
                intentos=0
                for j in range(3): #Hasta 3 intentos
                    print(f"***Intento {intentos} de escritura SPI ({i+1} de {N}) ***")
                    #**************************************************************
                    #*** Comunicación correspondiente a mando SPI de escritura  ***
                    #**************************************************************
                    # Prepara los datos a enviar (deben ser objetos tipo 'bytes')
                    tx_bytes= build_spi_bytes_4Post(0,RAM_ROM,ADD,Data[i])
                    tx_line= str(tx_bytes[0])+','+str(tx_bytes[1])+'\n'
                    print(f"Texto a transmitir: {tx_line}")
                    ascii_tx_line = tx_line.encode("utf-8")

                    # Salvamos el dato de la escritura SPI (Nota: el byte[1] contiene el campo de datos SPI):
                    if RAM_ROM == 0:  # Si fue una escritura a ROM, el campo de datos efectivo es de 3 bits
                        tx_datab = format(tx_bytes[1] & 0xFF, 'b').zfill(8) #se formatea entero como binario de 8 bits
                        tx_datab = tx_datab[5:8] #los 3 LSB del byte
                    else:  # Si fue una escritura a RAM, el campo de datos efectivo es de 1 bit
                        tx_datab = format(tx_bytes[1] & 0xFF, 'b').zfill(8) #se formatea entero como binario de 8 bits
                        tx_datab = tx_datab[7:8] #el LSB del byte

                    # Transmite los datos
                    ser.write(ascii_tx_line)
                    # Asegura que todos los bytes salgan del buffer de salida de Python
                    ser.flush()

                    # Recibe de datos de respuesta
                    print("Esperando respuesta...")
                    ascii_rx_line = ser.readline()

                    if ascii_rx_line:
                        rx_line = ascii_rx_line.decode('utf-8', errors='ignore')
#                        rx_bytes = [int(x.strip()) for x in rx_line.strip().split(",")]
#                        print(f"Byte0 recibido: {rx_bytes[0] & 0xFF}")
#                        print(f"Byte1 recibido: {rx_bytes[1] & 0xFF}")
                    else:
                        print("No se recibieron datos (Tiempo de espera agotado).")

                    #**************************************************************
                    #*** Comunicación correspondiente a mando SPI de lectura  ***
                    #**************************************************************
                    # Prepara los datos a enviar (deben ser objetos tipo 'bytes')
                    tx_bytes= build_spi_bytes_4Post(1,RAM_ROM,ADD,0x0)
                    tx_line= str(tx_bytes[0])+','+str(tx_bytes[1])+'\n'
                    print(f"Texto a transmitir: {tx_line}")
                    ascii_tx_line = tx_line.encode("utf-8")

                    # Transmite los datos
                    ser.write(ascii_tx_line)
                    # Asegura que todos los bytes salgan del buffer de salida de Python
                    ser.flush()

                    # Recibe de datos de respuesta
                    print("Esperando respuesta...")
                    ascii_rx_line = ser.readline()

                    if ascii_rx_line:
                        rx_line = ascii_rx_line.decode('utf-8', errors='ignore')
#                        rx_bytes = [int(x.strip()) for x in rx_line.strip().split(",")]
#                        print(f"Byte0 recibido: {rx_bytes[0] & 0xFF}")
#                        print(f"Byte1 recibido: {rx_bytes[1] & 0xFF}")
                    else:
                        print("No se recibieron datos (Tiempo de espera agotado).")

                    #**************************************************************
                    #*** Comunicación correspondiente a datos SPI de relleno  ***
                    #*** para la recuperación del dato leído y validación de  ***
                    #*** la escritura SPI.                                    ***
                    #**************************************************************
                    # Prepara los datos a enviar (deben ser objetos tipo 'bytes')
                    tx_bytes= build_spi_bytes_4Post(0,0,0x0,0x0)
                    tx_line= str(tx_bytes[0])+','+str(tx_bytes[1])+'\n'
                    print(f"Texto a transmitir: {tx_line}")
                    ascii_tx_line = tx_line.encode("utf-8")

                    # Transmite los datos
                    ser.write(ascii_tx_line)
                    # Asegura que todos los bytes salgan del buffer de salida de Python
                    ser.flush()

                    # Recibe de datos de respuesta
                    print("Esperando respuesta...")
                    ascii_rx_line = ser.readline()

                    if ascii_rx_line:
                        rx_line = ascii_rx_line.decode('utf-8', errors='ignore')
                        rx_bytes = [int(x.strip()) for x in rx_line.strip().split(",")]
#                        print(f"Byte0 recibido: {rx_bytes[0] & 0xFF}")
#                        print(f"Byte1 recibido: {rx_bytes[1] & 0xFF}")

                        #Validamos el éxito de la escritura SPI (Nota: el byte[1] contiene el campo de datos SPI):
                        if RAM_ROM==0: #Si fue una escritura a ROM, el campo de datos efectivo es de 3 bits
                            rx_datab = format(rx_bytes[1] & 0xFF, 'b').zfill(8) #se formatea entero como binario de 8 bits
                            rx_datab = rx_datab[5:8] #los 3 LSB del byte
                        else: #Si fue una escritura a RAM, el campo de datos efectivo es de 1 bit
                            rx_datab = format(rx_bytes[1] & 0xFF, 'b').zfill(8) #se formatea entero como binario de 8 bits
                            rx_datab = rx_datab[7:8] #el LSB del byte

                        #print(f"Se va a comparar tx_datab={tx_datab} vs. rx_datab={rx_datab}...")
                        if tx_datab==rx_datab:
                            break #Si la escritura es exitosa, interrumpe los intentos
                        else:
                            print(f"Intento {intentos} de escritura SPI fallido...")
                            intentos += 1
                    else:
                        print("No se recibieron datos (Tiempo de espera agotado).")

                if intentos==3:
                    print("¡¡¡Error: El dispositivo SPI esclavo no está funcionando correctamente!!!")
                    break #Interrumpe proceso

                ADD += 1  # Siguiente direccion

    except serial.SerialException as e:
        print(f"Error al abrir o comunicar con el puerto serie: {e}")
    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario.")

def comPC_serial_2Arduino_4PostSPI_Read(RAM_ROM,N,ORG):
#RAM_ROM: 0 para escritura a RAM y 1 para escritura a ROM de sistema Post
#N: Número de localidades a leer
#ORG: Dirección de origen (dirección inicial)
#Regresa
#Data: lista de datos leidos (almacenados como enteros)

    ADD= ORG
    Data=[]

    try:
        # Inicializa y abre el puerto serie
        with serial.Serial(
            port=PUERTO,
            baudrate=BAUDIOS,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=3,
            dsrdtr=False,  # Desactiva control de flujo DSR/DTR
            rtscts=False  # Desactiva control de flujo RTS/CTS
        ) as ser:

            print(f"Conectado con éxito al CH340 en el puerto {PUERTO}")
            ser.dtr = False
            time.sleep(3)  # Pausa breve para estabilizar la conexión
            # Forzamos limpieza de posibles residuos en los buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()

            for i in range(N):
                print(f"***Escritura SPI ({i+1} de {N}) ***")
                #**************************************************************
                #*** Comunicación correspondiente a mando SPI de lectura  ***
                #**************************************************************
                # Prepara los datos a enviar (deben ser objetos tipo 'bytes')
                tx_bytes= build_spi_bytes_4Post(1,RAM_ROM,ADD,0x0)
                tx_line= str(tx_bytes[0])+','+str(tx_bytes[1])+'\n'
                print(f"Texto a transmitir: {tx_line}")
                ascii_tx_line = tx_line.encode("utf-8")

                # Transmite los datos
                ser.write(ascii_tx_line)
                # Asegura que todos los bytes salgan del buffer de salida de Python
                ser.flush()

                # Recepcion de datos de respuesta
                print("Esperando respuesta...")
                ascii_rx_line = ser.readline()

                if ascii_rx_line:
                    rx_line = ascii_rx_line.decode('utf-8', errors='ignore')
#                    rx_bytes = [int(x.strip()) for x in rx_line.strip().split(",")]
#                    print(f"Byte0 recibido: {rx_bytes[0] & 0xFF}")
#                    print(f"Byte1 recibido: {rx_bytes[1] & 0xFF}")
                else:
                    print("No se recibieron datos (Tiempo de espera agotado).")

                #**************************************************************
                #*** Comunicación correspondiente a datos SPI de relleno  ***
                #*** para la recuperación del dato leído.                 ***
                #**************************************************************
                # Prepara los datos a enviar (deben ser objetos tipo 'bytes')
                tx_bytes= build_spi_bytes_4Post(0,0,0x0,0x0)
                tx_line= str(tx_bytes[0])+','+str(tx_bytes[1])+'\n'
                print(f"Texto a transmitir: {tx_line}")
                ascii_tx_line = tx_line.encode("utf-8")

                # Transmite los datos
                ser.write(ascii_tx_line)
                # Asegura que todos los bytes salgan del búfer de salida de Python
                ser.flush()

                # Recibe de datos de respuesta
                print("Esperando respuesta...")
                ascii_rx_line = ser.readline()

                if ascii_rx_line:
                    rx_line = ascii_rx_line.decode('utf-8', errors='ignore')
                    rx_bytes = [int(x.strip()) for x in rx_line.strip().split(",")]
#                    print(f"Byte0 recibido: {rx_bytes[0] & 0xFF}")
#                    print(f"Byte1 recibido: {rx_bytes[1] & 0xFF}")

                    #Recuperamos el dato leido (Nota: el byte[1] contiene el campo de datos SPI):
                    if RAM_ROM==0: #Si fue una escritura a ROM, el campo de datos efectivo es de 3 bits
                        rx_datab = format(rx_bytes[1] & 0xFF, 'b').zfill(8) #se formatea entero como binario de 8 bits
                        rx_datab = rx_datab[5:8] #los 3 LSB del byte
                    else: #Si fue una escritura a RAM, el campo de datos efectivo es de 1 bit
                        rx_datab = format(rx_bytes[1] & 0xFF, 'b').zfill(8) #se formatea entero como binario de 8 bits
                        rx_datab = rx_datab[7:8] #el LSB del byte

                    #print(f"Se va a almacenar rx_datab={rx_datab}...")
                    Data.append(int(rx_datab,2)) #Se alamacenan las secuencias binarias como enteros
                else:
                    print("No se recibieron datos (Tiempo de espera agotado).")

                ADD+=1 #Siguiente direccion

    except serial.SerialException as e:
        print(f"Error al abrir o comunicar con el puerto serie: {e}")
    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario.")

    return(Data)


#if __name__ == "__main__":

#    TxData=[0x1, 0x7]
#    comPC_serial_2Arduino_4PostSPI_Write(0,TxData,0x000)
#    RxData=comPC_serial_2Arduino_4PostSPI_Read(0, 2, 0x000)
#    for i in range(len(RxData)):
#        print(f"Rx_Data[{i}]={RxData[i]:0{2}x}") #Despliega entero con formato hexacedimal de 2 dígitos