import minimalmodbus, time, csv, os, threading 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from threading import Thread

#############################################################
#Il faut arranger la dimension des graphiques pour que le
#grid puisser fonctionner
#Il ne faut qu'afficher les 60 dernieres entree
#
#Optionnel : faire les rapports par jour et par semaine 
#
#############################################################

#create a file with the date
tempFile = './tmp.csv'
dataLogFile = 'dataLogging' + time.strftime("%Y-%m-%d") + '.csv'
infich = './' + dataLogFile

style.use('fivethirtyeight')

#creation d'une figure

fig = plt.figure()
i,j,k,l,m,n = 0,0,0,0,0,0

#titles
fig.suptitle('CO2Gen live',fontsize=20)
#ajout de sous figure dans la figure principale
ax1 = fig.add_subplot(5,2,1)
ax2 = fig.add_subplot(5,2,2)
ax3 = fig.add_subplot(5,2,3)
ax4 = fig.add_subplot(5,2,4)
ax5 = fig.add_subplot(5,1,5)


#creation de liste pour les yticks (l'intervalle du grid)
ax1YtickList = [i for i in range(0,200,2)]#Co2
ax2YtickList = [j for j in range(0,14)]#pH
ax3YtickList = [k for k in range(0,300,2)]#qEau
ax4YtickList = [l for l in range(0,138,2)]#qAir
ax5YtickList = [m for m in range(0,232,2)]#pressure
#creation de la liste pour les xticks (range max de 1 heure)
axXtickList = [n for n in range(0,3600,60)]#le temps
conversion =[str(h) for h in range(0,60)]



def shiftFile(line_count):
    #rewrite tmpfile to newfile then rename newfile
    tmpfile = open(tempFile,'r')
    newfile = open('newfile.csv', 'a')
    csv_writer = csv.writer(newfile)

    sp = []
    skip_to_line = 0
    for lines in tmpfile:
        skip_to_line+=1
        if skip_to_line == 1:#essentiellement je skip la premiere ligne
            for lines in tmpfile:
                sp = lines.split(',')
                csv_writer.writerow([int(sp[0]),int(sp[1]),int(sp[2]),int(sp[3]),
                                     int(sp[4]), int(sp[5])])
                
    newfile.close() # close the file
    tmpfile.close()
    os.remove(tempFile)#remove temporary file
    os.rename('newfile.csv','tmp.csv') #rename newfile to oldfile


def checkFile(tmpfile):
    line_count = 0
    for lines in tmpfile:
        line_count += 1
    print(line_count)
    if line_count == 10 :
        tmpfile.close()
        shiftFile(line_count)
        


    

#Lecture des sensors avec minimalmodbus 
def sensorReadings(p2k,cntx):
    
    DI = p2k.read_bit(0)#global di == 0, Using it for testing 
    #read registers
    Co2 = p2k.read_register(17,numberOfDecimals=0,functioncode=4)
    qEau = p2k.read_register(2,numberOfDecimals=0,functioncode=4)
    qAir = p2k.read_register(7,numberOfDecimals=0,functioncode=4)
    pH = p2k.read_register(5,numberOfDecimals=0,functioncode=4) 
    pressure = p2k.read_register(11,numberOfDecimals=0,functioncode=4)
    cntx+=1


    return Co2,pH,qEau,qAir,pressure,cntx,DI


def writingToFile(Co2,pH,qEau,qAir,pressure,cntx,infich,DI):
    if time.strftime("%H:%m") == '23:55':
        infich.close()#close the infich file 
        os.remove("/home/pi/tmpfile.csv")#remove the created file
        DI = 1
    else :
        acquisitionTime = 1 # global
        
        #ouverture du fichier CSV en mode ecriture et ecrire dans le fichier
        with open(tempFile,'a') as tmpfile:
            with open(infich, 'a') as csvfile :

                #ecrit dans le fichier CSV
                writer1 = csv.writer(tmpfile)#tmp file
                writer2 = csv.writer(csvfile)#csv file
                
                writer1.writerow([cntx, Co2, pH, qEau, qAir,pressure])#tmp file
                writer2.writerow([time.strftime("%Y-%m-%d"),time.strftime("%H:%M"),"ND","ND", qEau, "ND",
                                  qAir, pH,"ND","ND","ND","ND","ND", Co2,"ND"])
                tmpfile.close()#to save the file (for animate)
                csvfile.close()
                #a toutes les XX secondes
                time.sleep(acquisitionTime) 


        #Fonction qui va regarder le nombre de ligne du fichier
        #et qui va shifter le contenu du fichier vers le haut.
        
        with open(tempFile,'r') as tmpfile:        
            checkFile(tmpfile)
            tmpfile.close()
    
    return DI


