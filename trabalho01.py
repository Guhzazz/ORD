import io
import os
from sys import argv
from struct import pack, unpack, calcsize
from dataclasses import dataclass

GAMES_FILE = "games.dat"
HEADER_SIZE = 2
DELETION_MARK = "*"
PRIMARY_IND = "primario.ind"
GENRE_IND = "genero.ind"
PUBLISHER_IND = "publicadora.ind"
HEADER_FORMAT = "h"
INV_LIST_FILE = "listaInvertida.lst"

def main() -> None:
   # print("Uso do programa:\n")
    try:
        if len(argv) < 2:
            raise TypeError("Número incorreto de argumentos\n")

        flag = argv[1]
        if flag == "-b":
            constroe_indice()
        elif flag == "-e":
            if len(argv) < 3:
                print("Erro: Informe também o arquivo de operações")
                return None
            arquivo_operacoes = argv[2]
        elif flag == "-c":
            pass
        else:
            print(f"Flag não identificada: {flag}")
    except Exception as e:
        print("Erro")

@dataclass
class Jogo:
    '''Representa um jogo do arquivo games.dat'''
    id: int
    nome: str
    ano: str
    genero: str
    publicadora: str
    plataforma: str
    raw: str

@dataclass
class EntradaPrimaria:
    '''Abriga a chave primaria do jogo e o offset do registro'''
    id: int
    offset: int

@dataclass
class EntradaSecundaria:
    '''Abriga o valor da chave secundária do jogo e a posição na lista invertida'''
    chave: str
    pos: int

@dataclass
class NoListainvertida:
    '''Representa um nó da lista invertida, com id e índice do próximo nó'''
    id: int
    prox: int

#Aliases 
IndicePrimario = list[EntradaPrimaria]
IndiceSecundario = list[EntradaSecundaria]
ListaInvertida = list[NoListainvertida]

def le_registro(arquivo: str, offset: int)-> tuple[Jogo | None, int]:
    '''Lê um único registro do arquivo baseado no byte-offset informado'''
    try:
        with open(arquivo, "rb") as arquivo:

            arquivo.seek(offset, os.SEEK_SET)
            header: str = arquivo.read(HEADER_SIZE)
            if len(header) < HEADER_SIZE:
                return None, 0
            
            tamanho = unpack(HEADER_FORMAT, header)[0]
            conteudo_bytes = arquivo.read(tamanho)
            if len(conteudo_bytes) < tamanho:
                return None, 0
            
            conteudo = conteudo_bytes.decode()
            if conteudo.startswith(DELETION_MARK):
                return None, HEADER_SIZE + tamanho
            
            campos = conteudo.rstrip("|").split(sep="|")
            if len(campos) < 6:
                return None, HEADER_SIZE + tamanho
        
            jogo = Jogo(
                id=int(campos[0]),
                nome=campos[1],
                ano=campos[2],
                genero=campos[3],
                publicadora=campos[4],
                plataforma=campos[5],
                raw=conteudo
            )
                
            return jogo, HEADER_SIZE + tamanho
        
    except FileNotFoundError:
        print("Erro em le_arquivo")


def percorre_registros(arquivo: str)-> list[tuple[Jogo, int]]:
    '''Percorre o arquivo do ínicio ao fim, pulando arquivos logicamente removidos'''
    resultado = []
    offset = 0
    tamanho_arquivo = os.path.getsize(arquivo)
    while offset < tamanho_arquivo:
        jogo, total = le_registro(arquivo, offset)
        if total == 0:
            break
        if jogo is not None:
            resultado.append((jogo, offset))
        offset += total
    return resultado


def salva_indice_primario(indice: IndicePrimario)-> None:
    '''Persiste o íncice primário em primario.ind'''
    with open(PRIMARY_IND, 'w') as arq:
        for dado in indice:
            arq.write(f"{dado['id']} | {dado['offset']}\n")


def carrega_indice_primario()-> IndicePrimario:
    '''Lê  o arquivo primario.ind e reconstrói a lista indice_primario na memória'''
    indice: IndicePrimario = []
    with open(PRIMARY_IND, "r") as arq:
        for linha in arq:
            linha = linha.strip()
            partes = linha.split("|")
            indice.append({"id": int(partes[0]), "offset": int(partes[1])})
    return indice


def salva_indice_secundario(indice: IndiceSecundario, caminho: str)-> None:
    "Persiste um índice secundário(genêro ou publicadora)"
    with open(caminho, "w") as arq:
        for entrada in indice:
            arq.write(f"{entrada['chave']}|{entrada['pos']}\n")


def carrega_indice_secundario(caminho: str)-> IndiceSecundario:
    "Lê um arquivo de índice secundario e reconstrói a lista na memória"
    indice: IndiceSecundario = []
    with open(caminho, "r") as arq:
        for linha in arq:
            linha = linha.strip()
            partes = linha.split("|", 1)
            indice.append({"chave": partes[0], "pos": int(partes[1])})
    return indice


def salva_lista_invertida(lista: ListaInvertida)-> None:
    '''Persiste a lista invertida em listaInvertida.lst. O índice de cada elemento
    na lista é a sua posição lógica'''
    with open(INV_LIST_FILE, "w") as arq:
        for no in lista:
            arq.write(f"{no['id']}|{no['prox']}\n")


def carrega_lista_invertida()-> ListaInvertida:
    "Lê o arquivo listaInvertida.lst e reconstrói a lista na memória"
    lista: ListaInvertida =[]
    with open(INV_LIST_FILE, "r") as arq:
        for linha in arq:
            linha = linha.strip()
            partes = linha.split("|")
            lista.append({"id": int(partes[0]), "prox": int(partes[1])})
    return lista


def constroe_indice() -> None:
    jogos_lidos = percorre_registros(GAMES_FILE)
    print(f"\nTotal de jogos válidos encontrados: {len(jogos_lidos)}")
    for jogo, offset in jogos_lidos[:3]:
        print(f"Offset: {offset} | Jogo: {jogo.id} - {jogo.nome} ({jogo.genero})")

    return None

def busca():
    pass

def insercao():
    pass

def remocao():
    pass

def compactacao():
    pass
















if __name__ == "__main__":
    main()
