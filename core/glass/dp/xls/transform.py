"""
Transform tables using xlrd and xlwt
"""

import xlrd
import xlwt
import os


def groups_to_lines(xls_data, xls_sheet,
                    group_column, name_colum,
                    cls_column, interest_column,
                    column_labels, xls_output):
    """
    Table:
      | group | label | class | interest
    0 |  AT   | ATLA1 |   0   |    50
    1 |  AT   | ATLA2 |   1   |    70
    2 |  AT   | ATLA3 |   2   |    80
    3 |  AT   | ATLA4 |   2   |    90
    4 |  AT   | ATLA5 |   2   |    10
    5 |  PT   | PTLA1 |   0   |    20
    6 |  PT   | PTLA2 |   2   |    30
    7 |  PT   | PTLA3 |   2   |    40
    8 |  PT   | PTLA4 |   2   |    52
    9 |  PT   | PTLA5 |   1   |    61
    10|  PT   | PTLA6 |   2   |    12

    Will be converted to a python object such as:
    table = {
        AT: {
            group_name        : ATLA1,
            group_value       : interest of line 0,
            master_unit_value : interest of line 1,
            units_value       : [interest of line 2, 3, 4]
        },
        PT: {
            group_name        : PTLA1,
            group_value       : interest of line 5,
            master_unit_value : interest of line 9,
            units_value       : [interest of line 6, 7, 8, 10],
        }
    }

    Using this python object, the output table will be write as:

      | GROUP_NAME | GROUP_VALUE | MASTER_UNIT_VALUE | UNITS_1 | ... | UNITS_N
    0 |    ATLA1   |     50      |        70         |    80   | ... |   10
    1 |    PTLA1   |     20      |        61         |    30   | ... |   12
    """
    
    from glass.dp.xls.fld import get_columns_position

    interest_columns = [group_column, cls_column, name_colum, interest_column]

    # Open input
    __xls_data = xlrd.open_workbook(xls_data)
    sheet = __xls_data.sheet_by_name(xls_sheet)

    # Get columns position
    """
    cols_position = {
        column_name: position_index, ...
    }
    """
    cols_position = get_columns_position(sheet, interest_columns)

    if interest_column not in cols_position.keys():
        return "Interest column not encountered in data file"

    # Get data of spreadsheet for the interest column
    """
    data = {
        group: {
            group_name        : name,
            group_value       : value,
            master_unit_value : value,
            units_value       : [value_unit1, ..., value_unitn]
        },
    }
    """
    data = {}
    groups_name = {}
    for row in range(1, sheet.nrows):
        group_id = str(sheet.cell(row, cols_position[group_column]).value)

        row_class = int(sheet.cell(row, cols_position[cls_column]).value)

        row_name = sheet.cell(row, cols_position[name_colum]).value

        row_value = sheet.cell(row, cols_position[interest_column]).value

        if group_id not in data.keys():
            groups_name[row_name] = group_id
            if row_class == 0:
                data[group_id] = {
                    'group_name': row_name,
                    'group_value': row_value,
                    'units_value': []
                }

            elif row_class == 1:
                data[group_id] = {
                    'master_unit_value': row_value,
                    'units_value': []
                }

            elif row_class == 2:
                data[group_id] = {
                    'units_value': []
                }

            else:
                return 'Class value not recognized'

        else:
            if row_class == 0:
                groups_name[row_name] = group_id
                data[group_id].update({
                    'group_name': row_name,
                    'group_value': row_value
                })

            elif row_class == 1:
                data[group_id].update({
                    'master_unit_value': row_value,
                })

            elif row_class == 2:
                data[group_id]['units_value'].append(row_value)

            else:
                return 'Class value not recognized'

    # Write Output
    out_xls = xlwt.Workbook()
    out_sheet = out_xls.add_sheet(interest_column)

    # Write first line
    col_to_write = 0
    for k in data:
        c = len(data[k]['units_value'])
        if c > col_to_write:
            col_to_write = c
    for i in range(col_to_write):
        out_sheet.write(0, i+3, i+1)

    # Write second line
    for i in range(len(column_labels)):
        out_sheet.write(1, i, column_labels[i])

    aux_titles = ['Min', 'Max', 'EU28_Average']
    for i in range(len(aux_titles)):
        out_sheet.write(1, col_to_write + 3 + i, aux_titles[i])

    # Organize groups alphabetically based on names
    grp_names = sorted(groups_name.keys())
    groups = []
    for name in grp_names:
        groups.append(groups_name[name])
    # Write data
    l = []
    for k in range(len(groups)):
        out_sheet.write(k+2, 0, data[groups[k]]['group_name'])

        out_sheet.write(k+2, 1, data[groups[k]]['group_value'])

        if 'master_unit_value' not in data[groups[k]]:
            out_sheet.write(k+2, 2, data[groups[k]]['group_value'])
            master_unit_key = 'group_value'
        else:
            out_sheet.write(k+2, 2, data[groups[k]]['master_unit_value'])
            master_unit_key = 'master_unit_value'

        for i in range(len(data[groups[k]]['units_value'])):
            out_sheet.write(k+2, i+3, data[groups[k]]['units_value'][i])

        t = data[groups[k]]['units_value'] + [data[groups[k]][master_unit_key]]

        l += t

    # Write global min and max
    n_l = []
    for i in l:
        if type(i) == type(10) or type(i) == type(10.0):
            n_l.append(i)
    out_sheet.write(2, col_to_write + 3, min(n_l))
    out_sheet.write(2, col_to_write + 4, max(n_l))
    out_xls.save(xls_output)


