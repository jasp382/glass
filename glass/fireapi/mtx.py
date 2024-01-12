"""
Interact with the matrix.dec.uc.pt platform
"""

import json as js
import requests as rqst


def get_payload(data, ref_alt, cutoffval, mdlparam):
    """
    Produce JSON payload to request solution 
    to the matrix platform
    """

    return {
        "action": "exec_alg",
        "algorithms": {
            "madm": {
                "electre_tri": {
                    "elements": {
                        "global": {
                            "impact_matrix" : data,
                            "referenc_alternatives" : ref_alt,
                            "normalization" : "diff_ratio",
                            "cutoff_level" : cutoffval
                        },
                        "attr": mdlparam
                    }
                }
            }
        }
    }


def run_electretri(payload):
    """
    Run Electre TRI
    """

    url = 'http://aserver.dec.uc.pt:8081/'

    out = None

    try:
        r = rqst.post(url, data=js.dumps(payload))
    
    except:
        out = {"status" : -1}
    
    if not out:
        try:
            _r = r.json()

            out = {
                "status" : 1,
                "json"   : _r,
                "http"   : r.status_code
            }
        
        except:
            out = {
                "status" : 0,
                "http"   : r.status_code,
                "json"   : None
            }
    
    return out



def format_results(data,output_path):

    import xlsxwriter
    import pandas as pd

    results = data['results']

    df = pd.DataFrame.from_dict(results, orient = 'index')

    names = ['Afetação pessimista', 'Afetação otimista', 'Matriz das alternativas de referência', 'Matriz de concordância global impacto/referência', 'Matriz de concordância global referência/impacto', 'Matriz de credibilidade impacto/referência', 'Matriz de credibilidade referência/impacto', 'res_electre_tri_outrank_matr_imp_ref', 'res_electre_tri_outrank_matr_ref_imp', 'Número de reajustes dos limiares de indiferença', 'Número de reajustes dos limiares de veto', 'Pesos originais', 'Pesos normalizados à unidade']

    # Delete unnecessary colummns
    df.drop( ['position','type','group_title_type','shade_scope','row_title_type','col_title_type','limits','display_value','display_shade','shade_type'], axis = 1, inplace=True)

    # Create subsets from the original dataframe for easier manipulation
    df_alt = df.loc[ ['res_electre_tri_afect_pess','res_electre_tri_afect_opt' ], 'vector' ]
    df_matrix = df.loc[ ~df.index.isin(['res_electre_tri_afect_pess','res_electre_tri_afect_opt' ])   , 'matrix' ]

    # Create an Excel file
    workbook = xlsxwriter.Workbook(output_path)
    alternatives_sheet = workbook.add_worksheet(name='Alternativas')
    matrices_sheet = workbook.add_worksheet(name='Matrizes')


    # Write the Alternatives labels and vectores
    for col, data in enumerate( df_alt.iloc[:]):
        alternatives_sheet.write_string(0, col, names[col])
        alternatives_sheet.write_column(1, col, data)

    # Write the remaining matrices
    row = 0
    for line in range( len(df_matrix) ):
        matrices_sheet.write_string(row, 0, names[line + 2])

        num_cols = len(df_matrix.iloc[line])

        if isinstance( df_matrix.iloc[line][0] ,list):

            #write labels
            for col in range(num_cols):
                matrices_sheet.write_string(row,col+1,f'A{col+1}')

            row +=1

            #run through the matrix
            for col, data in enumerate( df_matrix.iloc[line] ):
                    matrices_sheet.write_column(row, col+1, data)


            row += len(df_matrix.iloc[line][0]) + 1


        else:

            #write labels
            for col in range(num_cols):
                matrices_sheet.write_string(row,col+1,f'ATT{col+1}')

            row +=1

            #run through the matrix
            for col, data in enumerate( df_matrix.iloc[line] ):
                    matrices_sheet.write_number(row, col+1, data)
            
            row += 2


    workbook.close()

