#correspondencia = caminho do ficheiro com correspondência entre as novas e antigas freguesias
#nome_correspondencia = folha do ficheiro com correspondência entre as novas e antigas freguesias
#dados_estatisticos = caminho do ficheiro com os dados a transformar entre as duas organizações administrativas
#fl_daos_estatisticos = folha do ficheiro com os dados a transformar entre as duas organizações administrativas
#coln_dados_estatisticos = coluna do ficheiro com os dados a transformar a que se quer submeter a transformação.
#nome_folha_resultado = nome que se pretende dar à folha excel com o resultado
#ficheiro_resultado = caminho e nome do ficheiro para guardar a tabela final

#Modulos
import xlrd
import xlwt

#ler ficheiro transformação freguesias e cria dicionário
def ler_freg (transform_freg, nome_folha):
    dic = {}
    livro = xlrd.open_workbook(transform_freg)
    folha = livro.sheet_by_name(nome_folha)
    for linha in range (1, folha.nrows):
        lst = []
        for coluna in range(folha.ncols):
            if coluna == 0:
                nome_freg = folha.cell(linha, coluna). value
            elif coluna == 1:
                dicofre_novo = folha.cell (linha, coluna).value
            else:
                v = folha.cell(linha, coluna).value
                if v == '':
                    continue
                else:
                    if type(v) == type(10.0):
                        lst.append(str(int(v)))
                    else:
                        lst.append(v)
        dic[dicofre_novo] = [lst, nome_freg]
    return dic

#Ler ficheiro de dados estatísticos e associa o valor da variável a dicionário com chave equivalente ao Dicofre da nova freguesia.
def ler_variaveis (ficheiro_variaveis, folha, coln_dados):
    dados = {}
    book = xlrd.open_workbook(ficheiro_variaveis)
    flh = book.sheet_by_name(folha)
    for linha in range (1, flh.nrows):
        l = []
        for coluna in range (flh.ncols):
            if coluna == 0:
                continue
            elif coluna == 1:
                chave = flh.cell (linha, coluna).value
                if type(chave) == type(10.0) or type(chave) == type(10):
                    chave = str(int(chave))
            elif coluna >= coln_dados:
                valor = flh.cell (linha, coluna).value
                l.append(valor)
            else:
                continue
        dados [chave] = l
    return dados

#Substitui valor no dicionário das novas freguesias
def substituir_valor(dicionario_freg, dicionario_variavel):
    associacao = {}
    ldic = dicionario_variavel.keys()
    for chave in dicionario_freg.keys():
        lst = []
        for i in range(len(dicionario_variavel[ldic[0]])):
            l = []
            for freg_velha in dicionario_freg[chave][0]:
                if freg_velha in dicionario_variavel.keys():
                    l.append(dicionario_variavel[freg_velha][i])
            lst.append(l)
        for e in range(len(lst)):
            lst[e] = sum(lst[e])
        tst_lst = [0 for i in range(len(lst))]
        if lst == tst_lst:
            continue
        else:
            associacao[chave] = [lst, dicionario_freg[chave][1]]
    return associacao

# Cria ficheiro excel e coloca os valores das novas freguesias e variáveis.
def escreve_dados (associacao_dados, folha_saida, ficheiro_saida):
    ficheiro = xlwt.Workbook ()
    titulo = ficheiro.add_sheet (folha_saida)
    lista = ['dicofre', 'unidade territorial', 'valor variavel']
    for i in range (len(lista)):
        titulo.write (0 , i, lista [i])
    c_linha = 1
    for chave in associacao_dados.keys():
        freguesia = associacao_dados [chave] [1]
        info = associacao_dados [chave] [0]
        lista = [chave, freguesia] + info
        for i in range (len(lista)):
            titulo.write (c_linha, i, lista [i])
        c_linha += 1
    ficheiro.save(ficheiro_saida)
    
#definicacao geral     
def main(correspondencia, nome_correspondencia, dados_estatisticos, fl_dados_estatisticos, coln_dados_estatisticos, nome_folha_resultado, ficheiro_resultado):
    dic_novas_velhas = ler_freg (correspondencia,nome_correspondencia)
    dic_velhas_dados = ler_variaveis (dados_estatisticos, fl_dados_estatisticos, coln_dados_estatisticos)
    dados_por_nova_freg = substituir_valor(dic_novas_velhas, dic_velhas_dados)
    escreve_dados(dados_por_nova_freg, nome_folha_resultado, ficheiro_resultado)
    
#chama definicao
main('D:/Dropbox/algoritmos/convers_admin.xls','freguesias', 'C:\\Users\\CAlves\\Documents\\gowe\\dados_estat\\outros\\analfabetos.xls', 'Quadro', 2, 'analfabetos', 'C:/Users/CAlves/Documents/gowe/dados_estat/outros/analfabetos1.xls')