def groups_to_lines_by_refs(data, xls_sheet, group_column,
                            name_colum, cls_column,
                            column_labels,
                            relations_table, workspace):
    """
    Execute method transpose_by_groups for any reference in relations table
    
    Relations table should be like this:
      | id | name | column
    0 | 01 | 'n1' |   UN
    1 | 02 | 'n2' |   UH
    
    This table should have only one sheet.
    
    Column field corresponds to the interest_column in the transpose_groups
    method.
    
    The id and name fields will be used to identified each table generated
    by the transpose_by_groups method.
    E.g. Generated files using this example:
    0 - 01_n1.xls
    1 - 02_n2.xls
    """
    
    xls_relations = xlrd.open_workbook(relations_table)
    all_sheets = xls_relations.sheet_names()
    __sheet = xls_relations.sheet_by_name(all_sheets[0])
    
    dic_relations = {
        __sheet.cell(i, 0).value : {
            'name'   : __sheet.cell(i, 1).value,
            'column' : __sheet.cell(i, 2).value
        } for i in range(1, __sheet.nrows)
    }
    
    for k in dic_relations:
        groups_to_lines(
            data, xls_sheet, group_column, name_colum, cls_column,
            dic_relations[k]['column'], column_labels,
            os.path.join(
                workspace, '{}_{}.xls'.format(
                    k, dic_relations[k]['name']
                )
            )
        )


