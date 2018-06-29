import matplotlib
matplotlib.use('TkAgg')

import minimalmodbus, time, csv, os, threading, shutil, sys 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker
from matplotlib import style
from matplotlib import pylab
from threading import Thread

##create a file with the date
tempFile = './tmp.csv'
outdir = 'Archives'

#style.use('fivethirtyeight')
style.use('ggplot')

#destination finale des fichiers cree
dst_co2 = './Rapport/Graphiques_Journee/CO2/'
dst_ph = './Rapport/Graphiques_Journee/pH/'
dst_qair = './Rapport/Graphiques_Journee/Debit Air/'
dst_qeau = './Rapport/Graphiques_Journee/Debit Eau/'
dst_qacide = './Rapport/Graphiques_Journee/Debit Acide/'
dst_pression = './Rapport/Graphiques_Journee/Pression/'

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
conversion = [str(h) for h in range(0,60)]

incrementFile = 0
cnt = 0

def plottingDailyReport(graphName,infich_2):

    fig1 = plt.figure()
    fig1.suptitle('Co2',fontsize=20)
    fig_CO2 = fig1.add_subplot(111)
    
    fig2 = plt.figure()
    fig2.suptitle('pH',fontsize=20)
    fig_pH = fig2.add_subplot(111)

    fig3 = plt.figure()
    fig3.suptitle('qAir',fontsize=20)
    fig_qAir = fig3.add_subplot(111)

    fig4 = plt.figure()
    fig4.suptitle('qEau',fontsize=20)
    fig_qEau = fig4.add_subplot(111)

    fig5 = plt.figure()
    fig5.suptitle('Pressure',fontsize=20)
    fig_pressure = fig5.add_subplot(111)

    fig6 = plt.figure()
    fig6.suptitle('qAcid',fontsize=20)
    fig_qAcid = fig6.add_subplot(111)

    fig_CO2.set_ylabel('[CO2]',fontsize=12)
    fig_pH.set_ylabel('[pH]',fontsize=12)
    fig_qEau.set_ylabel('qEau',fontsize=12)
    fig_qAir.set_ylabel('qAir',fontsize=12)
    fig_qAcid.set_ylabel('qAcid',fontsize=12)
    fig_pressure.set_ylabel('Pressure',fontsize=12)

    fig_CO2.set_xlabel('temps (s)',fontsize=12)
    fig_pH.set_xlabel('temps (s)',fontsize=12)
    fig_qEau.set_xlabel('temps (s)',fontsize=12)
    fig_qAir.set_xlabel('temps (s)',fontsize=12)
    fig_qAcid.set_xlabel('temps (s)',fontsize=12)
    fig_pressure.set_xlabel('temps (s)',fontsize=12)

    fig_CO2.yaxis.set_major_locator(ticker.MaxNLocator(5))
    fig_pH.yaxis.set_major_locator(ticker.MaxNLocator(5))
    fig_qEau.yaxis.set_major_locator(ticker.MaxNLocator(5))
    fig_qAir.yaxis.set_major_locator(ticker.MaxNLocator(5))
    fig_qAcid.yaxis.set_major_locator(ticker.MaxNLocator(5))
    fig_pressure.yaxis.set_major_locator(ticker.MaxNLocator(5))

    fig_CO2.yaxis.set_minor_locator(ticker.MaxNLocator(5))
    fig_pH.yaxis.set_major_locator(ticker.MaxNLocator(5))
    fig_qEau.yaxis.set_major_locator(ticker.MaxNLocator(5))
    fig_qAir.yaxis.set_major_locator(ticker.MaxNLocator(5))
    fig_qAcid.yaxis.set_major_locator(ticker.MaxNLocator(5))
    fig_pressure.yaxis.set_major_locator(ticker.MaxNLocator(5))
    
    co2_to_plot, qEau_to_plot, pH_to_plot, pressure_to_plot, qAcid_to_plot, qAir_to_plot, cntx = [],[],[],[],[],[],[]
    data_set = open(infich_2,'r').read()
    lines = data_set.split('\n')    
    i = 0
    
    
    for line in lines :
        i+=1
        
        if i in range(2,len(lines)):#skip header
            cntx.append(i)
            a,b,c,d,e,f,g,h,k,l,m,n,o,p,q = line.split(',')
            co2_to_plot.append(int(p))
            qEau_to_plot.append(int(e))
            pH_to_plot.append(int(h))
            pressure_to_plot.append(int(k))
            qAcid_to_plot.append(int(f))
            qAir_to_plot.append(int(g))
            


    #Plot processing
    fig_CO2.plot(cntx,co2_to_plot,linewidth=2)
    fig1.savefig(dst_co2+graphName)
    
    fig_pH.plot(cntx,pH_to_plot)
    fig2.savefig(dst_ph+graphName)
    
    fig_qAir.plot(cntx,qAir_to_plot,linewidth=2)
    fig3.savefig(dst_qair+graphName)

    fig_qEau.plot(cntx,qEau_to_plot,linewidth=2)
    fig4.savefig(dst_qeau+graphName)

    fig_pressure.plot(cntx,pressure_to_plot,linewidth=2)
    fig5.savefig(dst_pression+graphName)
    
    fig_qAcid.plot(cntx,qAcid_to_plot,linewidth=2)
    fig6.savefig(dst_qacide+graphName)

