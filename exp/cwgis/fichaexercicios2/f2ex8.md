# In QGIS/ArcGIS:

### Steps: 
1. Create a vector polygon based on the raster file (for the whole interested area).
2. Create a 200 m buffer for the water layer and dissolve it.
3. Create a difference layer between the vector polygon for the whole area and the buffer layer.
4. Merge the difference layer (id 0 in a table of attributes) with the buffer layer (id 1).
5. Convert the merge layer to a raster.
6. Using the raster calculator specify each condition for new raster values: 1,2,3,4.

![final result](https://github.com/MartaSolarz/Maps_and_GISWEB/blob/main/fichaexercicios2/image.png)
