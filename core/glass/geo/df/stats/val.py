"""
Validation techniques for modelling results
"""

"""
def roc_analysis(movs, validation_sample, rst_score, lmt, w, output):
    def Extract_Presences(shape, driver):
	shp = ogr.GetDriverByName(driver).Open(shape, 0)
	lyr = shp.GetLayer()
	lst = []
	for feat in lyr:
	    geom = feat.GetGeometryRef()
	    lst.append(geom.ExportToWkb())
	return lst
    def MergePresences_Ausences(lst1, lst0, all_validation):
	outShp = ogr.GetDriverByName('ESRI Shapefile').CreateDataSource(all_validation)
	lyr = outShp.CreateLayer(str.split(all_validation, '/')[-1][:-4], geom_type=ogr.wkbPoint)
	lyr.CreateField(ogr.FieldDefn('phenom', ogr.OFTInteger))
	featureDefn = lyr.GetLayerDefn()
	for pnt in lst1:
	    feat = ogr.Feature(featureDefn)
	    point = ogr.CreateGeometryFromWkb(pnt)
	    feat.SetGeometry(point)
	    feat.SetField('phenom', 1)
	    lyr.CreateFeature(feat)
	for pnt in lst0:
	    feat = ogr.Feature(featureDefn)
	    #point = ogr.CreateGeometryFromWkb(pnt)
	    point = ogr.Geometry(ogr.wkbPoint)
	    point.AddPoint(pnt[0], pnt[1])	    
	    feat.SetGeometry(point)
	    feat.SetField('phenom', 0)
	    lyr.CreateFeature(feat)
	outShp.Destroy()
    def ExtractValueByPoint(pnt, rst):
	shp = ogr.GetDriverByName(GDAL_GetDriverName(pnt)).Open(pnt, 1)
	lyr = shp.GetLayer()
	lyr.CreateField(ogr.FieldDefn('susc', ogr.OFTReal))
	img = gdal.Open(rst)
	geo_transform = img.GetGeoTransform()
	band = img.GetRasterBand(1)
	for feat in lyr:
	    geom = feat.GetGeometryRef()
	    mx, my = geom.GetX(), geom.GetY()
	    px = int((mx - geo_transform[0]) / geo_transform[1])
	    py = int((my - geo_transform[3]) / geo_transform[5])
	    val_pix = band.ReadAsArray(px, py, 1, 1)
	    feat.SetField('susc', float(val_pix[0][0]))
	    lyr.SetFeature(feat)
	shp.Destroy()
    def GetScores2List(pnt):
	true = []; score = []
	shp = ogr.GetDriverByName(GDAL_GetDriverName(pnt)).Open(pnt, 0)
	lyr = shp.GetLayer()
	for i in lyr: 
	    true.append(int(i.GetField('phenom')))
	    score.append(int(i.GetField('susc')))
	shp.Destroy()
	dic = {
	    'true':true,
	    'score':score
	}
	return dic
    def PlotRocGraphic(actual, predictions):
	fpr, tpr, thresholds = roc_curve(actual, predictions)
	roc_auc = auc(fpr, tpr)
	fig = plt.figure()
	plt.plot(fpr, tpr, label='ROC curve (area = %0.2f)' % roc_auc)
	plt.plot([0, 1], [0, 1], 'k--')
	plt.xlim([0.0, 1.0])
	plt.ylim([0.0, 1.05])
	plt.xlabel('False Positive Rate')
	plt.ylabel('True Positive Rate')
	plt.title('Receiver operating characteristic example')
	plt.legend(loc="lower right")
	#plt.show()
	return fig
    # We have to had some ausences to the presences of the validation sample - Count the number of points that we will had to the occourrences
    nr_pnt = GDAL_GetFeatureCount(validation_sample, GDAL_GetDriverName(validation_sample))
    # Get Boundary Extent
    extent = GDAL_GetLayerExtent(lmt, GDAL_GetDriverName(lmt))
    # List Presences
    presences = Extract_Presences(validation_sample, GDAL_GetDriverName(validation_sample))
    # Generate Ausences
    ausences = CreateRandomPoints(movs, nr_pnt, extent)
    MergePresences_Ausences(presences, ausences, w + '/validation.shp')
    GDAL_DefineProjection(w + '/validation.shp', validation_sample)
    # Relate get raster values by scored raster
    ExtractValueByPoint(w + '/validation.shp', rst_score)
    dic_scores = GetScores2List(w + '/validation.shp')
    _auc = roc_auc_score(
        numpy.array(dic_scores['true']),
        numpy.array(dic_scores['score'])
    )
    graph = PlotRocGraphic(dic_scores['true'], dic_scores['score'])
    pp = PdfPages(output)
    pp.savefig(graph)
    pp.close()
"""    