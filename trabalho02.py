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
PAG_FORMAT = f"{1 + 2 * (ORDEM - 1) + ORDEM}i"
GAMES_FILE = "games.dat"
BTREE_FILE = "btree.dat"


#Estrutura de Página

class Pagina:
    '''Inicializa a estrutura de uma página vazia na árvore B'''

    def __init__(self)-> None:
        self.numChaves: int = 0
        self.chaves: list = [None] * (ORDEM - 1)
        self.filhos: list = [None] * ORDEM
    
    @staticmethod
    def tamanho_pagina()-> int:
        '''Calcula o tamanho em bytes de uma página
        Cálculo: (1 + 2*(ORDEM-1) + ORDEM) campos x 4 bytes cada'''

        return (1 + 2 * (ORDEM -1)   + ORDEM) * 4


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
        return struct.pack(PAG_FORMAT, *campos)
    


def reverte_pag(dados: bytes)-> 'Pagina':
    '''Reconstrói uma página a partir de bytes lidos do disco'''

    valores = struct.unpack(PAG_FORMAT, dados)
    p = Pagina()
    p.numChaves = valores[0]

    for i in range(ORDEM - 1):
        chave = valores[1 + i * 2]
        offset = valores[2 + i * 2]
        if chave == CHAVE_NULA:
            p.chaves[i] = None
        else:
            p.chaves[i] = (chave, offset)
    
    inicio_filhos = 1 + 2 * (ORDEM - 1)
    for i in range(ORDEM):
        v = valores[inicio_filhos + i]
        if v == FILHO_NULO:
            p.filhos[i] = None
        else:
            p.filhos[i] = v

    return p



def aloca_pag(arq: io.TextIOWrapper, pag: Pagina)-> int:
    '''Grava uma nova página no final do arquivo btree.dat e retorna o rrn alocado'''
    
    arq.seek(0, os.SEEK_END)
    rrn = (arq.tell() - HEADER_SIZE) // Pagina.tamanho_pagina()
    arq.write(pag.converte_pag())

    return rrn


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




# Buscas

def buscaNaPagina(chave: int, pag: Pagina)-> tuple[bool, int]:
    '''Busca sequencial dentro de uma única página'''

    pos = 0
    while pos < pag.numChaves and chave > pag.chaves[pos][0]:
        pos += 1
    if pos < pag.numChaves and chave == pag.chaves[pos][0]:
        return True, pos
    else:
        return False, pos
    

def buscaNaArvore(arq: io.TextIOWrapper, chave: int, rrn)-> tuple:
    '''Busca recursiva na árvore a partir de um RRN'''
    if rrn is None:
        # Parada da recursão
        return False, None, None
    else:
        pag = ler_pag(arq, rrn)
        achou, pos = buscaNaPagina(chave, pag)

        if achou:
            return True, rrn, pos
        else:
            # Busca na página filha
            return buscaNaArvore(arq, chave, pag.filhos[pos])


def buscar(arq: io.TextIOWrapper, rrn_raiz: int, chave: int)-> tuple:
    '''Ponto de entrada da busca na árvore B'''
    achou, rrn, pos = buscaNaArvore(arq, chave, rrn_raiz)

    if not achou:
        return None
    
    pag = ler_pag(arq, rrn)
    offset = pag.chaves[pos][1]
    return rrn, pos, offset


# Auxiliares da inserção na árvore

def ler_pag(arq: io.TextIOWrapper, rrn: int)-> Pagina:
    '''Lê uma página do arquivo da árvore B'''

    byte_offset = HEADER_SIZE + rrn * Pagina.tamanho_pagina()
    arq.seek(byte_offset)
    return reverte_pag(arq.read(Pagina.tamanho_pagina()))



def escrever_pag(arq: io.TextIOWrapper, rrn: int, pag: Pagina)-> None:
    '''Grava uma página no arquivo btree.dat'''
    byte_offset = HEADER_SIZE + rrn * Pagina.tamanho_pagina()
    arq.seek(byte_offset)
    arq.write(pag.converte_pag())


def insereNaPagina(chave: int, filhoD, pag: Pagina)-> None:
    '''Insere uma chave e seu filho direito em uma página em memória,
    deslocando as entradas maiores para abrir posição e mantendo ordem crescente
    '''
    # aumenta temporariamente a capacidade da página se ela estiver cheia
    if  pag.numChaves == len(pag.chaves):
        pag.chaves.append(None)
        pag.filhos.append(None)

    i = pag.numChaves

    while i > 0 and chave < pag.chaves[i - 1]:
        pag.chaves[i] = pag.chaves[i - 1]
        pag.filhos[i + 1] = pag.fihos[i]
        i -= 1
    
    pag.chaves[i] = chave
    pag.filhos[i + 1] = filhoD

    pag.numChaves += 1

