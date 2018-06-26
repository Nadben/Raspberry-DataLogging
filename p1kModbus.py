import matplotlib
matplotlib.use('TkAgg')

import minimalmodbus, time, csv, os, threading, shutil, sys 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker
from matplotlib import style
from threading import Thread

#############################################################
#
#changer DI = p2k.read_bit(0) ---> DI = 0
#Tester ca Vendredi toute la journeee
# 
#Optionnel : faire les rapports par semaine 
#
#############################################################

#create a file with the date
tempFile = './tmp.csv'
dataLogFile = 'dataLogging' + time.strftime("%Y-%m-%d") + '.csv'
infich = './' + dataLogFile
outdir = 'Archives'
style.use('fivethirtyeight')



incrementFile = 0
#creation d'une figure
fig = plt.figure()
#titles
fig.suptitle('CO2Gen live',fontsize=20)
#ajout de sous figure dans la figure principale
ax1 = fig.add_subplot(5,2,1)
ax2 = fig.add_subplot(5,2,2)
ax3 = fig.add_subplot(5,2,3)
ax4 = fig.add_subplot(5,2,4)
ax5 = fig.add_subplot(5,1,5)


#creation de la liste pour les xticks (range max de 1 heure)
axXtickList = [n for n in range(0,3600,60)]#le temps
conversion =[str(h) for h in range(0,60)]





def fileCopy(src,dest):
    
    dest_dir = os.path.dirname(dest)

    try :
        os.makedirs(dest)
    except os.error as e:
        pass

    shutil.move(src,dest)



def shiftFile(line_count):
    #rewrite tmpfile to newfile then rename newfile
    with open(tempFile,'r') as tmpfile :
        with open('newfile.csv', 'a') as newfile :
            csv_writer = csv.writer(newfile)
            sp = []
            skip_to_line = 0
            for lines in tmpfile:
                skip_to_line+=1
                if skip_to_line == 1:#essentiellement je skip la premiere ligne
                    for lines in tmpfile:
                        sp = lines.split(',')
                        csv_writer.writerow(
                            [int(sp[0]), int(sp[1]), int(sp[2]),
                             int(sp[3]), int(sp[4]), int(sp[5])]
                            )
                        
    os.remove(tempFile)#remove temporary file
    os.rename('newfile.csv','tmp.csv') #rename newfile to oldfile


def checkFile(tmpfile):
    line_count = 0
    for lines in tmpfile:
        line_count += 1

    if line_count == 60 :
        tmpfile.close()
        shiftFile(line_count)
        


    

#Lecture des sensors avec minimalmodbus 
def sensorReadings(p2k,cntx):
    
    DI = 0
    Co2 = p2k.read_register(17,numberOfDecimals=0,functioncode=4)
    qEau = p2k.read_register(2,numberOfDecimals=0,functioncode=4)
    qAir = p2k.read_register(7,numberOfDecimals=0,functioncode=4)
    pH = p2k.read_register(5,numberOfDecimals=0,functioncode=4) 
    pressure = p2k.read_register(11,numberOfDecimals=0,functioncode=4)
    cntx+=1


    return Co2,pH,qEau,qAir,pressure,cntx,DI


def writingToFile(Co2,pH,qEau,qAir,pressure,cntx,infich,DI):
    if time.strftime("%H:%M") == '16:42':
        print("it's time to STOP")
        #os.remove("/home/pi/tmpfile.csv")#remove the created file
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
                writer2.writerow([time.strftime("%Y-%m-%d"),time.strftime("%H:%M"), 0, 0, qEau, 0,
                                  qAir, pH, 0, 0, 0, 0, 0, Co2, 0])
        
        time.sleep(acquisitionTime) 
        

        #Fonction qui va regarder le nombre de ligne du fichier
        #et qui va shifter le contenu du fichier vers le haut.
        
        with open(tempFile,'r') as tmpfile:        
            checkFile(tmpfile)
    
    return DI


#fonction qui graphe dynamiquement les donnee qu'on recoit a chaque 5 secondes
#Idealement, cest de garder les 30 dernieres minutes de plotting

def threadPlot():
    def dynamicPlotting(i):
##        DI = p2k.read_bit(0)
##        print(DI)
##        
##        if DI == 1:
##            plt.close(fig)
##            exit()

##        else:
        
        
        graph_data = open(tempFile,'r').read()
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
        ax1.set_xticks(axXtickList,conversion)
        ax2.set_xticks(axXtickList,conversion)
        ax3.set_xticks(axXtickList,conversion)   
        ax4.set_xticks(axXtickList,conversion)
        ax5.set_xticks(axXtickList,conversion)

        #set l'intervalle des yaxis
        ax1.yaxis.set_major_locator(ticker.MaxNLocator(5))
        ax2.yaxis.set_major_locator(ticker.MaxNLocator(5))
        ax3.yaxis.set_major_locator(ticker.MaxNLocator(5))
        ax4.yaxis.set_major_locator(ticker.MaxNLocator(5))
        ax5.yaxis.set_major_locator(ticker.MaxNLocator(5))
        
        #graphe les figures
        ax1.plot(x1,y1,linewidth=2)
        ax2.plot(x2,y2,linewidth=2)
        ax3.plot(x3,y3,linewidth=2)  
        ax4.plot(x4,y4,linewidth=2)
        ax5.plot(x5,y5,linewidth=2)

        plt.tight_layout()
            
    ani = animation.FuncAnimation(fig, dynamicPlotting, interval=1000)
    plt.show()


def startLog():
    cntx = 0
    p2k = minimalmodbus.Instrument('/dev/ttyUSB0',1)
    DI = 0
    
    while DI != 1 :
        Co2,pH,qEau,qAir,pressure,cntx,DI = sensorReadings(p2k,cntx)
        DI = writingToFile(Co2,pH,qEau,qAir,pressure,cntx,infich,DI)
        print(DI)


    print("moving the files")
    #Move le fichier datalog dans le dossier archives
    fileCopy(infich,outdir)
    print("deleting tmp files")
    #une fois que tout est fini remove le fichier temporary et datalog du root
    os.remove('./tmp.csv')
##    print("Sayonara")


#ouvre 1 process et effectue le code
if __name__ == '__main__' :
    #if the file doesn't exist we create it and write on it

    p2k = minimalmodbus.Instrument('/dev/ttyUSB0',1)
    if os.path.isfile(infich) == False:

        #ecrire le header du infich
        with open(infich,'a') as f :
            writing = csv.writer(f)
            writing.writerow(["date", "heure", "prenom", "source", "debit_eau", "debit_acide",
                              "debit_air", "ph_sensorex", "carbonates_uv", "carbonates_sortie",
                              "pression_eau_sortie_filtre", "pression_air_entree", "pression_air",
                              "concentration_co2", "ratio_debit", "ratio_debit_eau_pression_eau"])
  
        Thread(target=startLog).start()
        #Make it a daemonic Thread so i can forget about it when i kill the script
        threadPlot()
        
    
    else :
        print("file already exists")






















    