def year_to_col_by_attr(data_file, data_spreadsheet,
                                          field_id,
                                          fields_to_mantain,
                                          field_year,
                                          output_file):
    """
    Transpose a table by attribute and year

    For a given table such as:

       | group |  fid  | label | year | attribute_x | attribute_y
    0  |  AT   | AT_01 | ATLA1 | 2000 |    val_x    |   val_y
    1  |  AT   | AT_01 | ATLA1 | 2001 |    val_x    |   val_y
    2  |  AT   | AT_02 | ATLA2 | 2000 |    val_x    |   val_y
    3  |  AT   | AT_02 | ATLA2 | 2001 |    val_x    |   val_y
    4  |  AT   | AT_03 | ATLA3 | 2000 |    val_x    |   val_y
    5  |  AT   | AT_03 | ATLA3 | 2001 |    val_x    |   val_y
    6  |  AT   | AT_04 | ATLA4 | 2000 |    val_x    |   val_y
    7  |  AT   | AT_04 | ATLA4 | 2001 |    val_x    |   val_y
    8  |  PT   | PT_01 | PTLA1 | 2000 |    val_x    |   val_y
    9  |  PT   | PT_01 | PTLA1 | 2001 |    val_x    |   val_y
    10 |  PT   | PT_02 | PTLA2 | 2000 |    val_x    |   val_y
    11 |  PT   | PT_02 | PTLA2 | 2001 |    val_x    |   val_y
    12 |  PT   | PT_03 | PTLA3 | 2000 |    val_x    |   val_y
    13 |  PT   | PT_03 | PTLA3 | 2001 |    val_x    |   val_y

    This method will generate one table (spreadsheet) for each attribute:

    Table attribute_x
      | group |  fid  | label |  2000 | 2001
    0 |  AT   | AT_01 | ATLA1 | val_x | val_x
    1 |  AT   | AT_02 | ATLA2 | val_x | val_x
    2 |  AT   | AT_03 | ATLA3 | val_x | val_x
    3 |  AT   | AT_04 | ATLA4 | val_x | val_x
    4 |  PT   | PT_01 | PTLA1 | val_x | val_x
    5 |  PT   | PT_02 | PTLA2 | val_x | val_x
    6 |  PT   | PT_03 | PTLA3 | val_x | val_x

    Table attribute_y
      | group |  fid  | label |  2000 | 2001
    0 |  AT   | AT_01 | ATLA1 | val_y | val_y
    1 |  AT   | AT_02 | ATLA2 | val_y | val_y
    2 |  AT   | AT_03 | ATLA3 | val_y | val_y
    3 |  AT   | AT_04 | ATLA4 | val_y | val_y
    4 |  PT   | PT_01 | PTLA1 | val_y | val_y
    5 |  PT   | PT_02 | PTLA2 | val_y | val_y
    6 |  PT   | PT_03 | PTLA3 | val_y | val_y
    """

    from glass.dp.xls.fld  import get_columns_position
    from glass.dp.xls.fld  import get_columns_position_outside_options
    from glass.dp.xls.summ import list_unique_values_column
    from glass.dp.xls.fm   import get_unit_attributes

    # Open input
    xls_data = xlrd.open_workbook(data_file)
    sheet = xls_data.sheet_by_name(data_spreadsheet)

    # Get interest columns position
    interest_position = get_columns_position(sheet, fields_to_mantain)

    # Get year position
    year_position = get_columns_position(sheet, [field_year])

    # Get id position
    id_position = get_columns_position(sheet, [field_id])

    # Get attributes columns position - indicators
    attributes_position = get_columns_position_outside_options(
        sheet, fields_to_mantain + [field_year, field_id]
    )

    # List years
    years = list_unique_values_column(sheet, year_position[field_year])

    # List entities
    units = list_unique_values_column(sheet, id_position[field_id])
    units_atributtes = get_unit_attributes(
        sheet, id_position[field_id], interest_position
    )

    # add years to data dict
    for unit in units_atributtes:
        for year in years:
            units_atributtes[unit][year] = {}
    # Get values by year for each unit
    for line in range(1, sheet.nrows):
        __year = sheet.cell(line, year_position[field_year]).value
        __id = sheet.cell(line, id_position[field_id]).value
        if __id not in units_atributtes.keys():
            continue

        for indicator in attributes_position:
            if __year not in years:
                continue
            units_atributtes[__id][__year][indicator] = sheet.cell(
                line, attributes_position[indicator]).value

    # Write output
    out_xls = xlwt.Workbook()
    # for each attribute/indicator column
    for indicator in attributes_position:
        # Create new sheet
        out_sheet = out_xls.add_sheet(indicator)
        # Write columns
        out_sheet.write(0, 0, field_id)
        c = 1
        for field in interest_position:
            out_sheet.write(0, c, field)
            c += 1
        for year in years:
            out_sheet.write(0, c, year)
            c += 1
        # Write real data
        lnh = 1
        for unit in units_atributtes:
            out_sheet.write(lnh, 0, unit)
            col = 1
            for field in interest_position:
                out_sheet.write(
                    lnh,
                    col,
                    units_atributtes[unit][field]
                )
                col += 1

            for year in years:
                out_sheet.write(
                    lnh,
                    col,
                    units_atributtes[unit][year][indicator]
                )
                col += 1
            lnh += 1
    out_xls.save(output_file)


