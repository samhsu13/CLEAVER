setwd("/Users/samhsu/Documents/THESIS/Code/KineseItUp/")

rm(list=ls())
library(tree)
library(randomForest)
library(stringi)
library(data.table)

memory.limit()
memory.limit(size = 4000)

###this is for ActiGraph files with 80Hz data- .csv files without timestamps. 
#directory for functions
directory <-"/Users/samhsu/Documents/THESIS/Code/KineseItUp/"
#directory for ActiGraph files
ag.directory<-"/Users/samhsu/Documents/THESIS/Data/final_wrist_raw_csv/"
#directory where processed files are written
out.directory<- "/Users/samhsu/Documents/THESIS/Data/Out/"
#name of on off log 
on.off<- "/Users/samhsu/Documents/THESIS/Data/final_dolog_20181002.csv"


load("/Users/samhsu/Documents/THESIS/Code/KineseItUp/mods.Rdata")
source("/Users/samhsu/Documents/THESIS/Code/KineseItUp/fuctions.for.models.R")

start.stop <-  read.csv(on.off)

start.stop$date2 <-paste(start.stop$start_month,"/",start.stop$start_day,"/",start.stop$start_year,sep="")
start.stop$on.times <-  paste(start.stop$date2, start.stop$Actual.Start)
start.stop$off.times <- paste(start.stop$date2, start.stop$Actual.Stop)

n.sub <- dim(start.stop)[1]

win.width <- 1 # width of "windows" to analyze in seconds

filelist <- list.files(ag.directory)


for(iii in 1:length(filelist)){
sub <-   substr(filelist[iii],4,7)
filename <- paste(ag.directory,filelist[iii],sep='')

sub.info <- subset(start.stop,start.stop$ID==sub)

sub
start <- start.stop$on.times[1]
start <- strptime(start,format= "%m/%d/%Y %H:%M:%S")

stop <- start.stop$off.times[2]
stop <- strptime(stop,format= "%m/%d/%Y %H:%M:%S")

sub.info$on.times<-	strptime(sub.info$on.times,format="%m/%d/%Y %H:%M:%S")
sub.info$off.times<- strptime(sub.info$off.times, format="%m/%d/%Y %H:%M:%S")

ag.data <- read.act(filename)
n <- dim(ag.data)[1]

mins <- ceiling(n/(80*win.width)) 
ag.data$min <- rep(1:mins,each=win.width*80)[1:n]
ag.data$vm <- sqrt(ag.data$V1^2+ag.data$V2^2+ag.data$V3^2)
ag.data$v.ang <- 90*(asin(ag.data$V1/ag.data$vm)/(pi/2))
ag.data.sum <- data.frame(mean.vm=tapply(ag.data$vm,ag.data$min,mean,na.rm=T),
                          sd.vm=tapply(ag.data$vm,ag.data$min,sd,na.rm=T),
                          mean.ang=tapply(ag.data$v.ang,ag.data$min,mean,na.rm=T),
                          sd.ang=tapply(ag.data$v.ang,ag.data$min,sd,na.rm=T),
                          p625=tapply(ag.data$vm,ag.data$min,pow.625),
                          dfreq=tapply(ag.data$vm,ag.data$min,dom.freq),
                          ratio.df=tapply(ag.data$vm,ag.data$min,frac.pow.dom.freq))

ag.data.sum$sed.rf <- predict(rf.sed.model,newdata=ag.data.sum)

ag.data.sum$start.time <- as.POSIXlt(tapply(ag.data$time,ag.data$min,min,na.rm=T),origin="1970-01-01 00:00.00 UTC")

write.csv(ag.data.sum,paste("AG", iii, "-01.csv", sep=""),sep=",")
}