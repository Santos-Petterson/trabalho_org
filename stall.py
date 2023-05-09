# Abre o arquivo de texto em modo leitura ('r')
arquivo = open('ttt.txt', 'r')

#Instrução nop (add zero, zero, zero)
nop = "00000000000000000000000000110011"
# Lista para armazenar todas as instrucoes
lista_instrucoes = []

# Gerar a lista de instrucoes a partir do arquivo
for linha in arquivo:
    
    # Pega o binario e armazena na lista
    binario = linha[:32]
    lista_instrucoes.append(binario)


#--FUNÇÕES GERAIS--

def get_type(instrucao):
    opcode = instrucao[-7:]

    match opcode:
        # Possui apenas rd (tipo B)
        case '0110111' | '0010111' | '1101111':
            return 0
        # Possui rd e rs1 (tipo I)
        case '1100111' | '0000011' | '0010011': 
            return 1
        # Possui rd, rs1 e rs2 (tipo R)
        case '0110011':
            return 2
        # Possui rs1 e rs2 (tipo SW)
        case '1100011' | '0100011':
            return 3

    # ecall e outros que nao serao contabilizados
    return -1

def is_branch(instrucao):
    opcode = instrucao[-7:]

    if opcode == '1100011':
        return True
    return False

def is_load(instrucao):
    opcode = instrucao[-7:]

    # Se a instrucao for uma load word, retorna true
    if opcode == '0000011':
        return True
    return False

# Verifica se há hazard do tipo RAW
def is_raw_hazard(instrucao_atual, instrucao_proxima):
    tipo_proxima = get_type(instrucao_proxima)
    rd = instrucao_atual[20:25]

    if tipo_proxima == 1:
        # Armazena o rs1 da instrucao da vez
        rs1 = instrucao_proxima[12:17]
        # Caso a proxima instrucao use o rd em rs1 da instrucao atual, existe um hazard
        if rs1 == rd:
            return True
    elif tipo_proxima == 2 or tipo_proxima == 3:
        # Armazena o rs1 da instrucao da vez
        rs1 = instrucao_proxima[12:17]
        # Armazena o rs2 da instrucao da vez
        rs2 = instrucao_proxima[7:12]
        # Caso a proxima instrucao use o rd em rs1 ou rs2 da instrucao atual, existe um hazard
        if rs1 == rd or rs2 == rd:
            return True
        
    return False

# Verifica se há hazard do tipo WAR
def is_waw_hazard(instrucao_atual, instrucao_proxima):
    # Pega o rd da instrucao avaliada
    rd_atual = instrucao_atual[20:25]
    # Pega o rd da proxima instrucao
    rd_proxima = instrucao_proxima[20:25]

    # Verifica se o rd da instrucao atual e da proxima sao iguais
    return rd_atual == rd_proxima

# Gera um arquivo de texto
def gerar_arquivo(nome_arquivo, lista_instrucoes):
    with open(nome_arquivo+'.txt', 'w') as file:
        for instruction in lista_instrucoes:
            file.write(instruction + '\n')


#--QUESTÃO 1--

# Apenas insercao de stalls para evitar hazards
def questao1(lista_instrucoes):
    # Lista com a correção final da aplicação
    lista_instrucoes_corrigida = []

    for i in range(len(lista_instrucoes)):
        tipo_atual = get_type(lista_instrucoes[i])

        #Adiciona linha na Lista Corrigida
        lista_instrucoes_corrigida.append(lista_instrucoes[i])

        # Se caso nao possuir rd, vai para a proxima iteracao
        if tipo_atual == 3 | tipo_atual == -1:
            continue
        
        # Verificacoes quando perto do fim da lista
        if len(lista_instrucoes)-1 == i:
            continue
        elif len(lista_instrucoes) - i <= 2:
            limite_superior = 2
        else:
            limite_superior = 3

        # Verificacoes de instrucoes proximas
        for j in range(1, limite_superior):
            if is_raw_hazard(lista_instrucoes[i], lista_instrucoes[i + j]) or is_waw_hazard(lista_instrucoes[i], lista_instrucoes[i + j]):
                # Adiciona nop na Lista Corrigida
                if j == 1:
                    lista_instrucoes_corrigida.append(nop)
                    lista_instrucoes_corrigida.append(nop)
                    break
                else:
                    lista_instrucoes_corrigida.append(nop)
    return lista_instrucoes_corrigida


