import matplotlib
matplotlib.use('TkAgg')

import minimalmodbus, time, csv, os, threading, shutil, sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker
##import matplotlib.dates as mdates
from matplotlib import style
from matplotlib import pylab
from threading import Thread 

##create a file with the date
tempFile = '/home/pi/tmp.csv'
outdir = 'Archives'

#style.use('fivethirtyeight')
style.use('ggplot')

#destination finale des fichiers cree
dst_co2 = '/home/pi/Rapport/Graphiques_Journee/CO2/'
dst_ph = '/home/pi/Rapport/Graphiques_Journee/pH/'
dst_qair = '/home/pi/Rapport/Graphiques_Journee/Debit Air/'
dst_qeau = '/home/pi/Rapport/Graphiques_Journee/Debit Eau/'
dst_qacide = '/home/pi/Rapport/Graphiques_Journee/Debit Acide/'
dst_pression = '/home/pi/Rapport/Graphiques_Journee/Pression/'

#creation d'une figure
fig = plt.figure(666)

#titles
fig.suptitle('CO2Gen P1 sur site (SERRES LEFORT)',fontsize=20)

#ajout de sous figure dans la figure principale avec un grid 50 x 2 et spercifie l'emplacement de chaque subplot
ax1 = plt.subplot2grid((50,2),(3,0),rowspan=15,colspan=1)
ax2 = plt.subplot2grid((50,2),(3,1),rowspan=15,colspan=1)
ax3 = plt.subplot2grid((50,2),(19,0),rowspan=15,colspan=1)
ax4 = plt.subplot2grid((50,2),(19,1),rowspan=15,colspan=1)
ax5 = plt.subplot2grid((50,2),(35,0),rowspan=15,colspan=1)

#creation de la liste pour les xticks (range max de 1 heure)
axXtickList = [n for n in range(0,3600,60)]#le temps
conversion = [str(h) for h in range(0,60)] #pour les minutes
#conversionHour = [str(h) for h in range(0,3600)] #pour les heures



def dynamicPlotting(i):
    try :
        graph_data = open(tempFile,'r').read() 
    except FileNotFoundError as ferr:
        print("File not found retrying...")
        pass
    else:
        lines = graph_data.split('\n')

        x1,x2,x3,x4,x5 = [],[],[],[],[]
        y1,y2,y3,y4,y5 = [],[],[],[],[]
        
        for line in lines :
            if len(line) > 1:
                x,y,z,k,l,m = line.split(',') 
                x1.append(int(x))
                x2.append(int(x))
                x3.append(int(x))
                x4.append(int(x))
                x5.append(int(x))
                y1.append(int(y))
                y2.append(int(z))
                y3.append(int(k))
                y4.append(int(l))
                y5.append(int(m))
                
        ax1.clear()
        ax2.clear()
        ax3.clear()
        ax4.clear()
        ax5.clear()

        
        ax1.set_title('Évolution de la concentration du CO2',fontsize=12)
        ax2.set_title('Évolution du pH',fontsize=12)
        ax3.set_title('Évolution du débit de l\'eau',fontsize=12)
        ax4.set_title('Évolution du débit d\'air',fontsize=12)
        ax5.set_title('Évolution de la Pression en sortie du procédé',fontsize=12)
        
        ax1.set_ylabel('CO2 (mg/l)',fontsize=12)
        ax2.set_ylabel('pH',fontsize=12)
        ax3.set_ylabel('Qe (m3/h)')
        ax4.set_ylabel('Qa (m3/h)',fontsize=12)
        ax5.set_ylabel('P (psi)',fontsize=12)

        ax1.set_xlabel('temps (s)',fontsize=12)
        ax2.set_xlabel('temps (s)',fontsize=12)
        ax3.set_xlabel('temps (s)',fontsize=12)
        ax4.set_xlabel('temps (s)',fontsize=12)
        ax5.set_xlabel('temps (s)',fontsize=12)
        
        #set l'interval du grid
##        ax1.set_xticks(axXtickList)
##        ax2.set_xticks(axXtickList)
##        ax3.set_xticks(axXtickList)   
##        ax4.set_xticks(axXtickList)
##        ax5.set_xticks(axXtickList)
        
##        #set ticks label
##        ax1.set_xticklabels(conversion)
##        ax2.set_xticklabels(conversion)
##        ax3.set_xticklabels(conversion)   
##        ax4.set_xticklabels(conversion)
##        ax5.set_xticklabels(conversion)

        #set l'intervalle des yaxis
        ax1.yaxis.set_major_locator(ticker.MaxNLocator(10))
        ax2.yaxis.set_major_locator(ticker.MaxNLocator(10))
        ax3.yaxis.set_major_locator(ticker.MaxNLocator(10))
        ax4.yaxis.set_major_locator(ticker.MaxNLocator(10))
        ax5.yaxis.set_major_locator(ticker.MaxNLocator(10))
        
        #graphe les figures
        ax1.plot(x1,y1,linewidth=2)
        ax2.plot(x2,y2,linewidth=2)
        ax3.plot(x3,y3,linewidth=2)  
        ax4.plot(x4,y4,linewidth=2)
        ax5.plot(x5,y5,linewidth=2)

        plt.tight_layout()

ani = animation.FuncAnimation(fig, dynamicPlotting, interval=15000)
plt.show()
