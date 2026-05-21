import io
import os
from sys import argv
from struct import pack, unpack
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
        executa_operacoes(arquivo_operacoes)
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
            arq.write(f"{dado.id} | {dado.offset}\n")


def carrega_indice_primario()-> IndicePrimario:
    '''Lê  o arquivo primario.ind e reconstrói a lista indice_primario na memória'''
    try:
        indice: IndicePrimario = []
        with open(PRIMARY_IND, "r") as arq:
            for linha in arq:
                linha = linha.strip()
                partes = linha.split("|")
                indice.append(EntradaPrimaria(id = int(partes[0]), offset = int(partes[1])))
    except FileNotFoundError:
        print("Erro, arquivo não encontrado")
    return indice


def salva_indice_secundario(indice: IndiceSecundario, caminho: str)-> None:
    "Persiste um índice secundário(genêro ou publicadora)"
    with open(caminho, "w") as arq:
        for entrada in indice:
            arq.write(f"{entrada.chave}|{entrada.pos}\n")


def carrega_indice_secundario(caminho: str)-> IndiceSecundario:
    "Lê um arquivo de índice secundario e reconstrói a lista na memória"
    try:
        indice: IndiceSecundario = []
        with open(caminho, "r") as arq:
            for linha in arq:
                linha = linha.strip()
                partes = linha.split("|", 1)
                indice.append(EntradaSecundaria(chave = partes[0], pos = int(partes[1])))
    except FileNotFoundError:
        print("Erro, arquivo não encontrado")
    return indice


def salva_lista_invertida(lista: ListaInvertida)-> None:
    '''Persiste a lista invertida em listaInvertida.lst. O índice de cada elemento
    na lista é a sua posição lógica'''
    with open(INV_LIST_FILE, "w") as arq:
        for no in lista:
            arq.write(f"{no.id}|{no.prox}\n")


def carrega_lista_invertida()-> ListaInvertida:
    "Lê o arquivo listaInvertida.lst e reconstrói a lista na memória"
    try:
        lista: ListaInvertida =[]
        with open(INV_LIST_FILE, "r") as arq:
            for linha in arq:
                linha = linha.strip()
                partes = linha.split("|")
                lista.append(NoListainvertida(id = int(partes[0]), prox = int(partes[1])))
    except FileNotFoundError:
        print("Erro, arquivo não encontrado")
    return lista


def constroe_indice()-> None:
    '''Utiliza as funções de "salva" e "carrega" dos indices primarios, secundários
    e a lista invertida para consttuir os indices do programa'''
    jogos_lidos = percorre_registros(GAMES_FILE)
    print(f"\nTotal de jogos válidos encontrados: {len(jogos_lidos)}")

    indice_primario: IndicePrimario = []

    for jogo, offset in jogos_lidos[:3]:
        print(f"Offset: {offset} | Jogo: {jogo.id} - {jogo.nome} ({jogo.genero})")

    for jogo, offset in jogos_lidos:
        indice_primario.append(EntradaPrimaria(id = jogo.id, offset = offset))
        

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





def insercao(ind_primario: IndicePrimario, ind_genero: IndiceSecundario, ind_publicadora: IndiceSecundario, lst: ListaInvertida, linha_op: str)-> None:
    '''Insere um registro no final de "games.dat" e atualiza os índices.
    Rejeita a inserção se o id já existir'''

    campos = linha_op.strip("|").split("|")

    if len(campos) >= 6:
        id_novo = int(campos[0])
        nome = campos[1]
        ano = campos[2]
        genero = campos[3]
        publicadora = campos[4]
        plataforma = campos[5]

        print(f"Inserção do registro de chave {id_novo}")

        if busca_binaria(ind_primario, id_novo) != -1:
            print("ID duplicado, a inserção não pode ser realizada")
        else:
            conteudo = f"{id_novo}|{nome}|{ano}|{genero}|{publicadora}|{plataforma}"
            conteudo_bytes = conteudo.encode()
            tam = len(conteudo_bytes)
            header = pack(HEADER_FORMAT, tam)

            with open(GAMES_FILE, "r+b") as arq:
                arq.seek(0, os.SEEK_END)
                offset = arq.tell()
                arq.write(header + conteudo_bytes)
                print(f"Inserido com sucesso ({HEADER_SIZE + tam} bytes)")

            entrada = EntradaPrimaria(id = id_novo, offset = offset)
            pos_insercao = 0
            i = 0
            while i < len(ind_primario):
                if ind_primario[i].id < id_novo:
                    pos_insercao = i + 1
                i += 1
            ind_primario.insert(pos_insercao, entrada)

            atualiza_secundario(ind_genero, lst, id_novo, genero)
            atualiza_secundario(ind_publicadora, lst, id_novo, publicadora)


