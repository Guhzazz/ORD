# Integrantes:
# Gustavo Valério dos Santos RA 139067
# João Gabriel de Campos Nassar RA 

#Constantes
ORDEM = 5
CHAVE_NULA = -1
FILHO_NULO = -1
OFFSET_NULO = -1


class Pagina:
    '''Estrutura de uma página na árvore B'''
    def __init__(self)-> None:
        self.numChaves: int = 0
        self.chaves: list = [None] * (ORDEM - 1)
        self.filhos: list = [None] * ORDEM





def main()-> None:
    pass


if __name__ == "__main__":
    main()