#fonction qui graphe dynamiquement les donnee qu'on recoit a chaque 5 secondes
#Idealement, cest de garder les 30 dernieres minutes de plotting


def dynamicPlotting(i):
    graph_data = open(tempFile,'r').read()
    lines = graph_data.split('\n')
    #pas sure si ca va marcher
    x1,x2,x3,x4,x5 = [],[],[],[],[] #ne pas oublier de rajouter x5 et y5 pour qAcide
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

    
    ax1.set_title('Variation du [CO2]',fontsize=12)
    ax2.set_title('Variation du [pH]',fontsize=12)
    ax3.set_title('Debit de l\'eau',fontsize=12)
    ax4.set_title('Debit d\'air',fontsize=12)
    ax5.set_title('Pression de la ligne',fontsize=12)
    
    ax1.set_ylabel('[CO2]',fontsize=12)
    ax2.set_ylabel('[pH]',fontsize=12)
    ax3.set_ylabel('qEau')
    ax4.set_ylabel('qAir',fontsize=12)
    ax5.set_ylabel('Pressure',fontsize=12)

    ax1.set_xlabel('temps (s)',fontsize=12)
    ax2.set_xlabel('temps (s)',fontsize=12)
    ax3.set_xlabel('temps (s)',fontsize=12)
    ax4.set_xlabel('temps (s)',fontsize=12)
    ax5.set_xlabel('temps (s)',fontsize=12)
    
    #set l'interval du grid 
    ax1.set_yticks(ax1YtickList)
    ax2.set_yticks(ax2YtickList)
    ax3.set_yticks(ax3YtickList)    
    ax4.set_yticks(ax4YtickList)
    ax5.set_yticks(ax5YtickList)
    
    #set l'interval du grid
    ax1.set_xticks(axXtickList,conversion)
    ax2.set_xticks(axXtickList,conversion)
    ax3.set_xticks(axXtickList,conversion)   
    ax4.set_xticks(axXtickList,conversion)
    ax5.set_xticks(axXtickList,conversion)
    
    #graphe les figures
    ax1.plot(x1,y1,linewidth=2)
    ax2.plot(x2,y2,linewidth=2)
    ax3.plot(x3,y3,linewidth=2)  
    ax4.plot(x4,y4,linewidth=2)
    ax5.plot(x5,y5,linewidth=2)

    plt.tight_layout()
    

def startLog():
    cntx = 0
    p2k = minimalmodbus.Instrument('/dev/ttyUSB0',1)
    DI = p2k.read_bit(0)
    
    while DI != 1 :
        Co2,pH,qEau,qAir,pressure,cntx,DI = sensorReadings(p2k,cntx)
        writingToFile(Co2,pH,qEau,qAir,pressure,cntx,infich,DI)









#ouvre 1 process et effectue le code
if __name__ == '__main__' :
    #if the file doesn't exist we create it and write on it
    if os.path.isfile(infich) == False:

        #ecrire le header du infich
        print("writing f header")
        f = open(infich,'a')
        writing = csv.writer(f)
        writing.writerow(["date", "heure", "prenom", "source", "debit_eau", "debit_acide",
                          "debit_air", "ph_sensorex", "carbonates_uv", "carbonates_sortie",
                          "pression_eau_sortie_filtre", "pression_air_entree", "pression_air",
                          "concentration_co2", "ratio_debit", "ratio_debit_eau_pression_eau"])
        f.close()
        print("f closing")
        Thread(target=startLog).start()
        time.sleep(3) #pour laisser le temps d'ecrire quelques lignes
        
        ani = animation.FuncAnimation(fig, dynamicPlotting, frames=50, interval=1000)
        plt.show()
    
    else :
        print("file already exists")























    

