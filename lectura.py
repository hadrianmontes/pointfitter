# -*- coding: utf-8 -*-
"""
Created on Sun Jul 20 17:32:02 2014

@author: hadrian
"""
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pylab as plt
import sys

def lecturagrafico(entradatotal):
   #Open the xvg file
   data=[]
   leyenda=[]
   for entrada in entradatotal:
    f=open(entrada,'r')
    #Search in the xvg for a title
    titulo=""
    j=len(data)
    for l in f:
        try:
            if l.split()[1]=='title':
                le=len(l.split())
                for i in range(2,le):
                    titulo=titulo+l.split()[i]+" "
                titulo=titulo+"\n"
                break
        except:
            pass
    f.close
    f=open(entrada,'r')
    #Search in the xvg for a subtitle
    for l in f:
        try:
            if l.split()[1]=='subtitle':
                le=len(l.split())
                for i in range(2,le):
                    titulo=titulo+l.split()[i]+" "
                break
        except:
            pass
    f.close
    f=open(entrada,'r')
    x=[]
    y=[]
    for l in f:
        #Read only the lines with data
        try:
            x.append(float(l.split()[0]))
            y.append(float(l.split()[1]))
        except:
            #if there is a change in the group of data save the data and restart x and y
            if l.strip()=='&':
                data.append([x,y])
                x=[]
                y=[]
            else:
                pass
    #check if the data was saved and reseted, if not, save.
    if x!=[]:
        data.append([x,y])
    #Each group of data is saved under one element of the variable "data".
    #For each group of data the first element is an array with de x data and
    #the second element is de y data
    
    #We search now for a legend
    for i in range(len(data)-j):
        ley=''
        f=f=open(entrada,'r')
        for l in f:
            try:
                if l.split()[1:3]==['s%i'%i,'legend']:
                    for j in range(3,len(l.split())):
                        ley=ley+l.split()[j]+" "
                    leyenda.append(ley)
                    break
            except:
                pass
        try:
            leyenda[i+j]
        except:
	    if len(data)-j-1==0:
            	print 'Leyenda para el archivo',entrada
	    	leyenda.append(raw_input())
	    else:
		print 'Leyenda para el conjunto de datos',str(i+1), 'del archivo',entrada
	    	leyenda.append(raw_input())
   return data, leyenda, titulo
    #plot all the groups of data and integrate
def plotint(data,leyenda,titulo):
    fig, axes=plt.subplots()
    j=0
    if leyenda==[]:
        leyenda==['']
    for item in data:
           axes.plot(item[0],item[1],label=leyenda[j])
           j=j+1
    axes.set_title(titulo)
    axes.legend(loc='best')

    plt.show()       
if __name__=="__main__":
    if len(sys.argv)>=2:
	archivos=[]	
	for j in range(len(sys.argv)-1):
		archivos.append(sys.argv[j+1])
        data,leyenda,titulo=lecturagrafico(archivos)
        plotint(data,leyenda,titulo)
        
    else:
       sys.stderr.write('Usage: {} inputfile.xvg\n'.format(sys.argv[0]))
       sys.exit(1)
       