def transpose_groups_in_sheets(excel, datasheet, group, _id, output):
    """
    For an Input Table like:
      | group | id | variable_1 | variable_2
    0 |   A   |  1 |   V1_A1    |   V2_A1
    1 |   A   |  2 |   V1_A2    |   V2_A2
    2 |   B   |  1 |   V1_B1    |   V2_B1
    3 |   B   |  2 |   V1_B2    |   V2_B2
    
    This method will generate one table for each group:
    * GROUP A
      | variables  | var_code | id1_value | id2_value
    0 | variable_1 |          |   V1_A1   |   V1_A2
    1 | variable_2 |          |   V2_A1   |   V2_A2
    
    * GROUP B
      | variables  | var_code | id1_value | id2_value
    0 | variable_1 |          |   V1_B1   |   V1_B2
    1 | variable_2 |          |   V2_B1   |   V2_B2
    """
    
    import xlrd;          import xlwt
    from glass.dp.xls.fld import get_columns_position
    from glass.dp.xls.fld import get_columns_position_outside_options
    
    # Get data from excel
    xls = xlrd.open_workbook(excel)
    sdata = xls.sheet_by_name(datasheet)
    
    # Get data by group and variable
    """
    data = {
        groupA : {
            varA : [val_1, ..., val_n],
            varB : [val_1, ..., val_n]
        },
        ...
        groupN: {
            varA : [val_1, ..., val_n],
            varB : [val_1, ..., val_n]
        }
    }
    """
    position_grp_id = get_columns_position(sdata, [group, _id])
    position_var = get_columns_position_outside_options(sdata, [group, _id])
    # To mantain the writting order of the variables (first column
    # should be first line.)
    var_cols = position_var.values()
    var_cols.sort()
    for i in range(len(var_cols)):
        for col in position_var:
            if var_cols[i] == position_var[col]:
                var_cols[i] = col
    # The columns names will be written in the correct order
    
    groupsChild = {}
    for row in range(1, sdata.nrows):
        grp = sdata.cell(row, position_grp_id[group]).value
        
        if grp not in groupsChild:
            groupsChild[grp] = {}
        
        entity = sdata.cell(row, position_grp_id[_id]).value
        
        for col in var_cols:
            value = sdata.cell(row, position_var[col]).value
            
            if not col in groupsChild[grp]:
                groupsChild[grp][col] = [value]
            
            else:
                groupsChild[grp][col].append(value)
    
    # Write output - one table for each group
    out_xls = xlwt.Workbook()
    
    for grp in groupsChild:
        grp_sheet = out_xls.add_sheet(grp)
        
        # Write first line
        titles = ['MIN', 'Max',
                  'component/area of concern/dimension']
        
        for i in range(len(groupsChild[grp][groupsChild[grp].keys()[0]])):
            titles.append(i+1)
        
        for i in range(len(titles)):
            grp_sheet.write(0, i, titles[i])
        
        # Write Values
        for i in range(len(var_cols)): # each iteration is a new line
            # Write Variable name
            grp_sheet.write(i+1, 2, var_cols[i])
            
            # Write entities values
            for e in range(len(groupsChild[grp][var_cols[i]])):
                grp_sheet.write(i+1, 2 + e + 1,
                                groupsChild[grp][var_cols[i]][e])
            
            # Write MIN and MAX
            grp_sheet.write(i+1, 0, min(groupsChild[grp][var_cols[i]]))
            grp_sheet.write(i+1, 1, max(groupsChild[grp][var_cols[i]]))
    
    out_xls.save(output)
    
    return output


