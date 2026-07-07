# Integrantes:
# Gustavo Valério dos Santos RA 139067
# João Gabriel de Campos Nassar RA

import io
import os
import struct
import sys

# Constantes
ORDEM = 5

CHAVE_NULA = -1
FILHO_NULO = -1
OFFSET_NULO = -1

HEADER_SIZE = 4
HEADER_FORMAT = "i"
PAG_FORMAT = f"{1 + 2 * (ORDEM - 1) + ORDEM}i"
GAMES_FILE = "games.dat"
BTREE_FILE = "btree.dat"


# Estrutura de Página


class Pagina:
    """Inicializa a estrutura de uma página vazia na árvore B"""

    def __init__(self) -> None:
        self.numChaves: int = 0
        self.chaves: list = [None] * (ORDEM - 1)
        self.filhos: list = [None] * ORDEM

    @staticmethod
    def tamanho_pagina() -> int:
        """Calcula o tamanho em bytes de uma página
        Cálculo: (1 + 2*(ORDEM-1) + ORDEM) campos x 4 bytes cada"""

        return (1 + 2 * (ORDEM - 1) + ORDEM) * 4

    def converte_pag(self) -> bytes:
        """Converte  a página para uma sequência de bytes que pode ser gravada em disco"""

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


def reverte_pag(dados: bytes) -> "Pagina":
    """Reconstrói uma página a partir de bytes lidos do disco"""

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


def aloca_pag(arq: io.BufferedRandom, pag: Pagina) -> int:
    """Grava uma nova página no final do arquivo btree.dat e retorna o rrn alocado"""

    arq.seek(0, os.SEEK_END)
    rrn = (arq.tell() - HEADER_SIZE) // Pagina.tamanho_pagina()
    arq.write(pag.converte_pag())

    return rrn


def ler_raiz(arq: io.BufferedRandom) -> int:
    """Lê o RRN da raiz armazenado no cabeçalho do arquivo"""

    arq.seek(os.SEEK_SET)
    return struct.unpack(HEADER_FORMAT, arq.read(4))[0]


def escrever_raiz(arq: io.BufferedRandom, rrn: int) -> None:
    """Grava o RRN da raiz no cabeçalho do arquivo"""

    arq.seek(os.SEEK_SET)
    arq.write(struct.pack(HEADER_FORMAT, rrn))


def ler_registro(arq_games: io.BufferedRandom, offset: int) -> str:
    """Lê e retorna o registro localizado em **ofsset** dentro de games.dat"""
    arq_games.seek(offset)

    tamanho_bytes = arq_games.read(2)
    if not tamanho_bytes or len(tamanho_bytes) < 2:
        return ""

    tamanho = struct.unpack("<H", tamanho_bytes)[0]

    registro_bytes = arq_games.read(tamanho)

    return registro_bytes.decode("utf-8")


def parse_id(linha: str) -> int:
    """Extrai a chave primária de uma **linha** do arquivo games.dat"""

    return int(linha.split("|")[0])


# Buscas


def buscaNaPagina(chave: int, pag: Pagina) -> tuple[bool, int]:
    """Busca sequencial dentro de uma única página"""

    pos = 0
    while pos < pag.numChaves and chave > pag.chaves[pos][0]:
        pos += 1
    if pos < pag.numChaves and chave == pag.chaves[pos][0]:
        return True, pos
    else:
        return False, pos


def buscaNaArvore(arq: io.BufferedRandom, chave: int, rrn) -> tuple:
    """Busca recursiva na árvore a partir de um RRN"""
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


def buscar(arq: io.BufferedRandom, rrn_raiz: int, chave: int) -> tuple:
    """Ponto de entrada da busca na árvore B"""
    achou, rrn, pos = buscaNaArvore(arq, chave, rrn_raiz)

    if not achou:
        return None

    pag = ler_pag(arq, rrn)
    offset = pag.chaves[pos][1]
    return rrn, pos, offset


# Auxiliares da inserção na árvore


def ler_pag(arq: io.BufferedRandom, rrn: int) -> Pagina:
    """Lê uma página do arquivo da árvore B"""

    byte_offset = HEADER_SIZE + rrn * Pagina.tamanho_pagina()
    arq.seek(byte_offset)
    return reverte_pag(arq.read(Pagina.tamanho_pagina()))


def escrever_pag(arq: io.BufferedRandom, rrn: int, pag: Pagina) -> None:
    """Grava uma página no arquivo btree.dat"""
    byte_offset = HEADER_SIZE + rrn * Pagina.tamanho_pagina()
    arq.seek(byte_offset)
    arq.write(pag.converte_pag())


