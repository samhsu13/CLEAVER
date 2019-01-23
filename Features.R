### Sets the working directory for the R console to use
setwd("/Users/samhsu/Documents/THESIS/Data/BioStamp/")

### Removes anything already in the console and loads in needed libraries
rm(list=ls())
library(tree)
library(randomForest)
library(stringi)
library(data.table)

#memory.limit()
#memory.limit(size = 200000)

###this is for ActiGraph files with 80Hz data- .csv files without timestamps. 
#directory for functions
directory <-"/Users/samhsu/Documents/THESIS/Data/BioStamp/"
#directory for ActiGraph files
ag.directory <- "/Users/samhsu/Documents/THESIS/Data/BioStamp/"
#directory where processed files are written
out.directory <- "/Users/samhsu/Documents/THESIS/Data/BioStampOut/"
#name of on off log 
on.off <- "/Users/samhsu/Documents/THESIS/Data/final_dolog_20181002.csv"

load("/Users/samhsu/Documents/THESIS/Code/mods.Rdata")
source("/Users/samhsu/Documents/THESIS/Code/functions.for.models.R")

### Reads and formats the data 
start.stop <-  read.csv(on.off)

start.stop$date2 <-paste(start.stop$start_month,"/",start.stop$start_day,"/",start.stop$start_year,sep="")
start.stop$on.times <-  paste(start.stop$date2, start.stop$Actual.Start)
start.stop$off.times <- paste(start.stop$date2, start.stop$Actual.Stop)

n.sub <- dim(start.stop)[1]

### number of seconds to put into each window
win.width <- 1 

