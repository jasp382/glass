"""
Hydrologic procedures
"""


def hidric_balance(tempbymonth, rainbymonth, outrst, texture=None,
    insolation=[9.8,10.7,12.0,13.3,14.4,15.0,14.7,13.7,12.5,11.0,10.0,9.4]):
    """
    Proper description
    """
    
    import numpy as np
    from glass.g.rd.rst import rst_to_array
    from glass.g.wt.rst import obj_to_rst
    
    def SomaRstOnLst(l):
        for i in range(1, len(l)):
            l[i] = l[i] + l[i-1]
        return l[-1]
    
    def indexCaloricoAnual(tempMensal):
        lst_ICM = []
        c = 0
        for rst in tempMensal:
            rst_array = rst_to_array(rst)
            rst_icm = (rst_array / 5.0)**1.514
            lst_ICM.append(rst_icm)
        ica = SomaRstOnLst(lst_ICM)
        return ica
    
    def EvapotranspiracaoPotencial(tMensal, ICAnual, insolacao):
        dias_mes = [31,28,31,30,31,30,31,31,30,31,30,31]
        a = 0.492 + (0.0179 * ICAnual) - (0.0000771 * ICAnual**2) + (0.000000675 * ICAnual**3)
        lst_k = []
        ETP_value = []
        for mes in range(len(dias_mes)):
            k = (float(insolacao[mes]) * float(dias_mes[mes])) / 360.0
            lst_k.append(k)
        for raster in range(len(tMensal)):
            rst_array = rst_to_array(tMensal[raster])
            etp = 16.0 * ((10.0 * rst_array/ICAnual)**a)
            ETP = etp * lst_k[raster]
            ETP_value.append(ETP)
        return ETP_value
    
    def DefClimatico(precipitacao, EvapoT_Potencial):
        Exd_Hid = []
        dClimaC = []
        for raster in range(len(precipitacao)):
            rst_array = rst_to_array(precipitacao[raster])
            excedente_hidrico = rst_array - EvapoT_Potencial[raster]
            Exd_Hid.append(excedente_hidrico)
        for rst in range(len(Exd_Hid)):
            cop = np.zeros((Exd_Hid[rst].shape[0], Exd_Hid[rst].shape[1]))
            np.copyto(cop, Exd_Hid[rst], 'no')
            if rst == 0:
                np.place(cop, cop>0, 0)
                dClimaC.append(cop)
            else:
                np.place(cop, cop>0, 0)
                dClimaC.append(cop + dClimaC[rst-1])
        return [Exd_Hid, dClimaC]
    
    def reservaUtil(textura, excedenteHid, defice):
        lst_ru = []
        for rst in range(len(excedenteHid)):
            ru = textura * np.exp(defice[rst]/textura)
            np.copyto(ru, textura, 'no', defice[rst]==0)
            if rst == 0:
                lst_ru.append(ru)
            else:
                ex_hid_mes_anterior = np.zeros((ru.shape[0], ru.shape[1]))
                np.place(ex_hid_mes_anterior, excedenteHid[rst-1]<0, 1)
                ex_hid_este_mes = np.zeros((ru.shape[0], ru.shape[1]))
                np.place(ex_hid_este_mes, excedenteHid[rst]>0, 1)
                recarga = ex_hid_mes_anterior + ex_hid_este_mes
                no_caso_recarga = lst_ru[rst-1] + excedenteHid[rst]
                if 2 in np.unique(recarga):
                    np.copyto(ru, no_caso_recarga, 'no', recarga==2)
                else:
                    ex_hid_mes_anterior = np.zeros((ru.shape[0], ru.shape[1]))
                    np.place(ex_hid_mes_anterior, excedenteHid[rst-1]>0, 1)
                    ex_hid_este_mes = np.zeros((ru.shape[0], ru.shape[1]))
                    np.place(ex_hid_este_mes, excedenteHid[rst]>excedenteHid[rst-1], 1)
                    recarga = ex_hid_mes_anterior + ex_hid_este_mes
                    no_caso_recarga = lst_ru[rst-1] + excedenteHid[rst]
                    np.copyto(ru, no_caso_recarga, 'no', recarga==2)
                lst_ru.append(ru)
        return lst_ru
    
    def VariacaoReservaUtil(lst_ru):
        lst_vru = []
        for rst in range(len(lst_ru)):
            if rst == 0:
                vru = lst_ru[-1] - lst_ru[rst]
            else:
                vru = lst_ru[rst-1] - lst_ru[rst]
            lst_vru.append(vru)
        return lst_vru
    
    def ETR(precipitacao, vru, etp):
        lst_etr = []
        for rst in range(len(precipitacao)):
            p_array = RasterToArray(precipitacao[rst])
            etr = p_array + vru[rst]
            np.copyto(etr, etp[rst], 'no', p_array>etp[rst])
            lst_etr.append(etr)
        return lst_etr
    
    def DeficeHidrico(etp, etr):
        return [etp[rst] - etr[rst] for rst in range(len(etp))]
    
    if texture:
        rst_textura = rst_to_array(texture)
    else:
        rst_textura = None
    
    # Lista Raster com valores de precipitacao
    tempbymonth, rainbymonth
    
    ica = indexCaloricoAnual(tempbymonth)
    n_dias = fileTexto(file_insolacao)
    EvapotranspiracaoP = EvapotranspiracaoPotencial(tempbymonth, ica, n_dias)
    Defice_climatico = DefClimatico(rainbymonth, EvapotranspiracaoP)
    excedente_hidrico = Defice_climatico[0]
    defice_climatico_cumulativo = Defice_climatico[1]
    reserva_util = reservaUtil(rst_textura, excedente_hidrico, defice_climatico_cumulativo)
    vru = VariacaoReservaUtil(reserva_util)
    etr = ETR(rainbymonth, vru, EvapotranspiracaoP)
    def_hidrico = DeficeHidrico(EvapotranspiracaoP, etr)
    # Soma defice hidrico
    rst_hidrico = SomaRstOnLst(def_hidrico)
    obj_to_rst(rst_hidrico, outrst, tempbymonth[0])

