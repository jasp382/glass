"""
Compile some information from a table
"""


import xlrd
import xlwt
import os


def frequencies_by_place(xls, entities_sheet, entities_id, entities_place,
                                 data_sheet, output, null=None, out_cols_basename=None,
                                 entities_filter=None, cols_exclusion=None):
    """
    Entities table:
    ID_Aluno | codigo_postal
    xxxxxxxx | xxxx-xxx
    xxxxxxxx | xxxx-xxx

    data_sheet:
    ID_Aluno | disciplina_1 | disciplina_2 | disciplina_n
    xxxxxxxx |    nota_1    |    xxxxxxx   |   xxxxxxx
    xxxxxxxx |    nota_2    |    xxxxxxx   |   xxxxxxx
    xxxxxxxx |    nota_3    |    xxxxxxx   |   xxxxxxx


    Output tables (one for each disciplina and other for the total)
                    |  nota_1  |  nota_2  |  nota_3  | Mean | Variance
    total           | NrAlunos | NrAlunos | NrAlunos |  x   |    y
    codigo_postal_1 | NrAlunos | NrAlunos | NrAlunos |  x   |    y
    codigo_postal_n | NrAlunos | NrAlunos | NrAlunos |  x   |    y

    In the entities_sheet and data_sheet, there must be only one referente
    for an entity (duplicated entities are not allowed)

    Filtering entities properties is possible
    """

    import numpy
    from decimal           import Decimal
    from glass.pyt.xls.fld  import get_columns_position
    from glass.pyt.xls.summ import list_unique_values_column
    from glass.pyt.xls.summ import count_values_column
    from glass.pyt.xls.summ import count_values_column_if_entity_exists
    from glass.pyt.xls.summ import count_values_column_by_entity_property

    """
    Aux method to estimate some generic statistics based on a "Dict Histogram"
    (total, mean and standard deviation)
    """
    def map_dict(histogram):
        if 'mean' in histogram.keys():
            del histogram['mean']

        if 'stdesviation' in histogram.keys():
            del histogram['stdesviation']

        if 'total' in histogram.keys():
            del histogram['total']

        # Get the total of entities
        histogram['total'] = sum(histogram.values())        
        # Get mean
        numerator = 0
        denominator = 0
        std_sample = []
        for v in histogram:
            if type(v) != str:
                numerator += Decimal(v) * Decimal(histogram[v])
                denominator += histogram[v]
                std_sample += [v for x in range(histogram[v])]

        if numerator and denominator:
            histogram['mean'] = numerator / Decimal(denominator)
            histogram['stdesviation'] = Decimal(numpy.std(std_sample))

        return histogram

    # Open xls file
    __xls_file = xlrd.open_workbook(xls, on_demand=True)

    # Map entities with location
    """
    d = {
        entitie_id : location
    }
    """
    if entities_filter:
        filters = entities_filter.split(';')
        filters_map = {}
        for flt in filters:
            col_filter, val_filter = flt.split('=')
            filters_map[col_filter] = val_filter

        interest_col = [entities_id, entities_place] + filters_map.keys()

    else:
        filters_map = 0
        interest_col = [entities_id, entities_place]

    __entities_sheet = __xls_file.sheet_by_name(entities_sheet)
    id_place_position = get_columns_position(
        __entities_sheet, interest_col
    )

    if entities_id not in id_place_position.keys():
        raise ValueError('Couldn\'t find the given column id')
    elif entities_place not in id_place_position.keys():
        raise ValueError('Couldn\'t find the position of the place id')

    entities_map = {}
    for row in range(1, __entities_sheet.nrows):
        __id = __entities_sheet.cell(
            row, id_place_position[entities_id]).value

        location = __entities_sheet.cell(
            row, id_place_position[entities_place]).value

        if filters_map:
            c = 0
            for col_filter in filters_map:
                __filter = __entities_sheet.cell(
                    row, id_place_position[col_filter]).value

                if __filter != val_filter:
                    c += 1
                    break

            if c:
                continue

        entities_map[__id] = location

    # Count Entities by value in each column
    """
    d = {
        col_1 : {
            total : {
                total   : total_count,
                value_1 : value_1_count,
                value_2 : value_2_count,
                value_n : value_n_count
            },
            location_1: {
                total   : total_count,
                value_1 : value_1_count,
                value_2 : value_2_count,
                value_n : value_n_count
            },
            location_2: {
                total   : total_count,
                value_1 : value_1_count,
                value_2 : value_2_count,
                value_n : value_n_count
            }
        },
        col_2 : {
            total : {
                total   : total_count,
                value_1 : value_1_count,
                value_2 : value_2_count,
                value_n : value_n_count
            },
            location_1: {
                total   : total_count,
                value_1 : value_1_count,
                value_2 : value_2_count,
                value_n : value_n_count
            },
            location_2: {
                total   : total_count,
                value_1 : value_1_count,
                value_2 : value_2_count,
                value_n : value_n_count
            }
        },
        col_n : {
            ...
        }
    }
    """
    data_sheet = __xls_file.sheet_by_name(data_sheet)
    data = {}

    cols_exclusion = cols_exclusion if type(cols_exclusion) == list else \
        [cols_exclusion] if type(cols_exclusion) == str else 0

    for col in range(1, data_sheet.ncols):
        column_name = data_sheet.cell(0, col).value
        if cols_exclusion:
            if column_name in cols_exclusion:
                continue
        # List unique values
        values = list_unique_values_column(data_sheet, col)

        # Del NoData identifier if defined
        if null or null == 0:
            if null in values:
                values.remove(null)

        # Count occourences of a value in that column
        val_count = count_values_column_if_entity_exists(
            data_sheet, col, entities_map.keys(), values
        )

        for v in values:
            if v not in val_count:
                val_count[v] = 0

        data[column_name] = {'total' : map_dict(val_count)}

        # Do the same for each location
        locations = list(set(entities_map.values()))

        for place in locations:
            val_count = count_values_column_by_entity_property(
                data_sheet, col, place, entities_map,
                values
            )

            for v in values:
                if v not in val_count:
                    val_count[v] = 0

            data[column_name].update({place : map_dict(val_count)})

    """
    Update data dict with one combination of all keys/values data
    d.update({
        general : {
            total : {
                total   : total_count,
                value_1 : value_1_count,
                value_2 : value_2_count,
                value_n : value_n_count
            },
            location_1: {
                total   : total_count,
                value_1 : value_1_count,
                value_2 : value_2_count,
                value_n : value_n_count
            },
            location_2: {
                total   : total_count,
                value_1 : value_1_count,
                value_2 : value_2_count,
                value_n : value_n_count
            }
        }
    })
    """
    general = {}
    for col_sheet in data:
        for k in data[col_sheet]:
            if k not in general:
                general[k] = {}
                for _k in data[col_sheet][k]:
                    general[k][_k] = data[col_sheet][k][_k]
            else:
                for _k in data[col_sheet][k]:
                    if _k in general[k]:
                        general[k][_k] += data[col_sheet][k][_k]
                    else:
                        general[k][_k] = data[col_sheet][k][_k]
    data['general'] = general

    for __dict in data['general']:
        with_stats = map_dict(data['general'][__dict])
        data['general'][__dict] = with_stats


    # Write data in a new xls_file
    out_xls = xlwt.Workbook()
    for col_sheet in data:
        new_sheet = out_xls.add_sheet(col_sheet)

        if out_cols_basename:
            cols_basename = ['{b}_{_k}'.format(
                b=out_cols_basename, _k=str(k)
                ) for k in data[col_sheet]['total'].keys()]

        else:
            cols_basename = data[col_sheet]['total'].keys()

        cols_name = data[col_sheet]['total'].keys()

        cols_basename.sort()
        cols_name.sort()

        # Write columns names
        for c in range(len(cols_name)):
            new_sheet.write(0, c+1, cols_basename[c])

        # Write lines
        lnh = 1
        lines_name = data[col_sheet].keys()
        lines_name.sort()
        for line in lines_name:
            # Write line name
            new_sheet.write(lnh, 0, line)

            # Write counting data
            for cln in range(len(cols_name)):
                if cols_name[cln] in data[col_sheet][line].keys():
                    new_sheet.write(
                        lnh, cln + 1, data[col_sheet][line][cols_name[cln]]
                    )

            lnh += 1

    out_xls.save(output)

    __xls_file.release_resources()
    del __xls_file


