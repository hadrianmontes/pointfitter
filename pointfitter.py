#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 26 12:42:27 2015

@author: hadrian

"""
from Tkinter import *
import ttk
from scipy.optimize import curve_fit
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from scipy.interpolate import UnivariateSpline
from scipy import stats
#import scipy.special._ufuncs_cxx
import numpy as np
from numpy import e,pi,exp,cos,sin,tan,log,log10
import tkMessageBox,tkFileDialog
#import FileDialog

class fitter(Frame):
    def __init__(self,mainframe):
        #Creamos el frame Principal (en el que estara casi todo)
#        mainframe=ttk.Frame(master,padding="3 3 12 12")
#        mainframe.grid(column=1,row=0,sticky=(N,W,E,S))
#        mainframe.columnconfigure(0,weight=1)
#        mainframe.rowconfigure(0,weight=1)
        global xx,datos,yy,sigma
        xx=[]
        yy=[]
        datos=[]
        sigma=[]
        #Creamos un primer menu
        menu=Menu(root)
        menu2=Menu(menu,tearoff=0)
        menu2.add_command(label='Open',command=self.fileinput)
        menu2.add_command(label='Save',command=self.save)
        menu2.add_command(label='Export Data',command=self.exportdata)
        menu.add_cascade(label="File", menu=menu2)
        #Listado de funciones predefinidas
        self.indicef=dict()
        self.indicef.update({'Gaussiana':funcionindex()})
        self.indicef['Gaussiana'].funcion('gaussian(x,a,b,c)')
        self.indicef['Gaussiana'].index(3)
        self.indicef['Gaussiana'].helpp('Normalized Gaussian of amplitud a, mean b and width c')
        
        self.indicef.update({'Linear':funcionindex()})
        self.indicef['Linear'].funcion('recta(x,a,b)')
        self.indicef['Linear'].index(2)
        self.indicef['Linear'].helpp('function a+b*x')
        
        self.indicef.update({'Poisson':funcionindex()})
        self.indicef['Poisson'].funcion('poisson(x,a,b)')
        self.indicef['Poisson'].index(2)
        self.indicef['Poisson'].helpp('Poisson distribution of expected value b and amplitude a')
   
        self.indicef.update({'Cuadratic':funcionindex()})
        self.indicef['Cuadratic'].funcion('cuadratic(x,a,b,c)')
        self.indicef['Cuadratic'].index(3)
        self.indicef['Cuadratic'].helpp('function a*x**2+b*x+c') 
        
        self.indicef.update({'Cubic':funcionindex()})
        self.indicef['Cubic'].funcion('cubic(x,a,b,c,d)')
        self.indicef['Cubic'].index(4)
        self.indicef['Cubic'].helpp('function a*x**3+b*x**2+c*x+d')
        
        self.indicef.update({'Exponential Decay':funcionindex()})
        self.indicef['Exponential Decay'].funcion('exponentialdecay(x,a,b)')
        self.indicef['Exponential Decay'].index(2)
        self.indicef['Exponential Decay'].helpp('Exponential decay of initial value a and constant of decayment b')       
        #Funciones Predeterminadas
        ttk.Label(mainframe,text='Preset Functions\n Press Help and see the definition of each function').grid(column=0,row=7)
        self.funcion=StringVar()
        self.combo=ttk.Combobox(mainframe,textvariable=self.funcion,state='readonly')
        self.combo['values']=self.indicef.keys()
        self.combo.grid(column=1,row=7)
        self.combo.bind("<<ComboboxSelected>>",self.funcionselect2)   
        ttk.Button(mainframe,text='Help',command=self.funcionhelp).grid(column=2,row=7)
        
        #Entrada de la funcion
        ttk.Label(mainframe,text='Write a function of x using up to 9 parameters,\n use then in this order: a,b,c,d,f,g,h,i,j').grid(column=0,row=8)
        self.entrada=StringVar()
        self.name = ttk.Entry(mainframe, textvariable=self.entrada).grid(column=1,row=8)
        #Entrada numero de parametros
        ttk.Label(mainframe,text='Number of used parameters').grid(column=0,row=9,sticky=N)
        self.parametros=IntVar()
        ttk.Entry(mainframe,textvariable=self.parametros).grid(column=1,row=9,sticky=N)
        #Ploteado y ajustes
        ttk.Button(mainframe,command=self.plotear,text='Plot').grid(column=0,row=10,sticky=(N))
        #Ponemos los ajustes y reajustes
        ttk.Button(mainframe,command=self.selectorajuste,text='Fit').grid(column=0,row=11)
        self.salida=StringVar()
        ttk.Entry(mainframe,textvar=self.salida,width=35).grid(column=1,row=11,columnspan=2)
        #Escribimos las incertidumbres
        ttk.Label(mainframe,text='Uncertainty').grid(column=0,row=12)
        self.incertidumbresa=StringVar()        
        ttk.Entry(mainframe,textvar=self.incertidumbresa,width=35).grid(column=1,row=12,columnspan=2)
        #Representación grafica
        self.point=StringVar()
        self.point.set('x')
        self.line=StringVar()
        self.line.set('')
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas=FigureCanvasTkAgg(self.fig,master=mainframe)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=3,row=1,rowspan=8,columnspan=3)
        secondframe=ttk.Frame(mainframe)
        secondframe.grid(column=3,row=0,sticky=(N,W,E,S),columnspan=3)
        NavigationToolbar2TkAgg(self.canvas, secondframe)
        self.ax.set_xlim([1,10])
        
        #Guardar archivos
        #ttk.Label(mainframe,text='Ruta de Guardado').grid(column=3,row=5)
        self.rutasave=StringVar()
        #ttk.Entry(mainframe, textvariable=rutasave).grid(column=4,row=5)
        #ttk.Button(mainframe,text='Guardar',command=self.save).grid(column=5,row=9)
        
        #Apertura de archivo
        #ttk.Button(mainframe,text='file',command=self.fileinput).grid(column=1,row=0,sticky=(N))
        self.entradafile=StringVar()
        ttk.Label(mainframe,textvariable=self.entradafile,width=75).grid(column=0,row=0,sticky=(N),columnspan=3)
        
        
        # Vamso a escribir el archivo
        self.archivoescrito=StringVar()
        self.T=Text(mainframe,width=40)
        self.T.grid(column=0,row=1,rowspan=6,sticky=N)
        # Editamos los valores de las columnas
        ttk.Label(mainframe,text=' For defining the axes'+
        ' write\n a function of C1,C2,.. and press set X and setY.\n The number following C indicate the column').grid(column=1,row=3,columnspan=2)
        self.setx=StringVar()
        ttk.Entry(mainframe,textvar=self.setx).grid(column=1,row=4)
        ttk.Button(mainframe,text='Set x',command=self.setxcolumn).grid(column=2,row=4)
        self.sety=StringVar()
        ttk.Entry(mainframe,textvar=self.sety).grid(column=1,row=5)
        ttk.Button(mainframe,text='Set y',command=self.setycolumn).grid(column=2,row=5)
        
        
        #Añadimos edicion de las caracteristicas de las graficas
        self.xmin=DoubleVar()
        self.xmax=DoubleVar()
        self.xmax.set(1)
        self.ymin=DoubleVar()
        self.ymax=DoubleVar()
        self.ymax.set(1)

        ttk.Label(mainframe,text='Min.').grid(column=3,row=9)
        ttk.Label(mainframe,text='Max.').grid(column=4,row=9)
        #Eje x
        ttk.Entry(mainframe,textvar=self.xmin,width=10).grid(column=3,row=10)
        ttk.Entry(mainframe,textvar=self.xmax,width=10).grid(column=4,row=10)
        ttk.Button(mainframe,text='X range',command=self.reescalex).grid(column=5,row=10)
        #Eje y
        ttk.Entry(mainframe,textvar=self.ymin,width=10).grid(column=3,row=11)
        ttk.Entry(mainframe,textvar=self.ymax,width=10).grid(column=4,row=11)
        ttk.Button(mainframe,text='Y range',command=self.reescaley).grid(column=5,row=11)
        #Ejes Logaritmicos
        ttk.Button(mainframe,text='Lineal Scale',command=self.lineal).grid(column=3,row=12)
        ttk.Button(mainframe,text='Log X',command=self.logx).grid(column=4,row=12)
        ttk.Button(mainframe,text='Log Y',command=self.logy).grid(column=5,row=12)
       
        
        #ANTIGUO
        #ttk.Entry(mainframe,textvar=self.yaxe).grid(column=3,row=10)
        #ttk.Button(mainframe,text='Y Label',command=self.setylabel).grid(column=4,row=10,sticky=W)
        #Titulo

        #ttk.Entry(mainframe,textvar=titleaxe).grid(column=3,row=11)
        #ttk.Button(mainframe,text='Titulo',command=self.settitle).grid(column=4,row=11,sticky=W)

        #Ahora con menus cambiamos las etiquetas
        self.xaxe=StringVar()
        self.yaxe=StringVar()
        self.titleaxe=StringVar()
        edit=Menu(menu,tearoff=0)
        edit.add_command(label='Xlabel',command=self.setxlabel)
        edit.add_command(label='Ylabel',command=self.setylabel)
        edit.add_command(label='Title',command=self.settitle)

        menu.add_cascade(label="Edit", menu=edit)
        
        
        #Añado la opción de ir guardand las diferentes graficas que se hagan
        self.mantenerplot=IntVar()
        ttk.Checkbutton(mainframe,text='Maintain Graphics Between Plots',variable=self.mantenerplot
            ).grid(column=1,row=1)
            
        #Añadir la opcion de añadir incertidumbres    
        self.usarincertidumbres=IntVar()
        ttk.Checkbutton(mainframe,text='Use Uncertainties',variable=self.usarincertidumbres
            ).grid(column=1,row=2,sticky=W)
        self.stringincertidumbres=StringVar()
        ttk.Entry(mainframe,textvar=self.stringincertidumbres).grid(column=1,row=6)
        ttk.Button(mainframe,text='Set Uncertainties',command=self.setincertidumbres).grid(column=2,row=6)
        #Splines cubicos
        #ttk.Button(mainframe,text='Interpolate',command=self.splines).grid(column=4,row=12,sticky=W)
        #self.level=StringVar()
        #ttk.Entry(mainframe,textvar=self.level,width=5).grid(column=3,row=12)
        interpolate=Menu(menu,tearoff=0)
        interpolate.add_command(label='Cubic Splines',command=self.splines)
        interpolate.add_command(label='Special Cubic Splines',command=self.splines2)
        menu.add_cascade(label="Interpolate", menu=interpolate)
        #Añado Rebining
        histogram=Menu(menu,tearoff=0)
        histogram.add_command(label='Rebining',command=self.rebining)
        menu.add_cascade(label="Histogram", menu=histogram)
        chi=Menu(menu,tearoff=0)
	#Añadimos calculo de chi square
        chi.add_command(label='Chi square analisys',command=self.chisquare)
        menu.add_cascade(label="Chi Square", menu=chi)
        #Añadimos seleccion de rango
        edit.add_command(label='Set data Range',command=self.adquisicion)

        #Añadimos opciones sobre como hacer el plot
        Plot=Menu(menu,tearoff=0)
        Plot.add_command(label='Reset Plot',command=self.cleargraph)
        Plot.add_command(label='Select Point Marker',command=self.selectpoint)
        Plot.add_command(label='Derivate',command=self.derivate)
        self.savelegendfile=StringVar()
        Plot.add_command(label='Prepare Multiple Plot',command=self.legendwindow)
        Plot.add_command(label='Make Multiple Plot',command=self.importlegendfile)
        menu.add_cascade(label='Plot',menu=Plot)
        
        
        root.config(menu=menu)
    def legendwindow(self,*args):
        self.windowlegend=Toplevel()
        self.savedata=IntVar()
        self.savefit=IntVar()
        self.savesigma=IntVar()
        self.savedata.set(0)
        self.savefit.set(0)
        self.labeldata=StringVar()
        self.labelfit=StringVar()
        self.pointfit=StringVar()
        self.linefit=StringVar()
        self.linefit.set('-')
        ttk.Button(self.windowlegend,text='Outputile',command=self.selectlegendfile).grid(column=0,row=0)
        ttk.Entry(self.windowlegend,textvar=self.savelegendfile,width=40).grid(column=1,row=0,columnspan=6)
        ttk.Checkbutton(self.windowlegend,text='Add Data',variable=self.savedata).grid(column=0,row=1,sticky=W) 
        ttk.Label(self.windowlegend,text='Label').grid(column=1,row=1)
        ttk.Entry(self.windowlegend,textvar=self.labeldata).grid(column=2,row=1)
        ttk.Label(self.windowlegend,text='Marker').grid(column=3,row=1)
        ttk.Entry(self.windowlegend,textvar=self.point,width=5).grid(row=1,column=4)
        ttk.Label(self.windowlegend,text='Line Style').grid(row=1,column=5)
        ttk.Entry(self.windowlegend,textvar=self.line,width=5).grid(row=1,column=6)
        ttk.Checkbutton(self.windowlegend,text='Save Uncertainties',variable=self.savesigma).grid(column=7,row=1)
        ttk.Checkbutton(self.windowlegend,text='Add Fit',variable=self.savefit).grid(column=0,row=2,sticky=W) 
        ttk.Label(self.windowlegend,text='Label').grid(column=1,row=2)
        ttk.Entry(self.windowlegend,textvar=self.labelfit).grid(column=2,row=2)
        ttk.Label(self.windowlegend,text='Marker').grid(column=3,row=2)
        ttk.Entry(self.windowlegend,textvar=self.pointfit,width=5).grid(row=2,column=4)
        ttk.Label(self.windowlegend,text='Line Style').grid(row=2,column=5)
        ttk.Entry(self.windowlegend,textvar=self.linefit,width=5).grid(row=2,column=6)
        ttk.Button(self.windowlegend,text='Ok',command=self.exportlegendfile).grid(row=3,column=7)        
        return
    def selectlegendfile(self,*args):
        self.savelegendfile.set(tkFileDialog.asksaveasfilename())
        return
    def exportlegendfile(self,*args):
        global xx,yy,sigma
        f=open(self.savelegendfile.get(),'a+')
        if self.savedata.get()==1:
            f.write('#Begin\n')
            f.write(r'#Label '+self.labeldata.get()+'\n')
            f.write(r'#Marker '+self.point.get()+'\n')
            f.write(r'#linestyle '+self.line.get()+'\n')
            f.write(r'#sigma '+str(self.savesigma.get())+'\n')
            for i in range(len(xx)):
                f.write(str(xx[i])+'\t'+str(yy[i]))
                if self.savesigma.get()==1:
                    f.write('\t'+str(sigma[i]))
                f.write('\n')
            f.write(r'#END'+'\n')
        if self.savefit.get()==1:
            puntos=np.linspace(xx.min(),xx.max(),1000)
            index=self.parametros.get()
            p0=''
            for i in range(index):
                p0+=','+self.salida.get().split()[2*i+1]
            y=eval('self.funcion'+str(index)+r'var(puntos'+p0+')')
            f.write('#Begin\n')
            f.write(r'#Label '+self.labelfit.get()+'\n')
            f.write(r'#Marker '+self.pointfit.get()+'\n')
            f.write(r'#linestyle '+self.linefit.get()+'\n')
            f.write(r'#sigma '+'0'+'\n')
            for i in range(len(puntos)):
                f.write(str(puntos[i])+'\t'+str(y[i]))
                f.write('\n')
            f.write(r'#END'+'\n')
        f.close()
        self.windowlegend.destroy()
        return
    def importlegendfile(self,*args):
        filename=tkFileDialog.askopenfilename()
        f=open(filename,'r')
        self.ax.clear()
        siz=2
        x=[]
        y=[]
        sigma=[]
        for l in f:
            if l.startswith(r'#Label'):
                if len(l.split())==2:
                    Label=l.split()[1]
                elif len(l.split())>2:
                    Label=''
                    for palabra in l.split()[1:]:
                        Label=Label+' '+palabra
                else:
                    Label=srt(n)
            elif l.startswith(r'#Marker'):
                if len(l.split())==2:
                    Marker=l.split()[1]
                else:
                    Marker=''
            elif l.startswith(r'#linestyle'):
                if len(l.split())==2:
                    Linestyle=l.split()[1]
                else:
                    Linestyle=''
            elif l.startswith(r'#sigma'):
                siz=siz+int(l.split()[1])
            elif not l.startswith(r'#'):
                if len(l.split())>1:
                    if siz==2:
                        x.append(float(l.split()[0]))
                        y.append(float(l.split()[1]))      
                    elif siz==3:
                        x.append(float(l.split()[0]))
                        y.append(float(l.split()[1]))
                        sigma.append(float(l.split()[2]))
            elif l.startswith(r'#END'):
                if siz==2:
                    self.ax.plot(x,y,marker=Marker,linestyle=Linestyle,label=Label)
                elif siz==3:
                    self.ax.errorbar(x,y,yerr=sigma,marker=Marker,linestyle=Linestyle,label=Label)
                x=[]
                y=[]
                siz=2
        f.close()
        self.ax.legend(loc='best')
        self.canvas.draw()
        return
    def derivate(self,*args):
        global xx, yy
        xnew=[]
        ynew=[]
        for i in range(len(xx)-1):
            xnew.append(xx[i])
            ynew.append((yy[i+1]-yy[i])/(xx[i+1]-xx[i]))
        xx=np.array(xnew)
        yy=np.array(ynew)
        return
    def selectpoint(self,*args):
        self.windowselect=Toplevel()
        ws = self.windowselect.winfo_screenwidth()
        hs = self.windowselect.winfo_screenheight()
        self.select=StringVar()
        self.select.set(self.point.get())
        self.selectline=StringVar()
        self.selectline.set(self.line.get())
        # calculate position x, y
        w=175
        h=100
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.windowselect.geometry('%dx%d+%d+%d' % (w, h, x, y))
        ttk.Label(self.windowselect,text='Enter the marker ').grid(column=0,row=0,columnspan=2)
        ttk.Entry(self.windowselect,textvariable=self.select).grid(column=0,row=1,columnspan=2)
        ttk.Label(self.windowselect,text='Enter the linestyle').grid(column=0,row=2,columnspan=2)
        ttk.Entry(self.windowselect,textvariable=self.selectline).grid(column=0,row=3,columnspan=2)
        ttk.Button(self.windowselect,text='Cancel',command=self.windowselect.destroy).grid(column=0,row=4)
        ttk.Button(self.windowselect,text='Save',command=self.selectmanual).grid(column=1,row=4)
        return
    def selectmanual(self,*args):
        self.point.set(self.select.get())
        self.line.set(self.selectline.get())
        self.windowselect.destroy()
        return
        
    def cleargraph(self,*args):
        self.ax.clear()
        self.canvas.draw()
        return
    def exportdata(self,*args):
        global xx,yy,sigma
        self.rutaexport=StringVar()
        self.rutaexport.set(tkFileDialog.asksaveasfilename())
        f=open(self.rutaexport.get(),'w+')
        for i in range(len(xx)):
            f.write(str(xx[i]))
            f.write('\t')
            f.write(str(yy[i]))
            if len(xx)==len(sigma):
                f.write('\t')
                f.write(str(sigma[i]))
            f.write('\n')
        f.close()
        return
            
    def chisquare(self,*args):
        global xx,yy,sigma
        index=self.parametros.get()
        p0=''
        for i in range(index):
            p0+=','+self.salida.get().split()[2*i+1]
        suma=0
        for j in range(len(xx)):
            x=xx[j]
            y=yy[j]
            sig=sigma[j]
            suma+=(y-eval('self.funcion'+str(index)+r'var(x'+p0+')'))**2/(sig**2)
	prob=1-stats.chi2.cdf(suma,len(xx)-index)
        self.windowc=Toplevel()
        ws = self.windowc.winfo_screenwidth()
        hs = self.windowc.winfo_screenheight()
        # calculate position x, y
        w=175
        h=100
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.windowc.geometry('%dx%d+%d+%d' % (w, h, x, y))
        ttk.Label(self.windowc,text='Value of Chi Square').grid(column=0,row=0)
	self.suma=StringVar()
	self.prob=StringVar()
	self.suma.set(str(suma))
	self.prob.set(str(prob))
        ttk.Entry(self.windowc,textvar=self.suma).grid(column=0,row=1)
	ttk.Label(self.windowc,text='Probability').grid(column=0,row=2)
	ttk.Entry(self.windowc,textvar=self.prob).grid(column=0,row=3)
        ttk.Button(self.windowc,text='Ok',command=self.winchi).grid(column=0,row=4)
        return
    def winchi(self,*args):
        self.windowc.destroy()
        return
    def fileinput(self,*args):
        filename=tkFileDialog.askopenfilename()
        self.entradafile.set(filename)
        global datos,xx,yy
        datos,archivoentrada2=self.lectura(filename)
        self.archivoescrito.set(archivoentrada2)
        #xx=datos[0]
        #yy=datos[1]
        self.T.delete(0.0,END)
        self.T.insert(END, self.archivoescrito.get())
        return
    def funcionselect2(self,*args):
        self.entrada.set(self.indicef[self.funcion.get()].funcion)
        self.parametros.set(self.indicef[self.funcion.get()].index)
        return
    def funcionhelp(self,*args):
        tkMessageBox.showinfo('Info',self.indicef[self.funcion.get()].helpp)
        return
    def setxcolumn(self,*args):
        global xx
        xx=[]
        interpretado=''
        replaceindex=0
        numero=1
        total=0
        for i in range(len(self.setx.get())):
            if replaceindex==0:
                if self.setx.get()[i]!='C':
                    interpretado=interpretado+self.setx.get()[i]
                else:
                    replaceindex=1
                    interpretado=interpretado+'np.array(datos'
            else:
                try:
                    total=total*numero+int(self.setx.get()[i])
                    numero=numero*10
                except:                                    
                    interpretado=interpretado+'['+str(total-1)+'])'+self.setx.get()[i]
                    replaceindex=0
                    total=0
                    numero=1
        if replaceindex!=0:
            interpretado=interpretado+'['+str(total-1)+'])'
            replaceindex=0
            numero=1
            total=0
        try:
            xx=eval(interpretado)
        except:
            tkMessageBox.showerror("Error", 'Error al evaluar al expresion comprueba el uso de C mayuscula')
        return
    def setycolumn(self,*args):
        global yy
        yy=[]
        interpretado=''
        replaceindex=0
        numero=1
        total=0
        for i in range(len(self.sety.get())):
            if replaceindex==0:
                if self.sety.get()[i]!='C':
                    interpretado=interpretado+self.sety.get()[i]
                else:
                    replaceindex=1
                    interpretado=interpretado+'np.array(datos'
            else:
                try:
                    total=total*numero+int(self.sety.get()[i])
                    numero=numero*10
                except:                                    
                    interpretado=interpretado+'['+str(total-1)+'])'+self.sety.get()[i]
                    replaceindex=0
                    total=0
                    numero=1
        if replaceindex!=0:
            interpretado=interpretado+'['+str(total-1)+'])'
            replaceindex=0
            numero=1
            total=0
        try:
            yy=eval(interpretado)
        except:
            tkMessageBox.showerror("Error", 'Error al evaluar al expresion comprueba el uso de C mayuscula')
        return
    def setincertidumbres(self,*args):
        global sigma, datos
        sigma=[]
        interpretado=''
        replaceindex=0
        for i in range(len(self.stringincertidumbres.get())):
            if replaceindex==0:
                if self.stringincertidumbres.get()[i]!='C':
                    interpretado=interpretado+self.stringincertidumbres.get()[i]
                else:
                    replaceindex=1
                    interpretado=interpretado+'np.array(datos'
            else:
                replaceindex=int(self.stringincertidumbres.get()[i])-1
                interpretado=interpretado+'['+str(replaceindex)+'])'
                replaceindex=0
        try:
            sigma=eval(interpretado)
        except:
            tkMessageBox.showerror("Error", 'Error when evaluating the expersion, look for the use of capital C')
        return
        
    def save(self,*args):
        self.rutasave.set(tkFileDialog.asksaveasfilename(filetypes=(('Portable Document Format','*.pdf' ),
                                                                                       ('Portable Network Graphics','*.png'),
                                                                                       ('All files','*.*'))))
        try:
            self.fig.savefig(self.rutasave.get())
        except:
            tkMessageBox.showerror("Error", "The destination folder doesn't exist")
    def plotear(self,*args):
        if self.mantenerplot.get()==0:
            self.ax.clear()
        if self.usarincertidumbres.get()==0:
            self.ax.plot(xx,yy,linestyle=self.line.get(),marker=self.point.get())
        else:
            self.ax.errorbar(xx,yy,yerr=sigma,linestyle=self.line.get(),marker=self.point.get())
        self.canvas.draw()
        self.xmin.set(xx.min())
        self.xmax.set(xx.max())
        self.ymin.set(yy.min())
        self.ymax.set(yy.max())
        return
    def setxlabel(self,*args):
        self.window=Toplevel()
        ws = self.window.winfo_screenwidth()
        hs = self.window.winfo_screenheight()
        # calculate position x, y
        w=175
        h=75
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        ttk.Label(self.window,text='X Label').grid(column=0,row=0)
        ttk.Entry(self.window,textvar=self.xaxe).grid(column=0,row=1)
        ttk.Button(self.window,text='Ok',command=self.setxlabel2).grid(column=0,row=2)
        self.window.focus_force()          
        return
    def setxlabel2(self,*args):
        self.ax.set_xlabel(self.xaxe.get())
        self.canvas.draw()
        self.window.destroy()
        return
    def setylabel(self,*args):
        self.windowy=Toplevel()
        
        ws = self.windowy.winfo_screenwidth()
        hs = self.windowy.winfo_screenheight()
        # calculate position x, y
        w=175
        h=75
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.windowy.geometry('%dx%d+%d+%d' % (w, h, x, y))
        ttk.Label(self.windowy,text='Y Label').grid(column=0,row=0)
        ttk.Entry(self.windowy,textvar=self.yaxe).grid(column=0,row=1)
        ttk.Button(self.windowy,text='Ok',command=self.setylabel2).grid(column=0,row=2)
        self.windowy.focus_force()        
        return
    def setylabel2(self,*args):
        self.ax.set_ylabel(self.yaxe.get())
        self.canvas.draw()
        self.windowy.destroy()
        return
    def settitle(self,*args):
        self.windowt=Toplevel()
        
        ws = self.windowt.winfo_screenwidth()
        hs = self.windowt.winfo_screenheight()
        # calculate position x, y
        w=175
        h=75
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.windowt.geometry('%dx%d+%d+%d' % (w, h, x, y))
        ttk.Label(self.windowt,text='Title').grid(column=0,row=0)
        ttk.Entry(self.windowt,textvar=self.titleaxe).grid(column=0,row=1)
        ttk.Button(self.windowt,text='Ok',command=self.settitle2).grid(column=0,row=2)
        self.windowt.focus_force()  
        return
    def settitle2(self,*args):
        self.ax.set_title(self.titleaxe.get())
        self.canvas.draw()
        self.windowt.destroy()
        return
    def selectorajuste(self,*args):
        index=self.parametros.get()
        if index not in range(1,10):
            tkMessageBox.showerror("Error", 'The number of parameters must be an integer between 1 and 6')
            return
        rehacer=len(self.salida.get().split())
        if rehacer==2*index:
            p0=[]
            for i in range(index):
                p0.append(float(self.salida.get().split()[2*i+1]))
        else:
            p0=[]
            for i in range(index):
                p0.append(1)
        self.p0=np.array(p0)
        eval('self.ajuste'+str(index)+'()')
        return
    def ajuste1(self,*args):
        if self.mantenerplot.get()==0:
            self.ax.clear()
        if self.usarincertidumbres.get()==0:
            self.ax.plot(xx,yy,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion1var,xx,yy,p0=self.p0)
        else:
            self.ax.errorbar(xx,yy,yerr=sigma,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion1var,xx,yy,sigma=sigma,p0=self.p0)
        puntos=np.linspace(xx.min(),xx.max(),1000)
        self.ax.plot(puntos,self.funcion1var(puntos,salida[0]))
        self.canvas.draw()
        salidaformateada='a= %e'%salida[0]
        try:            
            incertidumbre='a= %e'%cov[0][0]**0.5
            self.incertidumbresa.set(incertidumbre)       
        except:
            self.incertidumbresa.set('Fit didnt converge')
        self.salida.set(salidaformateada)
        self.xmin.set(xx.min())
        self.xmax.set(xx.max())
        self.ymin.set(yy.min())
        self.ymax.set(yy.max())
        return
    def ajuste2(self,*args):
        if self.mantenerplot.get()==0:
            self.ax.clear()
        if self.usarincertidumbres.get()==0:
            self.ax.plot(xx,yy,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion2var,xx,yy,p0=self.p0)
        else:
            self.ax.errorbar(xx,yy,yerr=sigma,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion2var,xx,yy,sigma=sigma,p0=self.p0)
        puntos=np.linspace(xx.min(),xx.max(),1000)
        self.ax.plot(puntos,self.funcion2var(puntos,salida[0],salida[1]))
        self.canvas.draw()
        salidaformateada='a= %e'%salida[0]+' b= %1.8e'%salida[1]
        try:           
            incertidumbre='a= %e'%cov[0][0]**0.5+' b= %1.8e'%cov[1][1]**0.5
            self.incertidumbresa.set(incertidumbre)          
        except:
            self.incertidumbresa.set('Fit didnt converge')
        self.salida.set(salidaformateada)
        self.xmin.set(xx.min())
        self.xmax.set(xx.max())
        self.ymin.set(yy.min())
        self.ymax.set(yy.max())
        return
    def ajuste3(self,*args):
        if self.mantenerplot.get()==0:
            self.ax.clear()
        if self.usarincertidumbres.get()==0:
            self.ax.plot(xx,yy,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion3var,xx,yy,p0=self.p0)
        else:
            self.ax.errorbar(xx,yy,yerr=sigma,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion3var,xx,yy,sigma=sigma,p0=self.p0)
        puntos=np.linspace(xx.min(),xx.max(),1000)
        self.ax.plot(puntos,self.funcion3var(puntos,salida[0],salida[1],salida[2]))
        self.canvas.draw()
        salidaformateada='a= %e'%salida[0]+' b= %1.8e'%salida[1]+' c= %1.8e'%salida[2]
        try:        
            incertidumbre='a= %e'%cov[0][0]**0.5+' b= %1.8e'%cov[1][1]**0.5+' c= %1.8e'%cov[2][2]**0.5
            self.incertidumbresa.set(incertidumbre)   
        except:
            self.incertidumbresa.set('Fit didnt converge')
        self.salida.set(str(salidaformateada))
        self.xmin.set(xx.min())
        self.xmax.set(xx.max())
        self.ymin.set(yy.min())
        self.ymax.set(yy.max())
        return
    def ajuste4(self,*args):
        if self.mantenerplot.get()==0:
            self.ax.clear()
        if self.usarincertidumbres.get()==0:
            self.ax.plot(xx,yy,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion4var,xx,yy,p0=self.p0)
        else:
            self.ax.errorbar(xx,yy,yerr=sigma,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion4var,xx,yy,sigma=sigma,p0=self.p0)
        puntos=np.linspace(xx.min(),xx.max(),1000)
        self.ax.plot(puntos,self.funcion4var(puntos,salida[0],salida[1],salida[2],salida[3]))
        salidaformateada='a= %e'%salida[0]+' b= %1.8e'%salida[1]+' c= %1.8e'%salida[2]+' d= %1.8e'%salida[3]
        try:                
            incertidumbre='a= %e'%cov[0][0]**0.5+' b= %1.8e'%cov[1][1]**0.5+' c= %1.8e'%cov[2][2]**0.5+' d= %1.8e'%cov[3][3]**0.5
            self.incertidumbresa.set(incertidumbre)      
        except:
            self.incertidumbresa.set('Fit didnt converge')
        self.salida.set(str(salidaformateada))
        self.xmin.set(xx.min())
        self.xmax.set(xx.max())
        self.ymin.set(yy.min())
        self.ymax.set(yy.max())
        self.canvas.draw()
        return
    def ajuste5(self,*args):
        if self.mantenerplot.get()==0:
            self.ax.clear()
        if self.usarincertidumbres.get()==0:
            self.ax.plot(xx,yy,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion5var,xx,yy,p0=self.p0)
        else:
            self.ax.errorbar(xx,yy,yerr=sigma,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion5var,xx,yy,sigma=sigma,p0=self.p0)
        puntos=np.linspace(xx.min(),xx.max(),1000)
        self.ax.plot(puntos,self.funcion5var(puntos,salida[0],salida[1],salida[2],salida[3],salida[4]))
        salidaformateada='a= %e'%salida[0]+' b= %1.8e'%salida[1]+' c= %1.8e'%salida[2]+' d= %1.8e'%salida[3]+ ' f= %1.8e'%salida[4]
        try:      
            incertidumbre='a= %e'%cov[0][0]**0.5+' b= %1.8e'%cov[1][1]**0.5+' c= %1.8e'%cov[2][2]**0.5+' d= %1.8e'%cov[3][3]**0.5+ ' f= %1.8e'%cov[4][4]**0.5
            self.incertidumbresa.set(incertidumbre)        
        except:
            self.incertidumbresa.set('Fit didnt converge')        
        self.salida.set(str(salidaformateada))
        self.xmin.set(xx.min())
        self.xmax.set(xx.max())
        self.ymin.set(yy.min())
        self.ymax.set(yy.max())
        self.canvas.draw()
        return
    def ajuste6(self,*args):
        if self.mantenerplot.get()==0:
            self.ax.clear()
        if self.usarincertidumbres.get()==0:
            self.ax.plot(xx,yy,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion6var,xx,yy,p0=self.p0)
        else:
            self.ax.errorbar(xx,yy,yerr=sigma,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion6var,xx,yy,sigma=sigma,p0=self.p0)
        puntos=np.linspace(xx.min(),xx.max(),1000)
        self.ax.plot(puntos,self.funcion6var(puntos,salida[0],salida[1],salida[2],salida[3],salida[4],salida[5]))
        salidaformateada='a= %e'%salida[0]+' b= %1.8e'%salida[1]+' c= %1.8e'%salida[2]+' d= %1.8e'%salida[3]+ ' f= %1.8e'%salida[4]+' g= %1.8e'%salida[5]
        try:            
            incertidumbre='a= %e'%cov[0][0]**0.5+' b= %1.8e'%cov[1][1]**0.5+' c= %1.8e'%cov[2][2]**0.5+' d= %1.8e'%cov[3][3]**0.5+ ' f= %1.8e'%cov[4][4]**0.5+' g= %1.8e'%cov[5][5]**0.5
            self.incertidumbresa.set(incertidumbre)
        except:
            self.incertidumbresa.set('Fit didnt converge')
        self.salida.set(str(salidaformateada))
        self.xmin.set(xx.min())
        self.xmax.set(xx.max())
        self.ymin.set(yy.min())
        self.ymax.set(yy.max())
        self.canvas.draw()
        return
    def ajuste7(self,*args):
        if self.mantenerplot.get()==0:
            self.ax.clear()
        if self.usarincertidumbres.get()==0:
            self.ax.plot(xx,yy,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion7var,xx,yy,p0=self.p0)
        else:
            self.ax.errorbar(xx,yy,yerr=sigma,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion7var,xx,yy,sigma=sigma,p0=self.p0)
        puntos=np.linspace(xx.min(),xx.max(),1000)
        self.ax.plot(puntos,self.funcion7var(puntos,salida[0],salida[1],salida[2],salida[3],salida[4],salida[5],salida[6]))
        salidaformateada='a= %e'%salida[0]+' b= %1.8e'%salida[1]+' c= %1.8e'%salida[2]+' d= %1.8e'%salida[3]+ ' f= %1.8e'%salida[4]+' g= %1.8e'%salida[5]+' h= %1.8e'%salida[6]
        try:            
            incertidumbre='a= %e'%cov[0][0]**0.5+' b= %1.8e'%cov[1][1]**0.5+' c= %1.8e'%cov[2][2]**0.5+' d= %1.8e'%cov[3][3]**0.5+ ' f= %1.8e'%cov[4][4]**0.5+' g= %1.8e'%cov[5][5]**0.5+' h= %1.8e'%cov[6][6]**0.5
            self.incertidumbresa.set(incertidumbre)
        except:
            self.incertidumbresa.set('Fit didnt converge')
        self.salida.set(str(salidaformateada))
        self.xmin.set(xx.min())
        self.xmax.set(xx.max())
        self.ymin.set(yy.min())
        self.ymax.set(yy.max())
        self.canvas.draw()
        return
    def ajuste8(self,*args):
        if self.mantenerplot.get()==0:
            self.ax.clear()
        if self.usarincertidumbres.get()==0:
            self.ax.plot(xx,yy,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion8var,xx,yy,p0=self.p0)
        else:
            self.ax.errorbar(xx,yy,yerr=sigma,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion8var,xx,yy,sigma=sigma,p0=self.p0)
        puntos=np.linspace(xx.min(),xx.max(),1000)
        self.ax.plot(puntos,self.funcion8var(puntos,salida[0],salida[1],salida[2],salida[3],salida[4],salida[5],salida[6],salida[7]))
        salidaformateada='a= %e'%salida[0]+' b= %1.8e'%salida[1]+' c= %1.8e'%salida[2]+' d= %1.8e'%salida[3]+ ' f= %1.8e'%salida[4]+' g= %1.8e'%salida[5]+' h= %1.8e'%salida[6]+' i= %1.8e'%salida[7]
        try:            
            incertidumbre='a= %e'%cov[0][0]**0.5+' b= %1.8e'%cov[1][1]**0.5+' c= %1.8e'%cov[2][2]**0.5+' d= %1.8e'%cov[3][3]**0.5+ ' f= %1.8e'%cov[4][4]**0.5+' g= %1.8e'%cov[5][5]**0.5+' h= %1.8e'%cov[6][6]**0.5+' i= %1.8e'%cov[7][7]**0.5
            self.incertidumbresa.set(incertidumbre)
        except:
            self.incertidumbresa.set('Fit didnt converge')
        self.salida.set(str(salidaformateada))
        self.xmin.set(xx.min())
        self.xmax.set(xx.max())
        self.ymin.set(yy.min())
        self.ymax.set(yy.max())
        self.canvas.draw()
        return
    def ajuste9(self,*args):
        if self.mantenerplot.get()==0:
            self.ax.clear()
        if self.usarincertidumbres.get()==0:
            self.ax.plot(xx,yy,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion9var,xx,yy,p0=self.p0)
        else:
            self.ax.errorbar(xx,yy,yerr=sigma,linestyle=self.line.get(),marker=self.point.get())
            salida,cov=curve_fit(self.funcion9var,xx,yy,sigma=sigma,p0=self.p0)
        puntos=np.linspace(xx.min(),xx.max(),1000)
        self.ax.plot(puntos,self.funcion9var(puntos,salida[0],salida[1],salida[2],salida[3],salida[4],salida[5],salida[6],salida[7],salida[8]))
        salidaformateada='a= %e'%salida[0]+' b= %1.8e'%salida[1]+' c= %1.8e'%salida[2]+' d= %1.8e'%salida[3]+ ' f= %1.8e'%salida[4]+' g= %1.8e'%salida[5]+' h= %1.8e'%salida[6]+' i= %1.8e'%salida[7]+' j= %1.8e'%salida[8]
        try:            
            incertidumbre='a= %e'%cov[0][0]**0.5+' b= %1.8e'%cov[1][1]**0.5+' c= %1.8e'%cov[2][2]**0.5+' d= %1.8e'%cov[3][3]**0.5+ ' f= %1.8e'%cov[4][4]**0.5+' g= %1.8e'%cov[5][5]**0.5+' h= %1.8e'%cov[6][6]**0.5+' i= %1.8e'%cov[7][7]**0.5+' j= %1.8e'%cov[8][8]**0.5
            self.incertidumbresa.set(incertidumbre)
        except:
            self.incertidumbresa.set('Fit didnt converge')
        self.salida.set(str(salidaformateada))
        self.xmin.set(xx.min())
        self.xmax.set(xx.max())
        self.ymin.set(yy.min())
        self.ymax.set(yy.max())
        self.canvas.draw()
        return
    def funcion1var(self,x,a):
        y=eval(self.entrada.get())
        return y
    def funcion2var(self,x,a,b):
        y=eval(self.entrada.get())
        return y
    def funcion3var(self,x,a,b,c):
        y=eval(self.entrada.get())
        return y
    def funcion4var(self,x,a,b,c,d):
        y=eval(self.entrada.get())
        return y
    def funcion5var(self,x,a,b,c,d,f):
        y=eval(self.entrada.get())
        return y
    def funcion6var(self,x,a,b,c,d,f,g):
        y=eval(self.entrada.get())
        return y
    def funcion7var(self,x,a,b,c,d,f,g,h):
        y=eval(self.entrada.get())
        return y
    def funcion8var(self,x,a,b,c,d,f,g,h,i):
        y=eval(self.entrada.get())
        return y
    def funcion9var(self,x,a,b,c,d,f,g,h,i,j):
        y=eval(self.entrada.get())
        return y
    def splines(self,*args):
        global xx,yy
        ordenadox=xx*1
        ordenadoy=yy*1
        for i in range(len(xx)):
            indice=-1
            for j in range(len(xx)):
                 if xx[i]>=xx[j]:
                     indice+=1
            ordenadox[indice]=xx[i]
            ordenadoy[indice]=yy[i]
        plotx=np.linspace(ordenadox[0],ordenadox[-1],10000)
        funs=UnivariateSpline(ordenadox,ordenadoy,s=0)
        ploty=funs(plotx)    
        self.ax.plot(plotx,ploty)
        self.canvas.draw()
        return
    def splines2(self,*args):
        global xx,yy
        ordenadox=xx*1
        ordenadoy=yy*1
        for i in range(len(xx)):
            indice=-1
            for j in range(len(xx)):
                 if xx[i]>=xx[j]:
                     indice+=1
            ordenadox[indice]=xx[i]
            ordenadoy[indice]=yy[i]
        plotx=np.linspace(ordenadox[0],ordenadox[-1],10000)
        funs=UnivariateSpline(ordenadox,ordenadoy)
        ploty=funs(plotx)    
        self.ax.plot(plotx,ploty)
        self.canvas.draw()
        return        
        
    def lectura(self,archivoin):
        archivo=open(archivoin,'r')
        datos=[[]]
        archivoentrada2=''
        primera=1
        for l in archivo:
                archivoentrada2=archivoentrada2+l
                if l.startswith(r'#'):
                    pass
                else:
                    try:
                        if primera==1:
                            primera=0
                            indices=len(l.split())
                            datos[0].append(float(l.split()[0]))
                            if indices>1:
                                for columna in range(indices-1):
                                    datos.append([float(l.split()[columna+1])])
                        else:
                            for conjunto in range(len(l.split())):
                                datos[conjunto].append(float(l.split()[conjunto]))
                                
                    except:
                        pass
        archivo.close()
        return np.array(datos), archivoentrada2
    def reescalex(self,*args):
        self.ax.set_xlim([self.xmin.get(),self.xmax.get()])
        self.canvas.draw()
        return
    def reescaley(self,*args):
        self.ax.set_ylim([self.ymin.get(),self.ymax.get()])
        self.canvas.draw()
        return
    def lineal(self,*args):
        self.ax.set_xscale('linear')
        self.ax.set_yscale('linear')
        self.canvas.draw()
        return
    def logx(self,*args):
        self.ax.set_xscale('log')
        self.canvas.draw()
        return
    def logy(self,*args):
        self.ax.set_yscale('log')
        self.canvas.draw()
        return
    def rebining(self,*args):
        self.windowr=Toplevel()
        self.indicer=IntVar()
        ws = self.windowr.winfo_screenwidth()
        hs = self.windowr.winfo_screenheight()
        # calculate position x, y
        w=175
        h=75
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.windowr.geometry('%dx%d+%d+%d' % (w, h, x, y))
        ttk.Label(self.windowr,text='Rebining Index').grid(column=0,row=0)
        ttk.Entry(self.windowr,textvar=self.indicer).grid(column=0,row=1)
        ttk.Button(self.windowr,text='Ok',command=self.rebining2).grid(column=0,row=2)

        
    def rebining2(self,*args):
        global xx,yy
        self.setxcolumn()
        self.setycolumn()
        indice=self.indicer.get()
        newxx=[]
        newyy=[]
        for i in range(len(xx)/indice):
            newxx.append(xx[i*indice+(int(indice/2)-1)])
            newyy.append(np.sum(yy[i*indice:i*indice+indice]))
        xx=np.array(newxx)
        yy=np.array(newyy)
        self.windowr.destroy()
        return
    def adquisicion(self,*args):
        self.windowad=Toplevel()
        self.xi=DoubleVar()
        self.xf=DoubleVar()
        self.xi.set(self.xmin.get())
        self.xf.set(self.xmax.get())
        ws = self.windowad.winfo_screenwidth()
        hs = self.windowad.winfo_screenheight()
        # calculate position x, y
        w=175
        h=75
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.windowad.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        ttk.Label(self.windowad,text='X min').grid(column=0,row=0)
        ttk.Entry(self.windowad,textvar=self.xi).grid(column=1,row=0)
        ttk.Label(self.windowad,text='X max').grid(column=0,row=1)
        ttk.Entry(self.windowad,textvar=self.xf).grid(column=1,row=1)
        ttk.Button(self.windowad,text='Ok',command=self.adquisicion2).grid(column=1,row=2)

    def adquisicion2(self,*args):
        global xx,yy,sigma
        self.windowad.destroy()
        xnew=[]
        ynew=[]
        newsigma=[]
        xi=self.xi.get()
        xf=self.xf.get()
        for i in range(len(xx)):
            if xx[i]>=xi and xx[i]<=xf:
                xnew.append(xx[i])
                ynew.append(yy[i])
		if len(sigma)==len(xx):
                	newsigma.append(sigma[i])
            else:
                pass
        xx=np.array(xnew)
        yy=np.array(ynew)
        sigma=np.array(newsigma)
        return
def gaussian(x,a,b,c):
    return (a/(c*(2*pi)**(1/2)))*e**(-(x-b)**2/(2*c**2))
def recta(x,a,b):
    return a+b*x
def poisson(x,a,b):
    return b*a**x*np.e**(-a)/(factorial(x))
def factorial(x2):
 y2=[]
 for x in x2:
    i=1
    y=1
    while i<=x:
        y=y*i
        i+=1
    y2.append(y)
 return y2
def gausiana(x,A,mu,sig):
    return A*np.exp(-(x-mu)**2/(2*sig**2))
def cuadratic(x,a,b,c):
    return a*x**2+b*x+c
def cubic(x,a,b,c,d):
    return a*x**3+b*x**2+c*x+d
def exponentialdecay(x,a,b):
    return a*e**(-b*x)
class funcionindex:
    def funcion(self,func):
        self.funcion=func
    def index(self,ind):
        self.index=ind
    def helpp(self,hel):
        self.helpp=hel
        
            
            

root=Tk()
root.title('Point Fitter')
fitter(root)
#root.iconbitmap("icon.png")
root.mainloop()