for (p in 1:nrow(start.stop)) {
  p <- nrow(start.stop)  
  person <- start.stop$ID[p]
  person_path <- paste(ag.directory, person, sep="")
  ob <- start.stop$session[p]
  
  ob_path <- paste(person_path, "/", substr(ob, 1, 3), sep="")
  thigh_file <- paste(ob_path, "/anterior_thigh_left/accel.csv", sep="")
  chest_file <- paste(ob_path, "/medial_chest/accel.csv", sep="")
  

  ### Finds and adds time of the observation to the data frame - gets the start time of DO1 and the end time of DO2
  start <- start.stop$on.times[p]
  start <- strptime(start,format= "%m/%d/%Y %H:%M:%S")
  
  stop <- start.stop$off.times[p]
  stop <- strptime(stop,format= "%m/%d/%Y %H:%M:%S")
  
  ### reads the data file completely and adds the time to it 
  thigh.data <- read.actBiostamp(thigh_file)
  thigh_n <- dim(thigh.data)[1]
  chest.data <- read.actBiostamp(chest_file)
  chest_n <- dim(chest.data)[1]
  
  thigh_actual_start <- -1
  chest_actual_start <- -1
  thigh_mins <- c() # vectors to label thigh seconds
  chest_mins <- c() # vectors to label chest seconds
  
  # label minutes
  for (j in 1:thigh_n) { # loop through the number of samples from the thigh accel data
    
    # time_diff is time difference in seconds; 31.25 samples per second so time_diff should be the
    # same for ~ 31 rows
    time_diff <- as.integer(as.numeric(difftime(thigh.data$time[j], start, units = "secs")))
    
    if ((time_diff >= 0) & (thigh.data$time[j] <= stop)) { # if time is within start/stop window
      
      if (thigh_actual_start == -1) { # if it's the first row that's within the window
        thigh_actual_start <- j # save row number
      }
      thigh_mins <- c(thigh_mins, as.integer(time_diff+1))
      
    }
  }
  
  for (j in 1:chest_n) { # loop through the number of samples from the chest accel data
    time_diff <- as.integer(as.numeric(difftime(chest.data$time[j], start, units = "secs")))
    if ((time_diff >= 0) & (chest.data$time[j] <= stop)) {
      if (chest_actual_start == -1) {
        chest_actual_start <- j
      }
      chest_mins <- c(chest_mins, as.integer(time_diff+1))
    }
  }
  
  thigh_data_slice <- length(thigh_mins)
  thigh.data <- thigh.data[thigh_actual_start:(thigh_actual_start+thigh_data_slice-1),]
  chest_data_slice <- length(chest_mins)
  chest.data <- chest.data[chest_actual_start:(chest_actual_start+chest_data_slice-1),]
  
  thigh.data$min <- thigh_mins
  thigh.data$vm <- sqrt(thigh.data$V2^2+thigh.data$V3^2+thigh.data$V4^2) # vector magnitude aka sum squares
  thigh.data$v.ang <- 90*(asin(thigh.data$V2/thigh.data$vm)/(pi/2))
  thigh.data$xy <- thigh.data$V2 * thigh.data$V3
  thigh.data$yz <- thigh.data$V3 * thigh.data$V4
  thigh.data$xz <- thigh.data$V2 * thigh.data$V4
  thigh.data$xyz <- thigh.data$V2 * thigh.data$V3 * thigh.data$V4
  
  chest.data$min <- chest_mins
  chest.data$vm <- sqrt(chest.data$V2^2+chest.data$V3^2+chest.data$V4^2) # vector magnitude aka sum squares
  chest.data$v.ang <- 90*(asin(chest.data$V2/chest.data$vm)/(pi/2))
  chest.data$xy <- chest.data$V2 * chest.data$V3
  chest.data$yz <- chest.data$V3 * chest.data$V4
  chest.data$xz <- chest.data$V2 * chest.data$V4
  chest.data$xyz <- chest.data$V2 * chest.data$V3 * chest.data$V4
  
  thigh.data.sum <- data.frame(thigh.mean.vm = tapply(thigh.data$vm, thigh.data$min, mean, na.rm=TRUE),
                        thigh.sd.vm = tapply(thigh.data$vm, thigh.data$min, sd, na.rm=T),
                        thigh.mean.ang = tapply(thigh.data$v.ang, thigh.data$min, mean, na.rm=T),
                        thigh.sd.ang = tapply(thigh.data$v.ang, thigh.data$min, sd, na.rm=T),
                        thigh.p625 = tapply(thigh.data$vm, thigh.data$min, pow.625),
                        thigh.dfreq = tapply(thigh.data$vm, thigh.data$min, dom.freq),
                        thigh.ratio.df = tapply(thigh.data$vm, thigh.data$min, frac.pow.dom.freq),
                        thigh.min.x = tapply(thigh.data$V2, thigh.data$min, min),
                        thigh.min.y = tapply(thigh.data$V3, thigh.data$min, min),
                        thigh.min.z = tapply(thigh.data$V4, thigh.data$min, min),
                        thigh.max.x = tapply(thigh.data$V2, thigh.data$min, max),
                        thigh.max.y = tapply(thigh.data$V3, thigh.data$min, max),
                        thigh.max.z = tapply(thigh.data$V4, thigh.data$min, max),
                        thigh.mean.x = tapply(thigh.data$V2, thigh.data$min, mean, na.rm=T),
                        thigh.mean.y = tapply(thigh.data$V3, thigh.data$min, mean, na.rm=T),
                        thigh.mean.z = tapply(thigh.data$V4, thigh.data$min, mean, na.rm=T),
                        thigh.sd.x = tapply(thigh.data$V2, thigh.data$min, sd, na.rm=T),
                        thigh.sd.y = tapply(thigh.data$V3, thigh.data$min, sd, na.rm=T),
                        thigh.sd.z = tapply(thigh.data$V4, thigh.data$min, sd, na.rm=T),
                        thigh.mean.xy = tapply(thigh.data$xy, thigh.data$min, mean, na.rm=T),
                        thigh.mean.yz = tapply(thigh.data$yz, thigh.data$min, mean, na.rm=T),
                        thigh.mean.xz = tapply(thigh.data$xz, thigh.data$min, mean, na.rm=T),
                        thigh.mean.xyz = tapply(thigh.data$xyz, thigh.data$min, mean, na.rm=T))
  
  chest.data.sum <- data.frame(chest.mean.vm = tapply(chest.data$vm, chest.data$min, mean, na.rm=T),
                               chest.sd.vm = tapply(chest.data$vm, chest.data$min, sd, na.rm=T),
                               chest.mean.ang = tapply(chest.data$v.ang, chest.data$min, mean, na.rm=T),
                               chest.sd.ang = tapply(chest.data$v.ang, chest.data$min, sd, na.rm=T),
                               chest.p625 = tapply(chest.data$vm, chest.data$min, pow.625),
                               chest.dfreq = tapply(chest.data$vm, chest.data$min, dom.freq),
                               chest.ratio.df = tapply(chest.data$vm, chest.data$min, frac.pow.dom.freq),
                               chest.min.x = tapply(chest.data$V2, chest.data$min, min),
                               chest.min.y = tapply(chest.data$V3, chest.data$min, min),
                               chest.min.z = tapply(chest.data$V4, chest.data$min, min),
                               chest.max.x = tapply(chest.data$V2, chest.data$min, max),
                               chest.max.y = tapply(chest.data$V3, chest.data$min, max),
                               chest.max.z = tapply(chest.data$V4, chest.data$min, max),
                               chest.mean.x = tapply(chest.data$V2, chest.data$min, mean, na.rm=T),
                               chest.mean.y = tapply(chest.data$V3, chest.data$min, mean, na.rm=T),
                               chest.mean.z = tapply(chest.data$V4, chest.data$min, mean, na.rm=T),
                               chest.sd.x = tapply(chest.data$V2, chest.data$min, sd, na.rm=T),
                               chest.sd.y = tapply(chest.data$V3, chest.data$min, sd, na.rm=T),
                               chest.sd.z = tapply(chest.data$V4, chest.data$min, sd, na.rm=T),
                               chest.mean.xy = tapply(chest.data$xy, chest.data$min, mean, na.rm=T),
                               chest.mean.yz = tapply(chest.data$yz, chest.data$min, mean, na.rm=T),
                               chest.mean.xz = tapply(chest.data$xz, chest.data$min, mean, na.rm=T),
                               chest.mean.xyz = tapply(chest.data$xyz, chest.data$min, mean, na.rm=T))
  
  ### Adjusts the time stamp for each window
  thigh.data.sum$start.time <- as.POSIXlt(tapply(thigh.data$time, thigh.data$min, min, na.rm=T),origin="1970-01-01 00:00.00 UTC")
  ### Outputs the file to the directory with the specified name
  thigh.ag.file <- paste(person, "-", ob, "thigh.csv", sep="")
  write.csv(thigh.data.sum, paste(out.directory, thigh.ag.file, sep=""), sep=",")
  print(thigh.ag.file)
  
  chest.data.sum$start.time <- as.POSIXlt(tapply(chest.data$time, chest.data$min, min, na.rm=T),origin="1970-01-01 00:00.00 UTC")
  ### Outputs the file to the directory with the specified name
  chest.ag.file <- paste(person, "-", ob, "chest.csv", sep="")
  write.csv(chest.data.sum, paste(out.directory, chest.ag.file, sep=""), sep=",")
  print(chest.ag.file)
}