#--QUESTÃO 2--

# Implementacao de forwarding no hardware para evitar hazards
def questao2(lista_instrucoes):
    # Lista com a correção final da aplicação
    lista_instrucoes_corrigida = []

    for i in range(len(lista_instrucoes)):
        # Pega o rd da instrucao avaliada
        rd = lista_instrucoes[i][20:25]
        tipo_atual = get_type(lista_instrucoes[i])

        #Adiciona linha na Lista Corrigida
        lista_instrucoes_corrigida.append(lista_instrucoes[i])

        # Se caso nao possuir rd, vai para a proxima iteracao
        if tipo_atual == 3 | tipo_atual == -1:
            continue
        
        # Verificacoes quando perto do fim da lista
        if len(lista_instrucoes)-1 == i:
            continue
        else:
            limite_superior = 2

        # Verificacoes de instrucoes proximas
        for j in range(1, limite_superior):
            if is_raw_hazard(lista_instrucoes[i], lista_instrucoes[i + j]) or is_waw_hazard(lista_instrucoes[i], lista_instrucoes[i + j]):
                # Adiciona nop na Lista Corrigida
                if is_load(lista_instrucoes[j + i]):
                    lista_instrucoes_corrigida.append(nop)
                    lista_instrucoes_corrigida.append(nop)
                    break
                else:
                    lista_instrucoes_corrigida.append(nop)
    return lista_instrucoes_corrigida


#--QUESTÃO 3--

# Armazena um dicionário de registradores, inicializando todos em 0
def get_registradores(lista_instrucoes):
    lista_registradores = {}

    for instrucao in lista_instrucoes:

        tipo_instrucao = get_type(instrucao)

        if tipo_instrucao == 1: #Se tipo I
            # Salva registradores rd e rs1
            lista_registradores.update({instrucao[20:25]:0})
            lista_registradores.update({instrucao[12:17]:0})

        if tipo_instrucao == 2: #Se tipo R
            # Salva registradores rd, rs1 e rs2
            lista_registradores.update({instrucao[20:25]:0})
            lista_registradores.update({instrucao[12:17]:0})
            lista_registradores.update({instrucao[7:12]:0})

        if tipo_instrucao == 3: #Se tipo SW
            # Salva registradores rs1 e rs2
            lista_registradores.update({instrucao[12:17]:0})
            lista_registradores.update({instrucao[7:12]:0})
            

    return lista_registradores

