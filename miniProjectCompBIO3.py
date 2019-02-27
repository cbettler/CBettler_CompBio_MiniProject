import os
from Bio import SeqIO

currentDir = os.popen('pwd').read().rstrip()
#Gets path of current working directory to avoid hardcoding

path = (currentDir+ "/OptionA_Carlee_BettlerTEST4/")
#Sets path to inside of OptionA folder
#Note that optionA folder can be renamed if your name is not Carlee Bettler :)
#Note: Don't run python3 command (as explained in ReadME) from inside OptionA folder, will mess up/duplicate path name. Not sure how you would do this, as code runs in one go.... but don't

os.system('mkdir '+path)
#Makes OptionA_Carlee_Bettler folder

os.chdir(path)
#"Brings" user to inside of OptionA folder where rest of code will run

logFile = open(path + "OptionA.log", "w+")
#Creates logFile called OptionA.log

link1 = "ftp://ftp.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByRun/sra/SRR/SRR818/SRR8185310/SRR8185310.sra"
sraFile1 = "SRR8185310.sra"

def processSRA(link, sraFile):
    #This function retrieves .sra files and converts them to fastq files
    
    os.system("wget "+ link)
    #This retrieves single end Illumina reads from NCBI for the resequencing of K-12

    os.system("fastq-dump -I "+sraFile)
    #This converts .sra file retrieved in previous step to fastq file
    #You must have SRA-Toolkit installed

processSRA(link1, sraFile1)

def runSpades(path):
    #This function runs SPAdes to assemble the genome and writes command to log file. This must be installed.

    spadesPath ="spades -k 55,77,99,127 -t 15 --only-assembler -s " + path +"SRR8185310.fastq  -o"+path
    #Calls on previously made fastq file
    #The number of processors can be changed. I left it at 15 assuming the person running this has excess processing power. If you are tightly sharing resources, use -t 2.
    #This command format only works for single end, as opposed to paired-end, reads

    os.system(spadesPath)

    log = open(path + "OptionA.log", "a+")
    
    log.write(spadesPath+'\n\n')
    #Writes SPAdes path to logfile

runSpades(path)

def longContigs(path):
    #This function finds which contigs in the fasta file generated by SPAdes are >1000 nucleotides, and creates a new fasta file with these longer contigs, and writes results to log file
    longFastas = []
    #Holds longer contigs
    
    with open(path +"contigs.fasta") as handle:
        for record in SeqIO.parse(handle, "fasta"):
            if(len(record)>1000):
                longFastas.append(record)
    #Determines if length of records in the fasta file are > 1000, and if so adds them to a new list

    log = open(path + "OptionA.log", "a+")

    for i in range(1):
        log.write("There are " + str(len(longFastas)) + " contigs >1000 in the assembly."+'\n\n')
    #Writes to log how many contigs have a length >1000

    SeqIO.write(longFastas, path+"longFastas.fasta", "fasta")
    #This creates new fasta file from longFastas list

longContigs(path)

def basePairCount(path):
    #This function calculates the length of the assembly (the total number of basepairs in all the contigs with length >1000) and writes results to a log file
    seqs = []

    numBP = 0

    with open(path+"longFastas.fasta") as handle:
        for record in SeqIO.parse(handle, "fasta"):
            seqs.append(record.seq)
    #Adds sequences read in from fasta file to a list

    for i in range(len(seqs)):
        numBP = len(seqs[i])+numBP
    #Stores/accumulates number of basepairs in each sequence in seqs list to numBP

    log = open(path + "OptionA.log", "a+")

    for i in range(1):
        log.write("There are "+ str(numBP)+ " bp in the assembly"+'\n\n')
    #writes total number of basepairs to log file

basePairCount(path)

def Prokka(path):
    #This function uses Prokka, which must be installed, to annotate this assembly and writes path to log file.
    
    os.system("prokka --force --outdir "+path+"ProkkaOutput --genus Escherichia --locustag ECOL  longFastas.fasta")
    #--force forces it to replace old files with new files with the current date
    #Uses the Escherichia genus database
    
    log = open(path + "OptionA.log", "a+")
    
    for i in range(1):
        log.write("prokka --outdir "+path+"ProkkaOutput --genus Escherichia --locustag ECOL  longFastas.fasta"+'\n\n')
    #Writes Prokka command to log file