def insereNaPagina(chave: int, filhoD, pag: Pagina) -> None:
    """Insere uma chave e seu filho direito em uma página em memória,
    deslocando as entradas maiores para abrir posição e mantendo ordem crescente
    """
    # aumenta temporariamente a capacidade da página se ela estiver cheia
    if pag.numChaves == len(pag.chaves):
        pag.chaves.append(None)
        pag.filhos.append(None)

    i = pag.numChaves

    while i > 0 and chave[0] < pag.chaves[i - 1][0]:
        pag.chaves[i] = pag.chaves[i - 1]
        pag.filhos[i + 1] = pag.filhos[i]
        i -= 1

    pag.chaves[i] = chave
    pag.filhos[i + 1] = filhoD

    pag.numChaves += 1


def divide(arq: io.BufferedRandom, chave: tuple, filhoD: int, pag: Pagina) -> tuple:
    """Divide uma página cheia em duas após inserir a nova chave nela"""
    insereNaPagina(chave, filhoD, pag)

    meio = ORDEM // 2
    chavePro = pag.chaves[meio]

    # RRN que a nova página terá no disco
    arq.seek(0, os.SEEK_END)
    filhoDPro = (arq.tell() - HEADER_SIZE) // Pagina.tamanho_pagina()

    pAtual = Pagina()
    pAtual.numChaves = meio

    # Copia os dados da metade esquerda
    for i in range(meio):
        pAtual.chaves[i] = pag.chaves[i]
        pAtual.filhos[i] = pag.filhos[i]
    pAtual.filhos[meio] = pag.filhos[meio]

    pNova = Pagina()
    tam_dir = pag.numChaves - (meio + 1)
    pNova.numChaves = tam_dir

    # Copia os dados da metade direita
    for i in range(tam_dir):
        pNova.chaves[i] = pag.chaves[meio + 1 + i]
        pNova.filhos[i] = pag.filhos[meio + 1 + i]
    pNova.filhos[tam_dir] = pag.filhos[pag.numChaves]

    return chavePro, filhoDPro, pAtual, pNova


def gerenciadorDeInsercao(arq: io.BufferedRandom, raiz: int, entradas: list) -> int:
    """Gerencia a inserção de uma lista de chaves na árvore B"""
    for chave in entradas:
        if raiz == FILHO_NULO:
            pNova = Pagina()
            pNova.chaves[0] = chave
            pNova.numChaves = 1

            raiz = aloca_pag(arq, pNova)
            continue

        chavePro, filhoDpro, promocao = insereNaArvore(arq, raiz, chave)

        if promocao:
            pNova = Pagina()
            pNova.chaves[0] = chavePro
            pNova.filhos[0] = raiz
            pNova.filhos[1] = filhoDpro
            pNova.numChaves += 1
            raiz = aloca_pag(arq, pNova)

    return raiz


# Inserção na árvore


def insereNaArvore(arq: io.BufferedRandom, rrn: int, chave: tuple) -> tuple:
    """Inserção recursiva na árvore com promoção de chave"""

    if rrn is None or rrn == FILHO_NULO:
        # Chegou "abaixo" de uma folha, promove a própria chave
        return chave, None, True

    pag = ler_pag(arq, rrn)

    i = 0
    while i < pag.numChaves and chave[0] > pag.chaves[i][0]:
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
        chavePro, filhoDpro, pAtual, pNova = divide(arq, chavePro, filhoDpro, pag)
        escrever_pag(arq, rrn, pAtual)
        aloca_pag(arq, pNova)
        return chavePro, filhoDpro, True


# Execução do Arquivo de operações


def executar_operacoes(nome_arquivo: str) -> None:
    """Lê o arquivo de operações e as executa sequencialmente em games.dat e btree.dat"""

    if not os.path.exists("games.dat"):
        print("Erro: arquivo games.dat não encontrado.")
        return

    if not os.path.exists("btree.dat"):
        print("Erro: arquivo btree.dat não encontrado.")
        return

    if not os.path.exists(nome_arquivo):
        print(f"Erro: arquivo de operações '{nome_arquivo}' não encontrado.")
        return

    if not os.path.exists(BTREE_FILE):
        # Cria e ja grava -1 no cabeçalho
        with open(BTREE_FILE, "wb") as bf:
            bf.write(struct.pack(HEADER_FORMAT, FILHO_NULO))

    with open(nome_arquivo, "r") as arq:
        linhas = []
        for i in arq:
            linha = i.strip()
            if linha:
                linhas.append(linha)

    with open(GAMES_FILE, "r+b") as gf, open(BTREE_FILE, "r+b") as bf:
        raiz = ler_raiz(bf)

        for linha in linhas:
            op = linha[0]
            arg = linha[2:].strip()

            if op == "b":
                chave = int(arg)
                print(f"Busca pelo registro de chave {chave}")
                resultado = buscar(bf, raiz, chave)
                if resultado is None:
                    print("Erro: chave não encontrada\n")
                else:
                    _, _, byte_off = resultado
                    registro = ler_registro(gf, byte_off)
                    n_bytes = len(registro.encode("utf-8"))
                    print(f"{registro} ({n_bytes} bytes - offset {byte_off})\n")

            elif op == "i":
                chave = parse_id(arg)
                print(f"Inserção do registro de chave {chave}")

                if buscar(bf, raiz, chave) is not None:
                    print(f"Erro: chave {chave} duplicada\n")
                    continue

                gf.seek(0, os.SEEK_END)
                byte_off = gf.tell()

                arg_bytes = arg.encode("utf-8")
                tamanho_registro = len(arg_bytes)

                gf.write(struct.pack("<H", tamanho_registro))
                gf.write(arg_bytes)

                raiz = gerenciadorDeInsercao(bf, raiz, [(chave, byte_off)])

                print(f"{arg} ({tamanho_registro} bytes - offset {byte_off})\n")

        escrever_raiz(bf, raiz)

    print(f"As operações do arquivo {nome_arquivo} foram executadas com sucesso.")


