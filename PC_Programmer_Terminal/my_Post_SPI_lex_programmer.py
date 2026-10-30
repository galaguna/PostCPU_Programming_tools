##########################################################################################
# my_Post_SPI_lex_programmer.py
##########################################################################################
# Analizador léxico para programar microprocesador MPM (Máquina de Post Mejorada) con el
# código máquina y datos contenidos en archivos de texto (típicamente en formato hexadecimal)
##########################################################################################
# Universidad Autónoma Metropolitana, Unidad Lerma
# Programador: Gerardo Laguna
# 28 octubre de 2026
##########################################################################################
import sys
import ply.lex as lex
import comPC_term_4Arduino_wMaster_SPI_4Post as terminal

#Diccionario de palabras reservadas
palabras_reservadas = {
    'org': 'PRIMITIVA_ORG',
    'size': 'PRIMITIVA_SIZE'
}

#Lista de tokens:
tokens=('TERMINADOR',
        'DECIMAL',
        'HEXADECIMAL')+ tuple(palabras_reservadas.values())


##########################################################################################
#PLY (Python Lex-Yacc) evalua las reglas definidas como funciones en su orden de aparición
##########################################################################################

def t_TERMINADOR(t):
    r'[;\n\r]'  #El token 'TERMINADOR' puede ser ';', 'LF' o 'CR'

    if t.value in '\n\r': #Si el caracter es 'LF' o 'CR'
        t.lexer.lineno += 1 #Incrementa el contador de líneas del lexer.

    return t

#Primero se define el token hexadecimal para capturar antes que nadie el prefijo '0x'
def t_HEXADECIMAL(t):
    #Regla con expresión regular para token hexadecimal
    #r'0[xX][0-9a-fA-F]+'
    #   - Inicia con 0
    #   - Le sigue x (minúscula o mayúscula)
    #   - Finalmente una cadena compuesta por números y
    #     letras en el intervalo [A:F] (minúscula o mayúscula)
    r'0[xX][0-9a-fA-F]+'
    t.value= int(t.value,16)
    return t

#Luego se define el token decimal que también puede comenzar con '0'
def t_DECIMAL(t):
    #Regla con expresión regular para token decimal
    r'\d+'
    t.value= int(t.value)
    return t

#Caracteres que se ignoran:
#espacio, tabulador, coma, punto, dos puntos y paréntesis.
t_ignore = ' \t,.:()'

# Definición de regla para palabras e identificadores
def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    # Convertimos a minúsculas para comparar con las claves del diccionario 'org' y 'size'
    valor_minusculas = t.value.lower()
    if valor_minusculas in palabras_reservadas:
        t.type = palabras_reservadas[valor_minusculas]
    return t

def t_error(t):
    print(f'Caracter ilegal:{t.value[0]} en linea {t.lineno}, columna {t.lexpos+1}')
    sys.exit()


#Construye el lexer
lexer = lex.lex()

##########################################################################################
#Variables globales:
##########################################################################################
Lista_codigo_maquina = []
block_org=0
block_size=0
data_ix=0
ES_RAM=0 #Si el valor es cero se trabaja con la ROM, en otro caso, se trabaja con la RAM

##########################################################################################
#Análisis léxico-sintáctico
##########################################################################################

def next_token():
    ntok = lexer.token()
    #Depuración:
    #print(ntok)  # Imprime tipo (type), valor (value) del token, línea y columna.
    return ntok

def syntax_ana_4ORIGEN():
    global block_org, block_size, data_ix
    tok = next_token()
    if tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
        block_org = tok.value
        tok = next_token()
        if tok.type == 'PRIMITIVA_SIZE':
            tok = next_token()
            if tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
                block_size = tok.value
                Lista_codigo_maquina.clear()
                data_ix = 0
            else:
                print(f'¡¡¡Error de sintaxis en línea {tok.lineno}, columna {tok.lexpos+1}: Primitiva SIZE sin argumento válido!!!\n')
                sys.exit()

        else:
            print(f'¡¡¡Error de sintaxis en línea {tok.lineno}, columna {tok.lexpos+1}: Falta primitiva SIZE!!!\n')
            sys.exit()

    else:
        print(f'¡¡¡Error de sintaxis en línea {tok.lineno}, columna {tok.lexpos+1}: Primitiva ORG sin argumento válido!!!\n')
        sys.exit()

def syntax_ana_data(tok):
    global data_ix
    if tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
        data = tok.value
        Lista_codigo_maquina.append(data)
        data_ix+=1
        if data_ix == block_size:
            if ES_RAM:
                print(f'Los siguientes códigos: [{Lista_codigo_maquina}] son {block_size} y se van a escribir en RAM a partir de la dirección {block_org}')
            else:
                print(f'Los siguientes códigos: [{Lista_codigo_maquina}] son {block_size} y se van a escribir en ROM a partir de la dirección {block_org}')

            terminal.comPC_serial_2Arduino_4PostSPI_Write(ES_RAM, Lista_codigo_maquina, block_org)

    else:
        print(f'¡¡¡Error de sintaxis en línea {tok.lineno}, columna {tok.lexpos+1}: Se espera valor numérico!!!\n')
        sys.exit()


def analiza_linea_hex():
    tok = next_token()
    if not(not tok or tok.type == 'TERMINADOR'):
        if tok.type == 'PRIMITIVA_ORG':
            syntax_ana_4ORIGEN()
        else:
            syntax_ana_data(tok)



#Uso de token() en forma manual, para analizar y programar, línea por línea, un código máquina en formato de texto:
def spi_write_to_Post(es_ram,hex_file):
#es_ram: #Si el valor es cero se programa la ROM, en otro caso, se escribe en la RAM
#hex_file: archivo con el código máquina en formato de texto (típicamente codificado en hexadecimal)
    global ES_RAM

    ES_RAM = es_ram
    try:
        with open(hex_file, 'r') as machine_code:
            lexer.lineno =1 #Inicializamos contador de lineas del lexer
            #Iteramos línea por línea:
            for n_linea, linea in enumerate(machine_code, start=1):
                lexer.lineno = n_linea #El número de línea en turno
                lexer.input (linea)
                #Depuración:
                #print(f'Linea {n_linea}')
                #print(linea)
                analiza_linea_hex()

    except FileNotFoundError:
        print(f'El archivo {hex_file} no existe \n')


def spi_read_from_Post(es_ram,n,add):
#es_ram: #Si el valor es cero se lee la ROM, en otro caso, se lee la RAM
#n: número de localidades a leer
#add: dirección inicial de las lecturas

    RxData=terminal.comPC_serial_2Arduino_4PostSPI_Read(es_ram, n, add)
    for i in range(len(RxData)):
        if es_ram: #Si se lee la RAM
            print(f"Rx_Data[{i}]=0x{RxData[i]:0{1}x}") #Despliega entero con formato hexacedimal de 1 dígito
        else:# Otro caso, se lee la ROM
            print(f"Rx_Data[{i}]=0x{RxData[i]:0{2}x}") #Despliega entero con formato hexacedimal de 2 dígitos

if __name__ == "__main__":

    ROM=0
    RAM=1

    spi_write_to_Post(ROM,'Post_code.hex')
    spi_read_from_Post(ROM, 9, 0x00)

    spi_write_to_Post(RAM,'Post_data.hex')
    spi_read_from_Post(RAM, 4, 0x00)