##    plt.close(fig1)
##    plt.close(fig2)
##    plt.close(fig3)
##    plt.close(fig4)
##    plt.close(fig5)
##    plt.close(fig6)

    

    


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
                if skip_to_line == 1:#skip first line
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
##    DI = p2k.read_bit(0)
    
    DI = 0
    Co2 = p2k.read_register(0,functioncode=3)
    qEau = p2k.read_register(2,functioncode=3)
    qAir = p2k.read_register(4,functioncode=3)
    pH = p2k.read_register(6,functioncode=3) 
    pressure = p2k.read_register(8,functioncode=3)
    qAcid = p2k.read_register(10,functioncode=3)
    cntx+=1
    
    
    return Co2,pH,qEau,qAir,pressure,qAcid,cntx,DI


def writingToFile(Co2,pH,qEau,qAir,pressure,qAcid,cntx,infich,DI):


    
    if time.strftime("%H:%M") == '23:55':
        print("it's time to STOP")
        DI = 1
        
    #Bloc de test
        
##    elif time.strftime("%H:%M") == '15:20':
##        print("it's time to STOP")
##        DI = 1
##    elif time.strftime("%H:%M") == '15:25':
##        print("it's time to STOP")
##        DI = 1
##    elif time.strftime("%H:%M") == '15:30':
##        print("it's time to STOP")
##        DI = 1
##    elif time.strftime("%H:%M") == '15:35':
##        print("it's time to STOP")
##        DI = 1
##    elif time.strftime("%H:%M") == '15:40':
##        print("it's time to STOP")
##        DI = 1
##    elif time.strftime("%H:%M") == '15:45':
##        print("it's time to STOP")
##        DI = 1   
            

    else:
        acquisitionTime = 2 # global
        
        #ouverture du fichier CSV en mode ecriture et ecrire dans le fichier
        with open(tempFile,'a') as tmpfile:
            with open(infich, 'a') as csvfile :

                #ecrit dans le fichier CSV
                writer1 = csv.writer(tmpfile)#tmp file
                writer2 = csv.writer(csvfile)#csv file
                
                writer1.writerow([cntx, Co2, pH, qEau, qAir,pressure])#tmp file
                writer2.writerow([time.strftime("%Y-%m-%d"),time.strftime("%H:%M"), 0, 0, qEau, qAcid,
                                  qAir, pH, 0, 0, pressure, 0, 0, Co2, 0])
        
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
        try :
            graph_data = open(tempFile,'r').read()
        except FileNotFoundError as ferr:
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

    ani = animation.FuncAnimation(fig, dynamicPlotting, interval=5000)
    plt.show()



def startLog():

    p2k = minimalmodbus.Instrument('/dev/ttyUSB0',1)
