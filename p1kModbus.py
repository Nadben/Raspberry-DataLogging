#!/usr/bin/env python

import matplotlib
matplotlib.use('TkAgg')

import minimalmodbus, time, csv, os, threading, shutil, sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker

##import matplotlib.dates as mdates
from matplotlib import style
from matplotlib import pylab
from threading import Thread #not used



"""
Date : 03/07/2018
Code fait par Nadir Benabdesselam

Description:

    This script was written for OCO Technologies. It's a simple
    datalogger for remote use.


"""

headerList = ["date", "heure", "prenom", "source", "debit_eau", "debit_acide",
              "debit_air", "ph_sensorex", "carbonates_uv", "carbonates_sortie",
              "pression_eau_sortie_filtre", "pression_air_entree", "pression_air",
              "concentration_co2", "ratio_debit", "ratio_debit_eau_pression_eau"]




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

cnt = 0

def plottingDailyReport(graphName,infich_2):

    fig1 = plt.figure(1)
    fig1.suptitle('Co2',fontsize=20)
    fig_CO2 = fig1.add_subplot(111)

    fig2 = plt.figure(2)
    fig2.suptitle('pH',fontsize=20)
    fig_pH = fig2.add_subplot(111)

    fig3 = plt.figure(3)
    fig3.suptitle('qAir',fontsize=20)
    fig_qAir = fig3.add_subplot(111)

    fig4 = plt.figure(4)
    fig4.suptitle('qEau',fontsize=20)
    fig_qEau = fig4.add_subplot(111)

    fig5 = plt.figure(5)
    fig5.suptitle('Pressure',fontsize=20)
    fig_pressure = fig5.add_subplot(111)

    fig6 = plt.figure(6)
    fig6.suptitle('qAcid',fontsize=20)
    fig_qAcid = fig6.add_subplot(111)

    fig_CO2.set_ylabel('CO2 (mg/l)',fontsize=12)
    fig_pH.set_ylabel('pH',fontsize=12)
    fig_qEau.set_ylabel('Qe (m3/h)',fontsize=12)
    fig_qAir.set_ylabel('Qa (m3/h)',fontsize=12)
    fig_qAcid.set_ylabel('Q acid',fontsize=12)
    fig_pressure.set_ylabel('P (psi)',fontsize=12)

    fig_CO2.set_xlabel('temps (Min)',fontsize=12)
    fig_pH.set_xlabel('temps (Min)',fontsize=12)
    fig_qEau.set_xlabel('temps (Min)',fontsize=12)
    fig_qAir.set_xlabel('temps (Min)',fontsize=12)
    fig_qAcid.set_xlabel('temps (Min)',fontsize=12)
    fig_pressure.set_xlabel('temps (Min)',fontsize=12)

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
            co2_to_plot.append(float(p))
            qEau_to_plot.append(float(e))
            pH_to_plot.append(float(h))
            pressure_to_plot.append(float(k))
            qAcid_to_plot.append(float(f))
            qAir_to_plot.append(float(g))

    #Plot processing
    fig_CO2.plot(cntx,co2_to_plot,linewidth=2)
    fig1.savefig(dst_co2+graphName)
    plt.close(fig1)


    fig_pH.plot(cntx,pH_to_plot)
    fig2.savefig(dst_ph+graphName)
    plt.close(fig2)


    fig_qAir.plot(cntx,qAir_to_plot,linewidth=2)
    fig3.savefig(dst_qair+graphName)
    plt.close(fig3)


    fig_qEau.plot(cntx,qEau_to_plot,linewidth=2)
    fig4.savefig(dst_qeau+graphName)
    plt.close(fig4)


    fig_pressure.plot(cntx,pressure_to_plot,linewidth=2)
    fig5.savefig(dst_pression+graphName)
    plt.close(fig5)


    fig_qAcid.plot(cntx,qAcid_to_plot,linewidth=2)
    fig6.savefig(dst_qacide+graphName)
    plt.close(fig6)





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
                        #essai sans type cast int
                        csv_writer.writerow(
                            [int(sp[0]), float(sp[1]), float(sp[2]),
                             float(sp[3]), float(sp[4]), float(sp[5])]
                            )

    os.remove(tempFile)#remove temporary file
    os.rename('newfile.csv','tmp.csv') #rename newfile to oldfile


def checkFile(tmpfile):
    line_count = 0
    for lines in tmpfile:
        line_count += 1

    if line_count == 180 :
        shiftFile(line_count)





