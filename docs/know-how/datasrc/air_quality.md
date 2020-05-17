Air quality data sources
====================

## Some useful information in the web: ##

* https://medium.com/sentinel-hub/measuring-air-pollution-from-space-7492f5dad7bc 

## Data Sources list ##

##### URLS with compiled information: #####

* **Datasets provided by EarthData (NASA): https://earthdata.nasa.gov/earth-observation-data/near-real-time/hazards-and-disasters/air-quality

##### Layers List ##### 

* **Aerosol Index and UV Aerosol Index:** Aerosols absorb and scatter incoming sunlight, which reduces visibility and increases the optical depth. Aerosols have an effect on human health, weather and the climate. Sources of aerosols include pollution from factories, smoke from fires, dust from dust storms, sea salts, and volcanic ash and smog. Aerosols compromise human health when inhaled by people with asthma or other respiratory illnesses. Aerosols also have an affect on the weather and climate by cooling or warming the earth, helping or preventing clouds from forming. Satellite-derived Aerosol Index products are useful for identifying and tracking the long-range transport of volcanic ash from volcanic eruptions, smoke from wildfires or biomass burning events and dust from desert dust storms, even tracking over clouds and areas of snow and ice.    

    - OMI (AURA):  The Ozone Monitoring Instrument (OMI) AI indicates the presence of ultraviolet (UV)-absorbing particles in the air (aerosols) such as desert dust and soot particles in the atmosphere. The sensor resolution is 25 km, imagery resolution is 2 km, and the temporal resolution is daily.
        
        * https://omisips1.omisips.eosdis.nasa.gov/outgoing/OMAERUV/?C=M;O=D
    
    - OMPS (Suomi NPP): The Ozone Mapping and Profiler Suite (OMPS) AI indicates the presence of UV-absorbing particles in the air (aerosols) such as desert dust and soot particles in the atmosphere. The unitless range of the AI is from 0.00 to >=5.00, where 5.0 indicates heavy concentrations of aerosols that could reduce visibility or impact human health and this satisfies the needs of most users. However, the AI signal for pyrocumulonimbus (pyroCb) events, which are both dense and high in the atmosphere, can be much larger than 5.0. To provide better near real-time imagery for these high AI events, the pyroCb product with an upper AI limit of 50.0. The sensor resolution is 50 km, imagery resolution is 2 km, and the temporal resolution is daily.

        * https://omisips1.omisips.eosdis.nasa.gov/outgoing/OMPS/LANCE/NMTO3-L2-NRT/
    
    - Sentinel-5P: https://developers.google.com/earth-engine/datasets/tags/air-quality

* **Aerosol Optical Depth:** Aerosol Optical Depth (AOD) (or Aerosol Optical Thickness) indicates the level at which particles in the air (aerosols) prevent light from traveling through the atmosphere. Aerosols scatter and absorb incoming sunlight, which reduces visibility. From an observer on the ground, an AOD of less than 0.1 is “clean” - characteristic of clear blue sky, bright sun and maximum visibility. As AOD increases to 0.5, 1.0, and greater than 3.0, aerosols become so dense that sun is obscured. Sources of aerosols include pollution from factories, smoke from fires, dust from dust storms, sea salt, and volcanic ash and smog. Aerosols compromise human health when inhaled by people, particularly those with asthma or other respiratory illnesses. Aerosols also have an effect on the weather and climate by cooling or warming the earth, helping or preventing clouds from forming. Since aerosols are difficult to identify when they occur over different types of land surfaces and ocean surfaces, Worldview provides several different types of imagery layers to assist in the identification.

    - MODIS (Terra)

        * https://nrt3.modaps.eosdis.nasa.gov/archive/allData/61/MOD04_L2/Recent/

    - MODIS (Aqua)

        * https://nrt3.modaps.eosdis.nasa.gov/archive/allData/61/MYD04_L2/Recent/
    
    - MODIS (Terra/Aqua) - https://nrt3.modaps.eosdis.nasa.gov/archive/allData/61/MCDAODHD/Recent/

    - VIRS (Suomi NPP) - https://sips.ssec.wisc.edu/about/products/1/AERDB_L2_VIIRS_SNPP_NRT.html