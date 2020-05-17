"""
Sanitize values in a Excel table
"""


def split_attr(xls_path, sheet, interest_column, rule, out_path, overwrite=None):
	"""
	For a table like:

	ID |    ADRESS   | col_1 | ... | col_n
	1  | R. xxx, 145 |   x   | ... |   x
	2  | R. xxx, 146 |   x   | ... |   x
	3  | R. xxx, 147 |   x   | ... |   x
	4  | R. xxx, 148 |   x   | ... |   x
	5  | R. xxx, 149 |   x   | ... |   x

	And a rule == ', '

	Returns a table like:
	ID | ADRESS_1 | ADRESS_2 | col_1 | ... | col_n
	1  |  R. xxx  |    145   |   x   | ... |   x
	2  |  R. xxx  |    146   |   x   | ... |   x
	3  |  R. xxx  |    147   |   x   | ... |   x
	4  |  R. xxx  |    148   |   x   | ... |   x
	5  |  R. xxx  |    149   |   x   | ... |   x
	
	FID should be the first column
	"""
    
    import xlrd
    from glass.dct     import tbl_to_obj
    from glass.pys.oss import del_file
    from glass.dct  import dict_to_xls
    
	if overwrite:
		del_file(out_path)

	# XLS data to dict
	data = tbl_to_obj(
        xls_path, sheet=sheet, useFirstColAsIndex=True, output='dict'
    )

	# Split interest_column (attribute)
	for fid in data:
		for col in data[fid]:
			if str(col) == str(interest_column):
				str_lst = data[fid][col].split(rule)

		data[fid][interest_column+'_1'] = str_lst[0]
		data[fid][interest_column+'_2'] = str_lst[1] if len(str_lst) > 1 else ''

	# Write data in a new file
	dict_to_xls(data, out_path, sheet)


def replace_char(xls_path, interest_columns, charToReplace, _replacement, outXls, sheet=None):
	"""
	Replace charToReplace in the interest columns. charToReplace will be replaced by the value
	of the _replacement
	
	FID should be the first column
	
	TODO: Use Pandas insted
	"""
	
	import os
	from glass.dct        import tbl_to_obj
    from glass.dct     import dict_to_xls
    from glass.dp.xls.fld import col_name
	
	interest_columns = [interest_columns] if type(interest_columns) == str else \
		interest_columns if type(interest_columns) == list else None
	
	if not interest_columns:
		raise ValueError(
			'interest_columns should be a list or a string'
		)
	
	# XLS data to dict
	data = tbl_to_obj(
        xls_path, sheet_name=sheet, useFirstColAsIndex=True, output='dict'
    )
	
	# Get Order Values
	COLUMNS_BY_ORDER = col_name(xls_path, sheet_name=sheet)
	
	# Store and map changes
	changes = {}
	
	# Replace values
	for fid in data:
		for col in interest_columns:
			if charToReplace in data[fid][col]:
				repObj = data[fid][col].replace(charToReplace, _replacement)
				data[fid][col] = repObj
								
				if fid not in changes:
					changes[fid] = {col : data[fid][col]}
				else:
					changes[fid][col].update({col: data[fid][col]})
	
	# Write data
	# TODO: Write output file by order
	outsheet_name = sheet if sheet else os.path.splitext(os.path.basename(outXls))[0]
	dict_to_xls(data, outXls, outsheet_name)
	dict_to_xls(
		changes,
		os.path.splitext(outXls)[0] + '_meta.xls',
		outsheet_name
	)


def identify_cells_with_char(xls, sheetname, col_id, col_interest,
							interest_char, output):
	"""
	Identify the cells with a specific character in one column of interest
	
	Record these cells (ID and interest column) in a new file.
	"""
	
	import xlrd;          import xlwt
    from glass.dp.xls.fld import get_columns_position
	
	__xls = xlrd.open_workbook(xls)
	sheet = __xls.sheet_by_name(sheetname)
	
	cols_position = get_columns_position(sheet, [col_id, col_interest])
	
	out_xls = xlwt.Workbook()
	new_sheet = out_xls.add_sheet(sheetname)
	
	new_sheet.write(0, 0, col_id)
	new_sheet.write(0, 1, col_interest)
	
	Nrow = 1
	for row in range(1, sheet.nrows):
		val = sheet.cell(row, cols_position[col_interest]).value
		
		if interest_char in val:
			new_sheet.write(Nrow, 0, sheet.cell(row, cols_position[col_id]).value)
			new_sheet.write(Nrow, 1, val)
			Nrow+=1
	
	out_xls.save(output)