##    DI = p2k.read_bit(0)
    cntx,cnt,DI,t =0,7,0,0
    
    while True:

        if t != 1 :
            
 
            dataLogFile = 'dataLogging' + time.strftime("%Y-%m-%d") + '.csv'
            infich = './' + dataLogFile
            infich_2 = './Archives/dataLogging' + time.strftime("%Y-%m-%d") + '.csv'
            infich_3 = './Archives/Weekly/dataLogging' + time.strftime("%Y-%m") + '.csv'
            graphName = 'graph' + time.strftime("%Y-%m-%d") + '.png'
            
                        
            with open(infich,'a') as f :
                writing = csv.writer(f)
                writing.writerow(["date", "heure", "prenom", "source", "debit_eau", "debit_acide",
                                  "debit_air", "ph_sensorex", "carbonates_uv", "carbonates_sortie",
                                  "pression_eau_sortie_filtre", "pression_air_entree", "pression_air",
                                  "concentration_co2", "ratio_debit", "ratio_debit_eau_pression_eau"])
            t = 1
                
        elif cnt == 7:
            print(cnt)

            #ecrire le header du infich, car c'est une autre semaine
            with open(infich_3,'a') as f :
                writing = csv.writer(f)
                writing.writerow(["date", "heure", "prenom", "source", "debit_eau", "debit_acide",
                                  "debit_air", "ph_sensorex", "carbonates_uv", "carbonates_sortie",
                                  "pression_eau_sortie_filtre", "pression_air_entree", "pression_air",
                                  "concentration_co2", "ratio_debit", "ratio_debit_eau_pression_eau"])


            cnt = 0
            

        elif DI != 1 :
            
            Co2,pH,qEau,qAir,pressure,qAcid,cntx,DI = sensorReadings(p2k,cntx)
            DI = writingToFile(Co2,pH,qEau,qAir,pressure,qAcid,cntx,infich,DI)
     
        
        else :
            
            print("moving the files")
            #Move le fichier datalog dans le dossier archives
            fileCopy(infich,outdir)
            print("Writting the daily report")
            plottingDailyReport(graphName,infich_2)
            print("Writting the monthly report")
            cnt = weeklyReport(cnt,infich_2,infich_3)
            #wait 5 minutes until tomorrow 
            time.sleep(300)
            #time.sleep(60) #For testing
            DI,t = 0,0 #restart the loop
            
                
def writingWeeklyReport(cnt,Co2,pH,qEau,qAir,pressure,infich_3):
    cnt += 1
    if cnt <= 7 :
        with open(infich_3, 'a') as csvfile : 
            #ecrit dans le fichier CSV
            writer1 = csv.writer(csvfile)#csv file
            writer1.writerow([time.strftime("%Y-%m-%d"),time.strftime("%H:%M"), 0, 0, qEau, 0,
                              qAir, pH, 0, 0, 0, 0, 0, Co2, 0])
    else :
        cnt = 0

    return cnt


def weeklyReport(cnt,infich_2,infich_3):

    # opening the daily CSV reports

    a,b,c,d,e,f,g,h,k,l,m,n,o,p,q = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[]

    i=0
    file = open(infich_2, 'r').read()

    lines = file.split('\n')

    for line in lines:
        i+=1
        if len(line) > 1 and i > 1:
            a1,b1,c1,d1,e1,f1,g1,h1,k1,l1,m1,n1,o1,p1,q1 = line.split(',')
            
            e.append(int(e1)) #debit d'eau
            f.append(int(f1)) #debit acide
            g.append(int(g1)) #debit air
            h.append(int(h1)) #pH sensorex
            p.append(int(p1)) #Co2
            

    s1,s2,s3,s4,s5 = 0,0,0,0,0
    
    s1 = round(sum(e)/len(e),2)
    s2 = round(sum(f)/len(f),2)
    s3 = round(sum(g)/len(g),2)
    s4 = round(sum(h)/len(h),2)
    s5 = round(sum(p)/len(p),2)

    cnt = writingWeeklyReport(cnt,s5,s4,s1,s3,s2,infich_3)

    return cnt

    


#ouvre 1 process et effectue le code
if __name__ == '__main__' :
    #if the file doesn't exist we create it and write on it

    p2k = minimalmodbus.Instrument('/dev/ttyUSB0',1)

    Thread(target=startLog).start()
    threadPlot()

















    