# melhorar essa função, lógica está ruim
# acho que da pra fazer duas funções, copia metade da direita e copia metade da esquerda
def divide(arq: io.TextIOWrapper, chave: int, filhoD, pag: Pagina)-> tuple:
    '''Divide uma página cheia em duas após inserir a nova chave nela'''
    insereNaPagina(chave, filhoD, pag)

    meio = ORDEM // 2
    chavePro = pag.chaves[meio]

    # filhoDpro = RRN que pNova terá no arquivo
    arq.seek(0, os.SEEK_END)
    filhoDPro = (arq.tell() - HEADER_SIZE) // Pagina.tamanho_pagina()

    #pAtual = conteudo de pag até o meio
    pAtual = Pagina()
    pAtual.numChaves = meio
    pAtual.chaves = pag.chaves[:meio] + [None] * (ORDEM - 1 - meio)
    pAtual.filhos = pag.filhos[:meio + 1] + [None] * (ORDEM - meio - 1)

    # pNove = conteudo de pag a partir de meio + 1
    tam_dir =  ORDEM - 1 - meio
    pNova = Pagina()
    pNova.numChaves = tam_dir
    pNova.chaves = pag.chaves[meio + 1: meio + 1 + tam_dir] + [None] * (ORDEM - 1 - tam_dir)
    pNova.filhos = pag.filhos[meio + 1: meio + 1 + tam_dir] + [None] * (ORDEM - tam_dir - 1)

    return chavePro, filhoDPro, pAtual, pNova


def gerenciadorDeInsercao(arq: io.TextIOWrapper, raiz: int, entradas: list)-> int:
    '''Gerencia a inserção de uma lista de chaves na árvore B'''
    for chave in entradas:
        chavePro, filhoDpro, promocao = insereNaArvore(arq, raiz, chave)

        if promocao:
            pNova            = Pagina()
            pNova.chaves[0]  = chavePro   
            pNova.filhos[0]  = raiz       
            pNova.filhos[1]  = filhoDpro  
            pNova.numChaves += 1
            raiz = aloca_pag(arq, pNova)  
 
    return raiz



# Inserção na árvore

def insereNaArvore(arq: io.TextIOWrapper, rrn: int, chave: tuple)-> tuple:
    '''Inserção recursiva na árvore com promoção de chave'''

    if rrn is None or rrn == FILHO_NULO:
        # Chegou "abaixo" de uma folha, promove a própria chave
        return chave, None, True
    
    pag = ler_pag(arq, rrn)

    i = 0
    while i < pag.numChaves and chave[0] >  pag.chaves[i][0]:
        i += 1

    chavePro, filhoDpro, promocao = insereNaArvore(arq, pag.filhos[i], chave)

    if not promocao:
        return None, None, False
    
    pag = ler_pag(arq, rrn)

    if pag.numChaves < ORDEM - 1:
        # insere diretamente e persiste(cabe na pag)
        insereNaPagina(chavePro, filhoDpro, pag)
        escrever_pag(arq, rrn, pag)
        return None, None, False
    
    else:
        # pag cheia, divide e propaga promoção
        chavePro, filhoDpro, pAtual, pNova = divide(arq, chavePro, filhoDpro, pag, rrn)
        escrever_pag(arq, rrn, pAtual)
        aloca_pag(arq, pNova)
        return chavePro, filhoDpro, True


# Execução do Arquivo de operações

def executar_operacoes(nome_arquivo: str)-> None:
    '''Lê o arquivo de operações e as executa sequencialmente em games.dat e btree.dat'''

    if not os.path.exists('games.dat'):
        print("Erro: arquivo games.dat não encontrado.")
        return 
 
    if not os.path.exists('btree.dat'):
        print("Erro: arquivo btree.dat não encontrado.")
        return 
 
    if not os.path.exists(nome_arquivo):
        print(f"Erro: arquivo de operações '{nome_arquivo}' não encontrado.")
        return 

    
    with open(nome_arquivo, 'r') as arq:
        linhas = []
        for i in arq:
            linha = i.strip()
            if linha:
                linhas.append(linha)

    with open(GAMES_FILE, 'r+b') as gf, open(BTREE_FILE, 'r+b') as bf:
        raiz = ler_raiz(bf)

        for linha in linhas:
            op = linha[0]
            arg = linha[2:].strip()
        
            if op == 'b':
                chave = int(arg)
                print(f"Busca pelo registro de chave {chave}")
                resultado = buscar(bf, raiz, chave)
                if resultado is None:
                    print(f"Erro: chave não encontrada")
                else:
                    _, _, byte_off = resultado
                    registro = ler_registro(gf, byte_off)
                    n_bytes = len(registro.encode()) + 1
                    print(f"{registro} ({n_bytes} bytes - offset {byte_off})")

            elif op == 'i':
                chave = parse_id(arg)
                print(f"Inserção do registro de chave {chave}")
                if buscar(bf, raiz, chave) is not None:
                    print(f"Erro: chave {chave} duplicada")
                    continue
                gf.seek(0, os.SEEK_END)
                byte_off = gf.tell()
                gf.write((arg + '\n').encode())
                raiz = gerenciadorDeInsercao(bf, raiz, [(chave, byte_off)])
                n_bytes = len(arg.encode()) + 1
                print(f"{arg} ({n_bytes} bytes - offset {byte_off})")

        escrever_raiz(bf, raiz)
        
    print(f"\n As operações do arquivo {nome_arquivo} foram executadas com sucesso.")
                







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