def split_col_by_year(dataFile, sheetName, codeCol, yearCol, out_file):
    """
    For a table:
    
       | code | year | U | LTU
    0  |  PT1 | 2000 | x |  x
    1  |  PT2 | 2000 | x |  x
    2  |  PT3 | 2000 | x |  x
    3  |  PT1 | 2001 | x |  x
    4  |  PT2 | 2001 | x |  x
    5  |  PT3 | 2001 | x |  x
    6  |  PT1 | 2002 | x |  x
    7  |  PT2 | 2002 | x |  x
    8  |  PT3 | 2002 | x |  x
    9  |  PT1 | 2003 | x |  x
    10 |  PT2 | 2003 | x |  x
    11 |  PT3 | 2003 | x |  x
    12 |  PT1 | 2004 | x |  x
    13 |  PT2 | 2004 | x |  x
    14 |  PT3 | 2004 | x |  x
    
    The output will be:
    
       | code | U_2000 | U_2001 | ... | LTU_2000 | ... | LTU_2004
    0  | PT1  |    x   |    x   | ... |    x     | ... |    x
    1  | PT2  |    x   |    x   | ... |    x     | ... |    x
    2  | PT3  |    x   |    x   | ... |    x     | ... |    x
    
    Outfile should be a CSV.
    """
    
    import codecs
    from glass.dp.xls.fld  import get_columns_position, get_columns_position_outside_options
    from glass.dp.xls.summ import list_unique_values_column
    
    # Open input
    xls = xlrd.open_workbook(dataFile)
    sheet = xls.sheet_by_name(sheetName)
    
    # Get code and year columns position
    codePos_yearPos = get_columns_position(sheet, [codeCol, yearCol])
    codePos, yearPos = (codePos_yearPos[codeCol], codePos_yearPos[yearCol])
    
    # Get variable positions
    varPos = get_columns_position_outside_options(sheet, [codeCol, yearCol])
    
    # Get data
    data  = {}
    VARS  = []
    YEARS = []
    for row in range(1, sheet.nrows):
        entity = sheet.cell(row, codePos).value
        year   = int(sheet.cell(row, yearPos).value)
        
        if year not in YEARS:
            YEARS.append(year)
        
        if entity not in data:
            data[entity] = {}
        
        if year not in data[entity]:
            data[entity][year] = {}
        
        for var in varPos:
            if var not in data[entity][year]:
                data[entity][year][var] = sheet.cell(row, varPos[var]).value
            
            else:
                print('Variable is already there for that entity and year')
            
            if var not in VARS:
                VARS.append(var)
    
    VARS.sort()
    YEARS.sort()
    
    
    with codecs.open(out_file, mode='w', encoding='utf-8') as f:
        # Write titles
        f.write(codeCol + '\t')
        
        for var in VARS:
            for year in YEARS:
                f.write('{v}_{y}\t'.format(v=str(var), y=str(year)))
        
        f.write('\n')
        
        # Write real data
        for entity in data:
            f.write(entity + '\t')
            
            for var in VARS:
                for year in YEARS:
                    if year in data[entity]:
                        f.write('{}\t'.format(str(data[entity][year][var])))
                    else:
                        f.write('\t')
            
            f.write('\n')
        
        f.close()
    
    """
    TODO: Add excel option
    # Write data
    out_xls = xlwt.Workbook()
    out_sheet = out_xls.add_sheet(sheetName)
    
    # Write titles
    out_sheet.write(0, 0, codeCol)
        
    c=1
    for var in VARS:
        for year in YEARS:
            print c
            out_sheet.write(
                0, c, '{v}_{y}'.format(v=str(var), y=str(year))
            )
                
            c += 1
    
    # Write real data
    row = 1
    for entity in data:
        out_sheet.write(row, 0, entity)
        
        col = 1
        for var in VARS:
            for year in YEARS:
                out_sheet(
                    row, col, data[entity][year][var]
                )
                
                col += 1
        row += 1
    
    out_xls.save(out_file)
    """

