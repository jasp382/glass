"""
Likelihood Ratio Method Implementation
"""

import os


def grass_lri(events, vars, refrst, out, all_lri=None, eventsbyvar=None):
    """
    Likelihood Ratio Method using GRASS GIS

    vars: dict = {
        var_slug : path_to_raster,
        var_slug : {
            path_to_var : weight, ...
        }, ...
    }
    """

    from glass.prop.df  import is_rst
    from glass.wenv.grs import grass_session
    from glass.pys.oss  import fprop
    from glass.pys.tm   import now_as_str
    from glass.prop.rst import count_cells

    ws, loc = os.path.dirname(out), now_as_str(utc=True)

    # Start GRASS GIS Session
    gb = grass_session(ws, loc=loc, srs=refrst)

    from glass.it.rst        import rst_to_grs, grs_to_rst
    from glass.it.shp        import shp_to_grs
    from glass.dtt.rst.torst import grsshp_to_grsrst
    from glass.rst.zon.grs   import rstatszonal
    from glass.rst.alg       import grsrstcalc

    # Events to Raster and to GRASS GIS
    isrst = is_rst(events)

    if isrst:
        gevents = rst_to_grs(events, as_cmd=True)
        fevents = events
    
    else:
        evshp = shp_to_grs(events, asCMD=True)

        # To Raster
        gevents = grsshp_to_grsrst(evshp, 1, f'rst_{evshp}', cmd=True)
        fevents = grs_to_rst(
            gevents,
            os.path.join(ws, loc, f'{gevents}.tif'),
            as_cmd=True, dtype='Byte'
        )
    
    if eventsbyvar and type(eventsbyvar) == dict:
        for k in eventsbyvar:
            eventsbyvar[k] = rst_to_grs(eventsbyvar[k], as_cmd=True)

    # Count region cells
    ncells = count_cells(refrst)

    # Count burned cells
    bcells = count_cells(fevents)

    # Create RI Rasters
    def get_lri(factor, lri, ev):
        # Count number of burned cells by class
        burn_cells_cls = rstatszonal(factor, ev, 'count', f"burn_{factor}")
    
        # Count number of cells by class
        cells_cls = rstatszonal(factor, factor, 'count', f"class_{factor}")
    
        # Create LRI raster for the given factor
        _lri = grsrstcalc((
            f"(double({burn_cells_cls}) / double({cells_cls}))"
            f" / "
            f"({str(int(bcells))}.0 / {str(int(ncells))}.0)"
        ), lri)

        return lri
    
    for k in vars:
        if type(vars[k]) == dict:
            exp, y = [], 0
            
            for _k in vars[k]:
                _v = rst_to_grs(_k, as_cmd=True)

                if eventsbyvar and type(eventsbyvar) == dict and _k in eventsbyvar:
                    var_events = eventsbyvar[_k]
                
                else:
                    var_events = gevents

                _lri = get_lri(
                    _v, f'wlri_{_v}',
                    var_events
                )

                y += vars[k][_k]

                exp.append(f"({_lri} * {str(vars[k][_k])})")
            
            # Sum all
            vars[k] = grsrstcalc(
                f"({' + '.join(exp)}) / {str(y)}",
                f'lri_{k}'
            )
            
        else:
            if eventsbyvar and type(eventsbyvar) == dict and k in eventsbyvar:
                var_events = eventsbyvar[_k]
                
            else:
                var_events = gevents
            
            _v = rst_to_grs(vars[k], as_cmd=True)

            vars[k] = get_lri(_v, f'lri_{k}', var_events)
    
    if all_lri:
        for v in list(vars.values()):
            grs_to_rst(v, os.path.join(all_lri, f'{v}.tif'), dtype="Float64")
    
    # Sum everything
    frst = grsrstcalc(
        f" + ".join(list(vars.values())),
        fprop(out, 'fn')
    )

    # Export result
    grs_to_rst(frst, out, dtype="Float64")

    return out



