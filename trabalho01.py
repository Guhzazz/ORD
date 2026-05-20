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
    print("Uso do programa:\n" \
    "python programa.py -flag\n" \
    "Flags disponíveis: -b(construir), -e(arq operações), -c(compactar)")
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

def le_registro(arquivo: io.TextIOWrapper, offset: int)-> tuple[Jogo | None, int]:
    '''Lê um único registro do arquivo baseado no byte-offset informado'''
    try:
        arquivo.seek(offset, os.SEEK_SET)
        header = arquivo.read(HEADER_SIZE)
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


def percorre_registros(arquivo: io.TextIOWrapper)-> list[tuple[Jogo, int]]:
    '''Percorre o arquivo do ínicio ao fim, pulando arquivos logicamente removidos'''
    resultado = []
    offset = 0
    tamanho_arquivo = os.path.getsize(GAMES_FILE)
    with open(GAMES_FILE, "rb") as arquivo:
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
    '''Lê  o arquivo primario.ind e reconstrói a lista indice_primario na memória'''
    indice: IndicePrimario = []
    with open(PRIMARY_IND, "r") as arq:
        for linha in arq:
            linha = linha.strip()
            partes = linha.split("|")
            indice.append(EntradaPrimaria(id=int(partes[0]), offset=int(partes[1])))
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
            indice.append(EntradaSecundaria(chave=partes[0], pos=int(partes[1])))
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
            lista.append(NoListainvertida(id=int(partes[0]), prox=int(partes[1])))
    return lista


def constroe_indice()-> None:
    '''Utiliza as funções de "salva" e "carrega" dos indices primarios, secundários
    e a lista invertida para consttuir os indices do programa'''
    jogos_lidos = percorre_registros(GAMES_FILE)
    print(f"\nTotal de jogos válidos encontrados: {len(jogos_lidos)}")
    for jogo, offset in jogos_lidos[:3]:
        print(f"Offset: {offset} | Jogo: {jogo.id} - {jogo.nome} ({jogo.genero})")

    return None


def formata_registro(jogo: Jogo)-> str:
    '''Formata um jogo na representação textual exigida para a saída'''
    return (f"{jogo.id}|{jogo.nome}|{jogo.ano}|"
            f"{jogo.genero}|{jogo.publicadora}|{jogo.plataforma}|")


def busca_binaria(indice: IndicePrimario, id_buscado: int)-> int:
    '''Realiza uma busca binária pelo id.
    Retorna o índice do elemento na lista ou -1 se ele não for encontrado'''
    esq, dir = 0, (len(indice) -1)
    while esq <= dir:
        meio = (esq + dir) //2
        if indice[meio].id == id_buscado:
            return meio
        elif indice[meio].id < id_buscado:
            esq = meio + 1
        else:
            dir = meio - 1
    return -1

def busca_binaria_secundaria(indice: IndiceSecundario, chave_buscada: str) -> int:
    '''Realiza uma busca binária no índice secundário pela string da chave.'''
    esq, dir = 0, (len(indice) -1)
    while esq <= dir:
        meio = (esq + dir) //2
        if indice[meio].chave == chave_buscada:
            return meio
        elif indice[meio].chave < chave_buscada:
            esq = meio + 1
        else:
            dir = meio - 1
    return -1

def busca_primario(indice: IndicePrimario, id_buscado: int)-> None:
    '''Busca e imprime o registro correspondente a id_buscado usando o índice primário'''
    print(f"Busca pelo registro de id: {id_buscado}")
    pos = busca_binaria(indice, id_buscado)
    if pos == -1:
        print("Registro não encontrado.")
    else:
        offset = indice[pos].offset
        with open(GAMES_FILE, "rb") as arq:
            jogo, _ = le_registro(arq, offset)
            if jogo:
                print(formata_registro(jogo))
            else:
                print("Registro não encontrado.")
        

def busca_secundario(indice: IndiceSecundario, lst_inv: ListaInvertida, chave: str, tipo: str)->None:
    '''Busca e imprime todos os registros associados a uma chave secundária,
    percorrendo a lista invertida e acessando cada registro por byte-offset'''
    if tipo == "genero":
        print(f"Busca por registros de gênero: {chave}")
    else:
        print(f"Busca por registros da publicadora: {chave}")

    pos_ind = busca_binaria_secundaria(indice, chave)
    if pos_ind == -1:
        print("Registro não encontrado.")
    else:    
        ids = []
        pos = indice[pos_ind].pos
        while pos != -1:
            no = lst_inv[pos]
            ids.append(no.id)
            pos = no.prox
        print(f"({len(ids)}) registros")

        indice_primario = carrega_indice_primario()
        with open(GAMES_FILE, "rb") as arq:
            for id_jogo in ids:
                pos_p = busca_binaria(indice_primario, id_jogo)
                if pos_p != -1:
                    jogo, _ = le_registro(arq, indice_primario[pos_p].offset)
                    if jogo:
                        print(formata_registro(jogo))




def insercao():
    pass

def remocao():
    pass

def compactacao():
    pass
















if __name__ == "__main__":
    main()