def run_freq_by_place_by_sheet(xls, sheets_map, output_fld, null=None,
                               out_cols_basename=None, entities_filter=None,
                               cols_exclusion=None):
    """
    Execute frequencies_by_place for each group of entities and data sheets
    
    sheets_map should be something like this:
    sheets_map = {
        'entities_sheet_name' : {
            fid   : 'entities_field_id_name',
            place : 'entities_place_field_name',
            data  : 'data_sheet_name'
        },
        ...
    }
    """
    
    for entity_sheet in sheets_map:
        frequencies_by_place(
            xls, entity_sheet, sheets_map[entity_sheet]['fid'],
            sheets_map[entity_sheet]['place'],
            sheets_map[entity_sheet]['data'],
            output,
            null=null, out_cols_basename=out_cols_basename,
            entities_filter=entities_filter,
            cols_exclusion=cols_exclusion
        )


def frequencies_by_entity_attr(xls, entities_sheet, entities_id, attr_sheet,
                            interest_values, output, entities_filter=None,
                            attr_exclusion=None):
    """
    Count entities with a number of attributes with a set of specific values

    Example:
    specific_values = A, S
    Entities table:
    entity_id | some_data
    xxxxxxxx  | xxxx-xxx
    xxxxxxxx  | xxxx-xxx

    attributes_sheet:
    From tables as:
    entity | attr_1 | attr_2 | ... | attr_n
       0   |    S   |   S    | ... |   S
       1   |    A   |   B    | ... |   S
       2   |    B   |   B    | ... |   A
       3   |    S   |   A    | ... |   S
       4   |    A   |   S    | ... |   B

    We came to the following result:
    values  | entities_count | attribute_count
      S;A   |        2       |        3
      S;A   |        2       |        2
      S;A   |        1       |        1

    Filtering entities properties is possible... Many could be used...
    When many fields are used, the AND operator logic will be applied

    E.g of application:
    Number of students with a number of negatives
    """
    
    from glass.pyt.xls.fld import get_columns_position

    # Open file
    __xls = xlrd.open_workbook(xls, on_demand=True)

    # Map entities
    if entities_filter:
        filters = entities_filter.split(';')
        filters_map = {}
        for flt in filters:
            col_filter, val_filter = flt.split('=')
            filters_map[col_filter] = val_filter

        interest_col = [entities_id] + filters_map.keys()

    else:
        filters_map = 0
        interest_col = entities_id

    __entities_sheet = __xls.sheet_by_name(entities_sheet)
    cols_position = get_columns_position(__entities_sheet, interest_col)

    if entities_id not in cols_position:
        raise ValueError('Couldn\'t find the given column id')

    entities_map = {}
    for row in range(1, __entities_sheet.nrows):
        __id = __entities_sheet.cell(row, cols_position[entities_id]).value

        if filters_map:
            c = 0
            for col_filter in filters_map:
                __filter = __entities_sheet.cell(
                    row, cols_position[col_filter]).value

                if __filter != filters_map[col_filter]:
                    c += 1
                    break

            if c:
                continue

        entities_map[__id] = 0

    # Count occurences of the specific/interes values by entitie
    data_sheet = __xls.sheet_by_name(attr_sheet)


    interest_values = interest_values if type(interest_values) == list else \
        [interest_values] if type(interest_values) == str else 0

    if not interest_values: raise ValueError(
        'interest_values should be a list or string')

    for col in range(1, data_sheet.ncols):
        column_name = data_sheet.cell(0, col).value
        if attr_exclusion and type(attr_exclusion) == list:
            if column_name in attr_exclusion:
                continue

        for row in range(1, data_sheet.nrows):
            __id = data_sheet.cell(row, 0).value
            value = data_sheet.cell(row, col).value

            if value in interest_values:
                if __id in entities_map:
                    entities_map[__id] += 1

    # Count the number entities with the same number of occurences of the
    # interest/specific values
    occurence_count = entities_map.values()
    occurence_unique = list(set(occurence_count))

    entities_countv = {}
    for countv in occurence_unique:
        entities_count = occurence_count.count(countv)
        entities_countv[entities_count] = countv

    # Write output
    out_xls = xlwt.Workbook()
    new_sheet = out_xls.add_sheet(os.path.splitext(os.path.basename(output))[0])

    # colums
    c = ['values', 'entities_number', 'values_occurences']
    for i in range(len(c)):
        new_sheet.write(0, i, c[i])

    # values
    l = 1
    for i in entities_countv:
        new_sheet.write(l, 0, ';'.join([str(x) for x in interest_values]))
        new_sheet.write(l, 1, i)
        new_sheet.write(l, 2, entities_countv[i])
        l+=1

    out_xls.save(output)

    __xls.release_resources()
    del __xls