Prokka(path)

def ProkkaDif(path):
    #This function writes Prokka ouput file ending in .txt to a log file and writes difference in CDS and tRNA between the results in the file and the assembled genome in RefSeq for E. coli K-12 (NC_000913). Prokka must be installed
    
    import datetime
    now = str(datetime.datetime.now())
    date = now[5:7]+now[8:10]+now[0:4]
    #Gets current date/time and parses it for file name (Prokka includes this when automatically naming output files)

    txtFile = []
    infile = path+"ProkkaOutput/PROKKA_"+str(date)+".txt"
    #Creates new directory called ProkkaOutput where results will be found

    txtFile = open(infile).read().split("\n")
    
    log = open(path + "OptionA.log", "a+")
    
    for i in range(1):
        for j in range(len(txtFile)):
            log.write(txtFile[j]+'\n')
        log.write('\n')
        #Writes Prokka ouput file ending in .txt to a log file
    

    originalCDS = 4140
    originaltRNA = 89
    #Original RefSeq values for CDS and tRNA

    newtRNA = ''
    newCDS = ''

    for i in range(len(txtFile)):
        if txtFile[i].find("tRNA")>= 0:
            newtRNA = int(txtFile[i][5:])
        elif txtFile[i].find("CDS")>= 0:
            newCDS = int(txtFile[i][4:])

    #Reads in from.txt file values for tRNA and CDS

    dif_CDS = originalCDS - newCDS
    dif_tRNA = originaltRNA - newtRNA
    #Finds differences between original and new values of tRNA and CDS

    insert1 = " additional "
    insert2 = " additional "

    if dif_CDS >=0:
        insert1 = " less "
    else:
        dif_CDS = abs(dif_CDS)

    if dif_tRNA >= 0:
        insert2 = " less "
    else:
        dif_tRNA = abs(dif_tRNA)

    #Uses conditional structure to determine whether original values are greater or less than read in values, which determines whether the word additional or less inserted into the printed string. If no difference is found, it will simply output there is 0 less.

    log = open(path + "OptionA.log", "a+")

    for i in range(1):
        log.write("Prokka found "+ str(dif_CDS)+ insert1+ "CDS and "+ str(dif_tRNA)+ insert2+ "tRNA than the RefSeq."+'\n\n')
        #Writes Prokka command to log file

ProkkaDif(path)

link2= "ftp://ftp.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByRun/sra/SRR/SRR141/SRR1411276/SRR1411276.sra"
sraFile2 = "SRR1411276.sra"
processSRA(link2, sraFile2)
#Calls this function to retrieve a link to the file holding the E. coli transcriptome of a K-12 derivative from NCBI and converts it from an sra to a fastq file

link3 = "ftp://ftp.ncbi.nlm.nih.gov/genomes/archive/old_refseq/Bacteria/Escherichia_coli_K_12_substr__MG1655_uid57779/NC_000913.fna"
#This file is need for the next bowtie command. It is for annotated E. coli genome NC_000913

def bowTiePrep(link):
    #Runs bowTie2 (which must be installed) to generate an index to map to
    os.system("wget "+link)
    os.system("bowtie2-build NC_000913.fna EcoliK12")
    #Generates an index called Ecoli K12 to map to from file that was read in with wget

bowTiePrep(link3)

os.system("tophat2 --no-novel-juncs -p 20 -o /home/cbettler/OptionA_Carlee_Bettler/ProkkaOutput EcoliK12 SRR1411276.fastq")
#Note:This command is VERY SLOW!!! If it gets frozen or a pip breaks, hit cntrl+ C. It may say a pipe is broken, but is it has not stopped/lost connection, keep letting it run
#Must have tophat installed
#Tophat aligns annotated genome to a reference genome

os.system("cufflinks -p 20 accepted_hits.bam")
#If the tophat command above was not ran to completion, this will get frozen at 0%
#Must have cufflinks installed
#Cufflinks 'assembles' mapped reads into transcripts
#Note: I realize I do not have the final log file command done, but this is because I could never get my cufflinks command to finish running