def criar_indice() -> None:
    """Lê games.dat estruturado por indicadores de tamanho e cria o índice."""
    if not os.path.exists(GAMES_FILE):
        print(f"Erro: arquivo {GAMES_FILE} não encontrado.")
        return

    with open(BTREE_FILE, "wb") as bf:
        bf.write(struct.pack(HEADER_FORMAT, FILHO_NULO))

    with open(BTREE_FILE, "r+b") as bf, open(GAMES_FILE, "rb") as gf:
        raiz = ler_raiz(bf)

        while True:
            byte_off = gf.tell()

            tamanho_bytes = gf.read(2)

            if not tamanho_bytes or len(tamanho_bytes) < 2:
                break

            tamanho_registro = struct.unpack("<H", tamanho_bytes)[0]

            linha_bytes = gf.read(tamanho_registro)
            linha_str = linha_bytes.decode("utf-8")

            chave = parse_id(linha_str)
            raiz = gerenciadorDeInsercao(bf, raiz, [(chave, byte_off)])

        escrever_raiz(bf, raiz)

    print(f"Índice criado com sucesso no arquivo {BTREE_FILE}.")


def imprimir_arvore() -> None:
    """Imprime o conteúdo de todas as páginas da árvore-B."""

    if not os.path.exists(BTREE_FILE):
        print(f"Erro: arquivo {BTREE_FILE} não encontrado.")
        return

    with open(BTREE_FILE, "rb") as bf:
        raiz_rrn = ler_raiz(bf)

        bf.seek(0, os.SEEK_END)
        tamanho_arquivo = bf.tell()

        if tamanho_arquivo <= HEADER_SIZE:
            print("A árvore-B está vazia.")
            return

        total_paginas = (tamanho_arquivo - HEADER_SIZE) // Pagina.tamanho_pagina()

        for rrn in range(total_paginas):
            pag = ler_pag(bf, rrn)
            eh_raiz = rrn == raiz_rrn

            if eh_raiz:
                print("- - - - - - - - - - - - Raiz - - - - - - - - - - - -")
                print()

        chaves = ""
        offsets = ""
            
        for i in range(len(pag.chaves)):
            if pag.chaves[i] is not None:
                chaves += str(pag.chaves[i][0])
                offsets += str(pag.chaves[i][1])
            else:
                chaves += "-1"
                offsets += "-1"
            
            if i < len(pag.chaves) - 1:
                chaves += " | "
                offsets += " | "

            filhos = ""
            
            for i in range(len(pag.filhos)):
                if pag.filhos[i] is not None:
                    filhos += str(pag.filhos[i])
                else:
                    filhos += "-1"
                    
                if i < len(pag.filhos) - 1:
                    filhos += " | "

            print(f"Página {rrn}:")
            print(f"Chaves = {chaves}")
            print(f"Offsets = {offsets}")
            print(f"Filhos = {filhos}\n")

            if eh_raiz:
                print("- - - - - - - - - - - - - - - - - - - - - - - - - -\n")


def main() -> None:
    args = sys.argv[1:]

    if not args:
        print("Uso: python programa.py -b | -e <arquivo_ops> | -p")
        return

    flag = args[0]

    if flag == "-b":
        criar_indice()
    elif flag == "-e":
        if len(args) < 2:
            print("Erro, informe o nome do arquivo de operações")
        else:
            executar_operacoes(args[1])
    elif flag == "-p":
        imprimir_arvore()
    else:
        print(f"Flag desconhecida: {flag}")
        print("Uso: python programa.py -b | -e <arquivo_ops> | -p")


if __name__ == "__main__":
    main()
