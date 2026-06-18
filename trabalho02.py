# Integrantes:
# Gustavo Valério dos Santos RA 139067
# João Gabriel de Campos Nassar RA 

import sys
import struct
import os
import io


#Constantes
ORDEM = 5

CHAVE_NULA = -1
FILHO_NULO = -1
OFFSET_NULO = -1

HEADER_SIZE = 4
HEADER_FORMAT = "i"
GAMES_FILE = "games.dat"


class Pagina:
    '''Inicializa a estrutura de uma página vazia na árvore B'''

    def __init__(self)-> None:
        self.numChaves: int = 0
        self.chaves: list = [None] * (ORDEM - 1)
        self.filhos: list = [None] * ORDEM



    def converte_pag(self)-> bytes:
        '''Converte  a página para uma sequência de bytes que pode ser gravada em disco'''

        campos = [self.numChaves]
        for i in self.chaves:
            if i is None:
                campos += [CHAVE_NULA, OFFSET_NULO]
            else:
                campos += [i[0], i[1]]
        
        for filho in self.filhos:
            if filho is None:
                campos.append(FILHO_NULO)
            else:
                campos.append(filho)
        return struct.pack(HEADER_FORMAT, *campos)
    


def reverte_pag(dados: bytes)-> 'Pagina':
    '''Reconstrói uma página a partir de bytes lidos do disco'''


def tamanho_pagina()-> int:
    '''Calcula o tamanho em bytes de uma página'''

    return (1 + 2 * (ORDEM -1)   + ORDEM) * 4


def reconstroi_pagina(dados: bytes)-> Pagina:
    '''Reconstrói uma página a partir de bytes lidos do disco'''
    
    


def ler_raiz(arq: io.TextIOWrapper)-> int:
    '''Lê o RRN da raiz armazenado no cabeçalho do arquivo'''

    arq.seek(os.SEEK_SET)
    return struct.unpack(HEADER_FORMAT, arq.read(4))[0]


def escrever_raiz(arq: io.TextIOWrapper, rrn: int)-> None:
    '''Grava o RRN da raiz no cabeçalho do arquivo'''

    arq.seek(os.SEEK_SET)
    arq.write(struct.pack(HEADER_FORMAT, rrn))


def ler_registro(arq_games: io.TextIOWrapper, offset: int)-> str:
    '''Lê e retorna o registro localizado em **ofsset** dentro de games.dat'''

    arq_games.seek(offset)
    saida = arq_games.readline().decode().strip()
    return saida


def parse_id(linha: str)-> int:
    '''Extrai a chave primária de uma **linha** do arquivo games.dat'''

    return int(linha.split("|")[0])




def ler_pag(arq: io.TextIOWrapper, rrn: int)-> Pagina:
    '''Lê uma página do arquivo da árvore B'''

    byte_offset = HEADER_SIZE + rrn * Pagina.tamanho()
    arq.seek(byte_offset)






def buscaNaPagina(chave: int, pag: Pagina)-> tuple[bool, int]:
    '''Busca sequencial dentro de uma única página'''

    pos = 0
    while pos < pag.numChaves and chave > pag.chaves[pos]:
        pos += 1
    if pos < pag.numChaves and chave == pag.chaves[pos]:
        return True, pos
    else:
        return False, pos
    

def buscaNaArvore(chave: int, rrn)-> tuple:
    '''Busca recursiva na árvore a partir de um RRN'''
    if rrn == None:
        return False, None, None
    else:
        pag = ler_pag(, rrn)
        achou, pos = buscaNaPagina(chave, pag)

        if achou:
            return True, rrn, pos
        else:
            return buscaNaArvore(chave, pag.filhos[pos])


def main()-> None:
    args = sys.argv[1:]

    if not args:
        print("Uso: python programa.py -b | -e <arquivo_ops> | -p")
    
    flag = args[0]

    if flag == "-b":
        pass
    elif flag == "-e":
        if len(args) < 2:
            print("Erro, informe o nome do arquivo de operações")
            pass
    elif flag == "-p":
        pass
    else:
        print(f"Flag desconhecida: {flag}")
        print("Uso: python programa.py -b | -e <arquivo_ops> | -p")


if __name__ == "__main__":
    main()