def frequencies_table(xls, data_sheet, output,
                           entities_sheet=None, entities_id=None,
                           entities_filter=None, values_filter=None):
    """
    Count values occurences in each attribute column

    input table:
    entity | attr_1 | attr_2 | ... | attr_n
       0   |   a    |   b    | ... |   a
       1   |   b    |   c    | ... |   b
       2   |   b    |   c    | ... |   c
       3   |   a    |   f    | ... |   d
       4   |   c    |   a    | ... |   f

    output table:
           | a | b | c | d | f |
    attr_1 | 2 | 2 | 1 | 0 | 0 |
    attr_2 | 1 | 1 | 2 | 0 | 1 |
    attr_n | 1 | 1 | 1 | 1 | 1 |

    It is possible filter entities and attribute values
    """
    
    from glass.pyt.xls.fld  import get_columns_position
    from glass.pyt.xls.summ import count_values_column
    from glass.pyt.xls.summ import count_values_column_if_entity_exists

    # Open file
    __xls = xlrd.open_workbook(xls, on_demand=True)

    if entities_sheet and entities_id and entities_filter:
        filters = entities_filter.split(';')
        filters_map = {}
        for flt in filters:
            col_filter, val_filter = flt.split('=')
            filters_map[col_filter] = val_filter

        __entities_sheet = __xls.sheet_by_name(entities_sheet)

        int_col = [entities_id] + filters_map.keys()
        cols_position = get_columns_position(
            __entities_sheet, int_col
        )

        entities_map = []
        for row in range(1, __entities_sheet.nrows):
            __id = __entities_sheet.cell(
                row, cols_position[entities_id]).value

            c = 0
            for col_filter in filters_map:
                __filter = __entities_sheet.cell(
                    row, cols_position[col_filter]).value

                if __filter != filters_map[col_filter]:
                    c += 1
                    break

            if c:
                continue

            entities_map.append(__id)

    else:
        entities_map = None

    attr_sheet = __xls.sheet_by_name(data_sheet)

    data = {}
    registed_values = []
    values_filter = values_filter if type(values_filter) == list else \
        [values_filter] if type(values_filter) == str else None

    for col in range(1, attr_sheet.ncols):
        col_name = attr_sheet.cell(0, col).value

        if not entities_map:
            values_count = count_values_column(attr_sheet, col, values_filter)
        else:
            values_count = count_values_column_if_entity_exists(
                attr_sheet, col, entities_map, values_filter
            )

        registed_values.extend(values_count.keys())

        data[col_name] = values_count

    registed_values = list(set(registed_values))

    # Write output
    out_xls = xlwt.Workbook()
    new_sheet = out_xls.add_sheet(
        os.path.splitext(os.path.basename(output))[0]
    )

    # columns
    for i in range(len(registed_values)):
        new_sheet.write(0, i+1, registed_values[i])

    # Write values
    r=1
    for row in data:
        new_sheet.write(r, 0, row)
        for col in range(len(registed_values)):
            if registed_values[col] in data[row]:
                new_sheet.write(r, col+1, data[row][registed_values[col]])
        r += 1

    out_xls.save(output)

    __xls.release_resources()
    del __xls