class HeuristicLri:
    """
    Run LRI Methodology for fires or other hazard
    """

    ref_raster = None
    dem, slope, aspect = None, None, None
    vardem, varslope, varaspect = None, None, None
    gevents = None

    rst_lulc = {}

    lri_results = {}
    final_lri = None
    wildfireprob = None
    perigosity = None

    def __init__(self, ws:str, dem:str, loc:str|None=None):
        from glass.pys.tm import now_as_str
        from glass.wenv.grs import grass_session
        from glass.it.rst import rst_to_grs

        self.ref_raster = dem

        # Start GRASS GIS Session
        if not loc:
            self.loc = now_as_str(utc=True)
        else:
            self.loc = loc
        
        self.ws = ws
        
        self.gb = grass_session(ws, loc=self.loc, srs=dem)

        self.dem = rst_to_grs(dem)
    
    def gen_slope_aspect(self, rst_slope:str|None=None, rst_aspect:str|None=None):
        from glass.rst.surf.grs import slope, aspect
        from glass.it.rst import grs_to_rst

        ## Generate Slope and Aspect Raster
        self.slope = slope(self.dem, 'var_slope', data="degrees", api="grass")
        self.aspect = aspect(self.dem, 'var_aspect', from_north=True, api='grass')

        if rst_slope:
            grs_to_rst(self.slope, rst_slope, dtype="Float64")
        
        if rst_aspect:
            grs_to_rst(self.aspect, rst_aspect, dtype="Float64")
        
        return rst_slope, rst_aspect
    
    def recls_topo(self, rcls_dem:str|None, rcls_slope:str|None=None, rcls_aspect:str|None=None, ndig:int=2):
        """
        Reclass topographic variables
        """

        from glass.cons.firerisk import ELEVATION_RULES, SLOPE_RULES, ASPECT_RULES
        from glass.rst.alg       import grsrstcalc
        from glass.rst.rcls.grs  import rcls_rules, grs_rcls
        from glass.it.rst        import grs_to_rst

        if not self.slope:
            raise ValueError("Slope raster not available - import it first")
        
        if not self.aspect:
            raise ValueError("Aspect raster not available - import it first")

        multifactor = 10

        for i in range(1, ndig):
            multifactor = multifactor * 10
        
        topos = {
            'dem' : {'R' : self.dem, 'RULES' : ELEVATION_RULES},
            'slope' : {'R' : self.slope, 'RULES' : SLOPE_RULES},
            'aspect' : {'R' : self.aspect, 'RULES' : ASPECT_RULES}
        }
        
        # Adjust Rules, Reclassify and Export
        for _var in topos:
            nrules = {}

            for k in topos[_var]["RULES"]:
                nrules[(k[0] * multifactor, k[1] * multifactor)] = topos[_var]["RULES"][k]
            
            rules_txt = rcls_rules(nrules, os.path.join(self.ws, self.loc, f'{_var}_rules.txt'))

            topos[_var]["RULES"] = nrules
            topos[_var]["TXT"] = rules_txt

            # Multiply original rasters
            tmpvar = grsrstcalc(
                f'int(round({topos[_var]["R"]} * {str(multifactor)}))',
                f'int_{topos[_var]["R"]}'
            )

            # Reclassify
            topos[_var]["RCLS"] = grs_rcls(tmpvar, rules_txt, f'rcls_{topos[_var]["R"]}')

            # Export reclassification if requested
            if _var == 'dem' and rcls_dem:
                out = rcls_dem
            
            elif _var == 'slope' and rcls_slope:
                out = rcls_slope
            
            elif _var == 'aspect' and rcls_aspect:
                out = rcls_aspect
            
            else:
                out = None
            
            if out:
                grs_to_rst(topos[_var]["RCLS"], out, dtype="Int32")

        
        self.vardem    = topos["dem"]["RCLS"]
        self.varslope  = topos["slope"]["RCLS"]
        self.varaspect = topos["aspect"]["RCLS"]

        return rcls_dem, rcls_slope, rcls_aspect
    
    def import_events(self, events:str):
        """
        Import Events
        """

        from glass.prop.df       import is_rst
        from glass.it.rst        import rst_to_grs
        from glass.it.shp        import shp_to_grs
        from glass.dtt.rst.torst import grsshp_to_grsrst

        # Check if it is a raster or not
        # If not, convert it to raster
        isrst = is_rst(events)

        isrst = is_rst(events)

        if isrst:
            self.gevents = rst_to_grs(events, as_cmd=True)
    
        else:
            evshp = shp_to_grs(events, asCMD=True)
            # To Raster
            self.gevents = grsshp_to_grsrst(evshp, 1, f'rst_{evshp}', cmd=True)
    
    def import_topo_vars(self, dem:str|None=None, slope:str|None=None, aspect:str|None=None):
        """
        Import topographic variables

        Already reclassified
        """

        from glass.it.rst import rst_to_grs

        if dem:
            self.vardem = rst_to_grs(dem)
        
        if slope:
            self.varslope = rst_to_grs(slope)
        
        if aspect:
            self.varaspect = rst_to_grs(aspect)
        
    def import_lulc_vars(self, vars_lulc:list[str], weights:list[int], 
                         burnareas:list[str]):
        """
        Import Land Use/Land Cover data
        """

        from glass.it.rst        import rst_to_grs
        from glass.rst.alg     import grsrstcalc

        for i, lulc in enumerate(vars_lulc):
            # Import Raster
            rlulc = rst_to_grs(lulc)

            # Ensure it is an integer
            ilulc = grsrstcalc(f"int({rlulc})", f'i{rlulc}')
            self.rst_lulc[ilulc] = {
                "weight" : 1 if not weights[i] else weights[i],
                "burned" : rst_to_grs(burnareas[i])
            }
        
    
    def get_lri(self, events:str, rstvar:str, lri:str, burncells:int, tcells:int) -> str:
        """
        Calculate LRI for a specific variable
        """

        from glass.rst.zon.grs import rstatszonal
        from glass.rst.alg     import grsrstcalc

        # Count number of burned cells by class
        burn_cells_cls = rstatszonal(rstvar, events, 'count', f"burn_{rstvar}")

        # Count number of cells by class
        cells_cls = rstatszonal(rstvar, rstvar, 'count', f"class_{rstvar}")

        # Create LRI raster for the given factor
        _lri = grsrstcalc((
            f"(double({burn_cells_cls}) / double({cells_cls}))"
            f" / "
            f"({str(burncells)}.0 / {str(tcells)}.0)"
        ), lri)

        return _lri
    
    def calc_lri(self, out=None):
        """
        Calculate LRI
        """

        from glass.prop.rst import count_cells
        from glass.rst.alg  import grsrstcalc
        from glass.it.rst import grs_to_rst

        if not self.vardem:
            raise ValueError('DEM var is missing')
        
        if not self.varslope:
            raise ValueError('SLOPE var is missing')
        
        if not self.varaspect:
            raise ValueError('ASPECT var is missing')
        
        if not self.rst_lulc:
            raise ValueError('LULC var is missing')
        
        if not self.gevents:
            raise ValueError('Events raster is missing')

        # Count region cells
        filevardem = grs_to_rst(
            self.vardem,
            os.path.join(self.ws, self.loc, f'{self.vardem}.tif'),
            dtype='Int32'
        )
        ncells = count_cells(filevardem)

        # Count burned cells
        fileev = grs_to_rst(
            self.gevents,
            os.path.join(self.ws, self.loc, f'{self.gevents}.tif'),
            dtype='Int32'
        )
        bcells = count_cells(fileev)

        _vars = {
            "dem"    : self.vardem,
            "slope"  : self.varslope,
            "aspect" : self.varaspect,
            "lulc"   : self.rst_lulc
        }

        for k in _vars:
            if type(_vars[k]) == dict:
                exp, y = [], 0

                for lulc in _vars[k]:
                    revents = _vars[k][lulc]['burned']

                    _lri = self.get_lri(
                        revents, lulc, f'lri_{lulc}',
                        bcells, ncells
                    )

                    y += _vars[k][lulc]["weight"]

                    exp.append(f"({_lri} * {str(_vars[k][lulc]['weight'])})")
                
                # Get Final LULC LRI
                self.lri_results[k] = grsrstcalc(
                    f"({' + '.join(exp)}) / {str(y)}",
                    f'lri_{k}'
                )
            
            else:
                self.lri_results[k] = self.get_lri(
                    self.gevents, _vars[k], f'lri_{k}',
                    bcells, ncells
                )
        
        # Sum Everything
        self.final_lri = grsrstcalc(
            f" + ".join(list(self.lri_results.values())),
            'final_lri'
        )

        if out:
            grs_to_rst(self.final_lri, out, dtype="Float64")

        return out
    
    def export_vars_lri(self, outfolder, bname):
        """
        Export all variables LRI's
        """

        from glass.it.rst import grs_to_rst

        for _var in self.lri_results:
            grs_to_rst(
                self.lri_results[_var],
                os.path.join(outfolder, f'{bname}_{_var}.tif'),
                dtype="Float64"
            )
    
    def export_final_lri(self, outrst):
        """
        Export final LRI
        """

        from glass.it.rst import grs_to_rst

        grs_to_rst(
            self.final_lri, outrst, dtype="Float64"
        )
    
    def wildfire_probability(self, burnedareas, out=None, ff='.shp'):
        """
        Calculate wildfire probability
        """

        from glass.rst.stats.grs import count_regionshp
        from glass.pys.oss import lst_ff
        from glass.it.rst import grs_to_rst

        shps = burnedareas if type(burnedareas) == list else \
            lst_ff(burnedareas, file_format=ff)

        self.wildfireprob = count_regionshp(
            shps,
            out if out else os.path.join(self.ws, self.loc, 'probraster.tif'),
            return_prob=True, nnprob=None
        )

        if out:
            grs_to_rst(self.wildfireprob, out, dtype="Float64", nodata=-1)

        return out
    
    def get_perigosity(self, inlri=None, wildprob=None, out=None):
        """
        Calculate perigosity
        """

        from glass.it.rst import grs_to_rst, rst_to_grs
        from glass.rst.alg       import grsrstcalc

        if inlri:
            self.final_lri = rst_to_grs(inlri)
        
        if wildprob:
            self.wildfireprob = rst_to_grs(wildprob)


        if not self.wildfireprob:
            raise ValueError("Wildfire Probability raster doesn't exist!")
        
        if not self.final_lri:
            raise ValueError("Susceptability raster doesn't exist!")
    

        self.perigosity = grsrstcalc(
            f"if({self.wildfireprob} == 0, 0.001 * {self.final_lri}, {self.wildfireprob} * {self.final_lri})",
            'rst_perigosity'
        )

        if out:
            grs_to_rst(self.perigosity, out, dtype="Float64")

            return out
        
        else:
            return None

