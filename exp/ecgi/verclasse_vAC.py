from PIL import Image
import numpy as np
import numpy.matlib
import math

#Rotina para determinar se existe visibilidade de uma c�lula
#(obsrow,obscol) para uma classe indicada no ficheiro lulc_class com o
#valor 1. As c�lulas onde n�o existe essa classe t�m um valor negativo ou NoData

def verclasse(obsrow,obscol):
    
	#Ler o ficheiro com a localiz�o da classe de interesse (lulc_test.tif)
	im = Image.open('lulc_test_100.tif')
	
	lulc_class = np.array(im)
	
	lulc_class[lulc_class < 0]=np.nan
	
	#Determinar o n� de linhas e colunas do ficheiro com a informa��o de lulc
	lin,col = lulc_class.shape
	
	#Ler o ficheiro com o Modelo Digital de Eleva��o e converter os valores
	#NoData (que aparecem como valores negativos) para NaN
	im2 = Image.open('dem_test_100.tif')
	dem = np.array(im2)
	dem[dem < 0]=np.nan

	#O ficheiro do DEM que o Joaquim enviou tinha mais uma linha e uma coluna
	#do que o ficheiro de LULC, da� ter tirado a �ltima linha e a �ltima
	#coluna.
	
	#Se no local de observa��o n�o houver dados no mapa de LULC ou no DEM,
	#termina e a visibilidade (vis) sai NaN
	if np.isnan(lulc_class[obsrow-1,obscol-1]) or np.isnan(dem[obsrow-1,obscol-1]):
		vis=np.nan
		return vis

	#Se no local de observa��o estiver a classe de interesse, a visibilidade
	#(vis) passa a ser positiva (vis=1) e termina
	if lulc_class[obsrow-1,obscol-1] == 1:
		vis=1
		return vis

	#Inicializa��o de vis a zero
	vis=0

	# verclasse.m:40
	#Testar a visibilidade para todas as c�lulas (seenrow,seencol)
	
	for seenrow in range(0,lin):
		for seencol in range(0,col):
			#Se no local a observar n�o houver dados no mapa de LULC ou no DEM
	#passa j� a analisar a c�lula seguinte
			
			if np.isnan(lulc_class[seenrow-1,seencol-1]) or np.isnan(dem[seenrow-1,seencol-1]):
				continue
				#Se no local a observar estiver a classe de interesse vai testar se o ponto
	#� visivel. Da rotina visibility sai um valor de vis igual a 0 (n�o vis�vel) ou 1 (vis�vel).
			elif lulc_class[seenrow-1,seencol-1] == 1:
				vis=visibilidade(lin,col,obsrow,obscol,seenrow,seencol,dem)
				#return vis
	# verclasse.m:52
			#Se vis=1 encontrou um ponto visvel e termina. Se n�o, vai analisar o
	#ponto seguinte.
			if vis == 1:
				print(vis)
				print(seenrow)
				print(seencol)
				return vis

def visibilidade(lin=None,col=None,obsrow=None,obscol=None,seenrow=None,seencol=None,dem=None):
	

    #Entram:
#- Os valores da dimenso das matrizes - variveis "lin" e "col";
#- A linha e coluna do ponto de observao ('obsrow' e 'obscol' e do ponto
#a visualizar ('seenrow' e 'seencol');
#- O ficheiro raster onde estamos a registar a visibilidade 'event_vis';
#- O Modelo Digital de Terreno ('DEM').
    
    #Tirar 0.5 de do valor da linha e coluna da c�lula de origem e destino para 
#obter o centro da clula em funo do n da linha e coluna.
    
    #Depois calcula-se o valor de z para os pontos de origem e destino a partir
#do DEM ('zobs' e 'zseen').
    
	yobs=obsrow - 0.5
	xobs=obscol - 0.5
	zobs=dem[obsrow-1,obscol-1]

	yseen=seenrow - 0.5
	xseen=seencol - 0.5
	zseen=dem[seenrow-1,seencol-1]

    #Vetor diretor da reta no espa�o
    
	vetor_diretor = np.array([[xseen-xobs , yseen-yobs , zseen-zobs]])
	
	#print(vetor_diretor.shape)
	#return
    
#Declive ('m') e ordenada na origem ('b') da equao da reta no pano que une 
#o ponto de observao e o ponto a observar.
    
	m = np.divide((yseen - yobs), (xseen - xobs))
	b = yobs - m * xobs
	
    #Pretende-se obter os valores de x e y de interseo do segmento que une o 