# Reordena uma lista de instruções, com base em seus registradores, considerando implementação de forwarding
def reordenar_instrucoes(lista_instrucoes):

    # Dicionário/Lista de registradores, verifica se registradores estão atualizados
    lista_registradores = get_registradores(lista_instrucoes)

    lista_instrucoes_reordenada = [] # Lista final a ser retornada
    lista_instrucoes_hazard = [] # Lista que armazenará as instruções afetadas por hazard, até que sejam reposicionadas corretamente
    i = 0

    while len(lista_instrucoes_reordenada) != len(lista_instrucoes):
        #rs = r1 rt=r2  rd= r destino

        if len(lista_instrucoes_hazard) != 0:
            for instrucao_hazard in lista_instrucoes_hazard:
                instrucao_hazard_type= get_type(instrucao_hazard)
                if instrucao_hazard_type == 1: #tipo I
                  rd= instrucao_hazard[20:25]
                  rs1= instrucao_hazard[12:17]
                  if lista_registradores[rd] == 0 and lista_registradores[rs1] == 0:
                    lista_instrucoes_reordenada.append(instrucao_hazard)
                    lista_registradores.update({rd:3})
                    lista_instrucoes_hazard.remove(instrucao_hazard)
                if instrucao_hazard_type == 2: #tipo R
                  rd= instrucao_hazard[20:25]
                  rs1= instrucao_hazard[12:17]
                  rs2=instrucao_hazard[7:12]
                  if lista_registradores[rd] == 0 and lista_registradores[rs1] == 0 and lista_registradores[rs2] == 0:
                    lista_instrucoes_reordenada.append(instrucao_hazard)
                    lista_registradores.update({rd:3})
                    lista_instrucoes_hazard.remove(instrucao_hazard)
                if instrucao_hazard_type == 3: #tipo Sw
                  rs1= instrucao_hazard[12:17] 
                  rs2=instrucao_hazard[7:12]
                  if lista_registradores[rs1] == 0 and lista_registradores[rs2] == 0:
                    lista_instrucoes_reordenada.append(instrucao_hazard)
                    lista_registradores.update({rs1:2})
                    lista_registradores.update({rs2:2})
                    lista_instrucoes_hazard.remove(instrucao_hazard)

        if i < len(lista_instrucoes):
            instrucao = lista_instrucoes[i]
            instrucao_type = get_type(instrucao)

            if is_branch(instrucao): # Branch
                # Não altera nada após um branch, recoloca todas as instruções na sequencia inicial e encerra a função
                while len(lista_instrucoes_reordenada) != len(lista_instrucoes):
                    lista_instrucoes_reordenada.append(lista_instrucoes[i])
                    i += 1
                break
            
            if instrucao_type == 0: # Tipo B
                rd = instrucao[20:25]
                if lista_registradores[rd] == 0:
                    lista_instrucoes_reordenada.append(instrucao)
                    lista_registradores.update({rd:3})
                else:
                    lista_instrucoes_hazard.append(instrucao)

            if instrucao_type == 1: # Tipo I
                rd = instrucao[20:25]
                rs1 = instrucao[12:17]
                if lista_registradores[rd] == 0 and lista_registradores[rs1] == 0:
                    lista_instrucoes_reordenada.append(instrucao)
                    lista_registradores.update({rd:3})
                else:
                    lista_instrucoes_hazard.append(instrucao)

            if instrucao_type == 2: # Tipo R
                rd = instrucao[20:25]
                rs1 = instrucao[12:17]
                rs2 = instrucao[7:12]
                if lista_registradores[rd] == 0 and lista_registradores[rs1] == 0 and lista_registradores[rs2] == 0:
                    lista_instrucoes_reordenada.append(instrucao)
                    lista_registradores.update({rd:3})
                else:
                    lista_instrucoes_hazard.append(instrucao)

            if instrucao_type == 3: # Tipo SW
                rs1 = instrucao[12:17]
                rs2 = instrucao[7:12]
                print(instrucao[-7:])
                print(rs1)
                print(rs2)
                if lista_registradores[rs1] == 0 and lista_registradores[rs2] == 0:
                    lista_instrucoes_reordenada.append(instrucao)
                    lista_registradores.update({rs1:2})
                    lista_registradores.update({rs2:2})
                else:
                    lista_instrucoes_hazard.append(instrucao)

            i += 1

        # Decrementa dicionário de registradores
        for reg in lista_registradores:
            if lista_registradores[reg] > 0:
                lista_registradores[reg] -= 1

    return lista_instrucoes_reordenada

# Implementacao de forwarding no hardware + reordenacao de instrucoes + stalls para evitar hazards
def questao3(lista_instrucoes):
    lista_instrucoes_reordenada = reordenar_instrucoes(lista_instrucoes)
    lista_instrucoes_reordenada = questao2(lista_instrucoes_reordenada)
    return lista_instrucoes_reordenada


#--MAIN--

lista_instrucoes_corrigida_questao1 = questao1(lista_instrucoes)
gerar_arquivo("result_questao1", lista_instrucoes_corrigida_questao1)

lista_instrucoes_corrigida_questao2 = questao2(lista_instrucoes)
gerar_arquivo("result_questao2", lista_instrucoes_corrigida_questao2)

lista_instrucoes_corrigida_questao3 = questao3(lista_instrucoes)
gerar_arquivo("result_questao3", lista_instrucoes_corrigida_questao3)