import io
import os
from sys import argv

GAMES_FILE = "games.dat"
HEADER_SIZE = 2
DELETION_MARK = "*"
PRIMARY_IND = "primario.ind"

def main() -> None:
    print(salva_indice_primario(PRIMARY_IND))
   # print("Uso do programa:\n")
    '''try:
        flag = argv[1]
        if flag == "-b":
            pass
        elif flag == "-e":
            if len(argv) < 3:
                print("Erro: Informe também o arquivo de operações")
                pass
        elif flag == "-c":
            pass
        else:
            print(f"Flag não identificada: {flag}")
    except Exception as e:
        print("Erro")
'''
class Jogo:
    '''Representa um jogo do arquivo games.dat'''
    id: int
    nome: str
    ano: str
    genero: str
    publicadora: str
    plataforma: str
    raw: str

class EntradaPrimaria:
    '''Abriga a chave primaria do jogo e o offset do registro'''
    id: int
    offset: int

class EntradaSecundaria:
    '''Abriga o valor da chave secundária do jogo e a posição na lista invertida'''
    chave: str
    pos: int

class NoListainvertida:
    '''Representa um nó da lista invertida, com id e índice do próximo nó'''
    id: int
    prox: int

#Aliases 
IndicePrimario = list[EntradaPrimaria]
IndiceSecundario = list[EntradaSecundaria]
ListaInvertida = list[NoListainvertida]

def le_registro(arquivo: io.TextIOWrapper, offset: int)-> tuple[Jogo | None, int]:
    '''Lê um único registro do arquivo baseado no byte-offset informado'''
    try:
        with open(arquivo, "rb") as arquivo:

            arquivo.seek(offset, os.SEEK_SET)
            header = arquivo.read(HEADER_SIZE)
            if len(header) < HEADER_SIZE:
                return None, 0
            
            tamanho = int.from_bytes(header, 'little')
            conteudo_bytes = arquivo.read(tamanho)
            if len(conteudo_bytes) < tamanho:
                return None, 0
            
            conteudo = conteudo_bytes.decode()
            if conteudo.startswith(DELETION_MARK):
                return None, HEADER_SIZE + tamanho
            
            campos = conteudo.rstrip("|").split(sep="|")
            if len(campos) < 6:
                return None, HEADER_SIZE + tamanho
        
            jogo = Jogo = {
                "id": int(campos[0]),
                "nome": campos[1],
                "ano": campos[2],
                "genero": campos[3],
                "publicadora": campos[4],
                "plataforma": campos[5],
                "raw": conteudo
            }
            return jogo, HEADER_SIZE + tamanho
    except FileNotFoundError:
        print("Erro em le_arquivo")


def percorre_registros(arquivo: io.TextIOWrapper)-> list[tuple[Jogo, int]]:
    '''Percorre o arquivo do ínicio ao fim, pulando arquivos removidos'''
    resultado = []
    offset = 0
    tamanho_arquivo = os.path.getsize(GAMES_FILE)
    while offset < tamanho_arquivo:
        jogo, total = le_registro(arquivo, offset)
        if total == 0:
            return None
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
    '''Lê primario.ind e reconstrói a lista na memória'''
    with open(PRIMARY_IND, 'r') as arq:
        pass





def constroe_indice():
    pass

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