#ponto de observao com o ponto a observar (no plano) com os limites das clulas.
#Para isso, comea-se no valor minimo de x, e usa-se o menor nmero inteiro maior
#que o minimo de x, e vai-se somando 1 at chegar ao maior inteiro menor que o valor 
#mximo de x. No final inclui-se tambm o as coordenadas do ponto do ltimo
#ponto, que pode ser o ponto de origem ou destino (dependendo de qual dos
#pontos tem maior valor de x), portanto ser
    
    #Faz-se da mesma forma para y.
    
	#print(math.ceil(min(xobs,xseen)))
	#print(math.floor(max(xobs,xseen)))
	#print(max(xobs,xseen))
	#return
	seg_x=np.array([np.append(np.arange(math.ceil(min(xobs,xseen)) , math.floor(max(xobs,xseen))+1 , 1), max(xobs,xseen))])
	seg_y=np.array([np.append(np.arange(math.ceil(min(yobs,yseen)) , math.floor(max(yobs,yseen))+1 , 1), max(yobs,yseen))])
    
    #Para cada valor de x encontrado calcula-se o y, usando a equao da
#reta no plano. Da mesma forma para cada valor de y encontrado calcula-se o valor de
#x.
    
	if xseen == xobs:
		x1=np.matlib.repmat(seg_x,seg_y.shape[0],seg_y.shape[1])
		seg_x=np.array([])
		y1=np.array([])
		
	elif m == 0:
		y1=m*seg_x + b
		x1=np.array([])
		seg_y=np.array([])
				
	else:
		print('else')
		y1=m*seg_x + b
		x1=(seg_y - b) / m		
    
#Constroi-se um vetor para agregar os valores de y aos valores de x
#encontrados acima, e vice versa (os valores de x para os valores de y
#encontrados acima). Isto d�-nos as coordenadas dos pontos de interse��o
#dos segmentos com os limites das c�lulas.

	#print(seg_y.shape)
	#print(x1.shape)
	
	if xseen == xobs:
		vec1=np.array([])
	else:
		vec1=np.append(seg_x.T, y1.T, axis=1)
	if m==0:
		vec2=np.array([])
	else:
		vec2=np.append(x1.T, seg_y.T, axis=1)
	
#Juntam-se os dois vetores apenas num, e depois ordenam-se de forma a ter
#os valores de x crescentes.

	vec=np.array(np.append(vec1, vec2,axis=0))
	vec_ord=np.sort(vec,0)

#Para cada ponto de interses�o o identifica-se qual a celula de onde a linha
#vem (e que portanto interseta a linha) e vai-se guardando a sequncia de
#clulas encontradas - vetor "cells".
# 
# cells=[ceil(vec_ord(1,2)) ceil(vec_ord(1,1))];
# 
# for i=2:size(vec_ord,1)
#     cells=[cells;ceil(vec_ord(i,2)) ceil(vec_ord(i,1))];
# end



	
	cells=np.ceil(np.append(vec_ord[:,1:2],vec_ord[:,0:1],axis=1))
	
# if cells(1,:)==[obsrow obscol]
#     cells=[cells;seenrow seencol]
# else
#     cells=[cells;obsrow obscol]
# end
    
#Obter a linha encontrada em formato matriz - comea-se com uma matriz de
#vazia (NaN) e alteram-se para 1 as clulas que pertencem  linha.
    
	line=np.full((lin,col),np.nan)

	indice = cells[:,0] + (cells[:,1]-1)*lin
	indice = [int(x) for x in indice]

	line.ravel()[indice]=1

#Para obter o valor de z para cada c�lula da linha em fun��o do declive da reta no espa�o, calcula-se 
#o valor da constante K da equa��o vetorial da reta no espa�o que passa
#pelo ponto de observa��o e pelo ponto a considerar.
    
	K=(vec_ord[:,:1] - xobs) / vetor_diretor[0][0]

	Z=zobs + np.dot(K,vetor_diretor[0][2])
	
	z_line=np.full((lin,col),np.nan)
	
	z_line.ravel()[indice]=np.ravel(Z)

#Para determinar a diferena entre o valor da altitude obtida para cada
#ponto e e clula
    
	
	Dif=dem - z_line
	Dif[np.isnan(Dif)] = 0
	
	if np.sum(np.sum(Dif>0) > 0):
		vis=0
	else:
		vis=1
	
	return vis

# teste
print(verclasse(580,533))