#Lecture des sensors avec minimalmodbus
def sensorReadings(p2k,cntx):
##            DI = p2k.read_bit(0)
    #faire un try except block OSError et gérer l'erreur
    while True:
        try :
            Co2 = p2k.read_register(0,functioncode=3)
        except OSError as ose :
            print("couldn't communicate with the plc! Verify the connection please. ")
            time.sleep(10)
            continue
        else :
            break

 
    DI = 0
    Co2 = p2k.read_register(0,functioncode=3)
    pressure = p2k.read_register(1,functioncode=3)
    qEau = p2k.read_register(2,functioncode=3)
    pH = p2k.read_register(3,functioncode=3)
##        qAcid = p2k.read_register(5,functioncode=3)
    qAcid = 0
    qAir = 0
    cntx+=1

    ## parametres de conversions
    qEau *= (77 / 8191)
    Co2 *= (120000 / 8191)
    pH *= ((1400 / 8191)/100)
    pressure *= ((600 / 8191 )/10)


    return Co2,pH,qEau,qAir,pressure,qAcid,cntx,DI


def writingToFile(Co2,pH,qEau,qAir,pressure,qAcid,cntx,infich,DI):

    if time.strftime("%H:%M") == '23:55':
        print("it's time to STOP")
        DI = 1

    #Bloc de test

##    if time.strftime("%H:%M") == '11:58':
##        print("it's time to STOP")
##        DI = 1
##    if time.strftime("%H:%M") == '13:42':
##        print("it's time to STOP")
##        DI = 1
##    elif time.strftime("%H:%M") == '13:45':
##        print("it's time to STOP")
##        DI = 1
##    elif time.strftime("%H:%M") == '13:48':
##        print("it's time to STOP")
##        DI = 1
##    elif time.strftime("%H:%M") == '13:53':
##        print("it's time to STOP")
##        DI = 1
##    elif time.strftime("%H:%M") == '13:56':
##        print("it's time to STOP")
##        DI = 1


    else:
        acquisitionTime = 1 # global

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



def writingWeeklyReport(cnt,Co2,pH,qEau,qAir,pressure,infich_3):
    cnt += 1
    print(cnt)
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

            e.append(float(e1)) #debit d'eau
            f.append(float(f1)) #debit acide
            g.append(float(g1)) #debit air
            h.append(float(h1)) #pH sensorex
            p.append(float(p1)) #Co2


    s1,s2,s3,s4,s5 = 0,0,0,0,0

    s1 = round(sum(e)/len(e),2)
    s2 = round(sum(f)/len(f),2)
    s3 = round(sum(g)/len(g),2)
    s4 = round(sum(h)/len(h),2)
    s5 = round(sum(p)/len(p),2)

    cnt = writingWeeklyReport(cnt,s5,s4,s1,s3,s2,infich_3)

    return cnt





def startLog():
    minimalmodbus.BAUDRATE = 9600
    p2k = minimalmodbus.Instrument('/dev/ttyUSB0',1)
##    DI = p2k.read_bit(0)
    cntx,cnt,DI,t = 0,7,0,0

    while True:

        if t != 1 :


            dataLogFile = 'dataLogging' + time.strftime("%Y-%m-%d") + '.csv'
            infich = './' + dataLogFile
            infich_2 = './Archives/dataLogging' + time.strftime("%Y-%m-%d") + '.csv'
            infich_3 = './Archives/Weekly/dataLogging' + time.strftime("%Y-%m") + '.csv'
            graphName = 'graph' + time.strftime("%Y-%m-%d") + '.png'


            if os.path.isfile(infich) :
                os.remove(infich)

            else :
                with open(infich,'a') as f :
                    writing = csv.writer(f)
                    writing.writerow(headerList)
                t = 1

        elif cnt == 7:


            #ecrire le header du infich, car c'est une autre semaine
            with open(infich_3,'a') as f :
                writing = csv.writer(f)
                writing.writerow(headerList)


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




if __name__ == '__main__' :

    # removing any temporary file before starting log
    # this is here only if there is a restart during the day
    # the downside is that it will delete the data for that protion of the day
    if os.path.isfile(tempFile):
        os.remove(tempFile)
    elif os.path.isfile('/home/pi/newfile.csv'):
        os.remove('/home/pi/newfile.csv')
    
    startLog()





    
