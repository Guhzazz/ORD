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


class Pagina:
    '''Inicializa a estrutura de uma página vazia na árvore B'''

    def __init__(self)-> None:
        self.numChaves: int = 0
        self.chaves: list = [None] * (ORDEM - 1)
        self.filhos: list = [None] * ORDEM


def tamanho_pagina()-> int:
    '''Calcula o tamanho em bytes de uma página'''

    return (1 + 2 * (ORDEM -1)   + ORDEM) * 4


def converte_pag(self)-> bytes:
    '''Converte  a página para uma sequência de bytes que pode ser gravada em disco'''

    campos = [self.numChaves]
    for i in self.chaves:
        if i is None:
            campos += [CHAVE_NULA, OFFSET_NULO]
        else:
            campos += [i[0], i[1]]
            

def ler_raiz(arq: io.TextIOWrapper)-> int:
    '''Lê o RRN da raiz armazenado no cabeçalho do arquivo'''

    arq.seek(os.SEEK_SET)
    return struct.unpack(HEADER_FORMAT, arq.read(4))[0]


def escrever_raiz(arq: io.TextIOWrapper, rrn: int)-> None:
    '''Grava o RRN da raiz no cabeçalho do arquivo'''

    arq.seek(os.SEEK_SET)
    arq.write(struct.pack(HEADER_FORMAT, rrn))





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
    pass


if __name__ == "__main__":
    main()