def atualiza_secundario(indice: IndiceSecundario, lst: ListaInvertida, id_novo: int, chave: str)-> None:
    '''Adiciona id_novo à cadeia de chave no índice secundário e na lista invertida
    Se a chave ainda não existir, cria uma nova entrada no índice secundário'''

    pos_ind = busca_binaria_secundaria(indice, chave)
    pos_novo = len(lst)
    lst.append(NoListainvertida(id = id_novo, prox = -1))
    
    if pos_ind == -1:
        entrada = EntradaSecundaria(chave = chave, pos = pos_novo)
        pos_insercao = 0
        i = 0
        while i < len(indice):
            if indice[i].chave < chave:
                pos_insercao = i + 1
            i += 1
        indice.insert(pos_insercao, entrada)
    else:
        pos = indice[pos_ind].pos
        while lst[pos].prox != -1:
            pos = lst[pos].prox
        lst[pos].prox = pos_novo


def remove_da_lista_invertida(indice: IndiceSecundario, lst_inv: ListaInvertida, chave: str, id_remover: int) -> None:
    '''Remove id_remover da cadeia da lista invertida associada à chave.'''
    pos_ind = busca_binaria_secundaria(indice, chave)
    if pos_ind == -1:
        return None
 
    pos_atual = indice[pos_ind].pos
    pos_anterior = -1
 
    while pos_atual != -1:
        no = lst_inv[pos_atual]
        if no.id == id_remover:
            if pos_anterior == -1:
                indice[pos_ind].pos = no.prox
            else:
                lst_inv[pos_anterior].prox = no.prox
 
            if indice[pos_ind].pos == -1:
                indice.pop(pos_ind)
            return None
        pos_anterior = pos_atual
        pos_atual = no.prox


def remocao(id_remov: int,  indice_primario: IndicePrimario, ind_genero: IndiceSecundario, ind_publicadora, lst: ListaInvertida) -> None:
    '''Remove o registro logicamente e marca com '*' no arquivo.'''
 
    pos_p = busca_binaria(indice_primario, id_remov)
    if pos_p == -1:
        print("Registro não encontrado")
        return
 
    offset = indice_primario[pos_p].offset
 
    with open(GAMES_FILE, "rb") as arq:
        jogo, _ = le_registro(arq, offset)
 
    if jogo is None:
        print(f"Inconsistência: offset {offset} não contém registro válido.")
        return
 
    byte_original = None
    try:
        with open(GAMES_FILE, "r+b") as arq:
            arq.seek(offset + HEADER_SIZE, os.SEEK_SET)
            byte_original = arq.read(1)
            arq.seek(offset + HEADER_SIZE, os.SEEK_SET)
            arq.write(DELETION_MARK.encode())
 
        indice_primario.pop(pos_p)
        remove_da_lista_invertida(ind_genero, lst, jogo.genero, id_remov)
        remove_da_lista_invertida(ind_publicadora, lst, jogo.publicadora, id_remov)
 
        print(f'Remoção do registro de chave "{id_remov}" (offset = {offset})')
 
    except Exception as e:
        if byte_original is not None:
            with open(GAMES_FILE, "r+b") as arq:
                arq.seek(offset + HEADER_SIZE, os.SEEK_SET)
                arq.write(byte_original)
        print(f"Erro: {e}")

    return None


def executa_operacoes(arq_operacoes: str) -> None:
    '''Executa as operações presentes no arquivo .txt de operações'''

    indice_primario = carrega_indice_primario()
    ind_genero = carrega_indice_secundario(GENRE_IND)
    ind_publicadora = carrega_indice_secundario(PUBLISHER_IND)
    lst = carrega_lista_invertida()

    try:
        with open(arq_operacoes, 'r') as operacoes:
            for operacao in operacoes:
                operacao = operacao.strip()
                if not operacao:
                    continue
                
                partes = operacao.split(" ", 1)
                comando = partes[0]
                resto = partes[1]

                if comando == "bp":
                    busca_primario(indice_primario, int(resto))
                elif comando == "bs1":
                    busca_secundario(ind_genero, lst, resto, "genero")
                elif comando == "bs2":
                    busca_secundario(ind_publicadora, lst, resto, "publicadora")
                elif comando == "i":
                    insercao(indice_primario, ind_genero, ind_publicadora, lst, resto)
                elif comando == "r":
                    remocao(int(resto), indice_primario, ind_genero, ind_publicadora, lst)
                else:
                    print("Operação inválida.")
    
    except FileNotFoundError:
        print("Arquivo não encontrado.")

def compactacao():
    pass
















if __name__ == "__main__":
    main()
