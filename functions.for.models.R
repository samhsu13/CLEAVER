pow.625 <- function(vm)
{
	mods <- Mod(fft(vm))
	mods <- mods[-1]	
	n <- length(mods)
	n <- floor(n/2)
	freq <- 31.25*(1:n)/(2*n)
	mods <- mods[1:n]
	inds <- (1:n)[(freq>0.6)&(freq<2.5)]
	pow625 <- sum(mods[inds])/sum(mods)
	mods[is.na(mods)] <- 0
	if(is.na(sd(vm)) == FALSE) {
	  if (sd(vm)==0) {
		  pow625 <- 0
	  }
	}
	return(pow625)
}

dom.freq <- function(vm)
{
	if(length(vm)==1)
		return(NA)
	mods <- Mod(fft(vm))
	mods <- mods[-1]	
	n <- length(mods)
	n <- floor(n/2)
	freq <- 31.25*(1:n)/(2*n)
	mods <- mods[1:n]
	dom.ind <- which.max(mods)
	d.f <- as.vector(freq[which.max(mods)])
	return(d.f)
}

frac.pow.dom.freq <- function(vm)
{
	mods <- Mod(fft(vm))
	mods <- mods[-1]	
	n <- length(mods)
	n <- floor(n/2)
	freq <- 31.25*(1:n)/(2*n)
	mods <- mods[1:n]
	rat <- max(mods)/sum(mods)
	mods[is.na(mods)] <- 0
	if (is.na(sd(vm)) == FALSE) {
	  if (sd(vm)==0) {
		  rat <- 0
  	}
  }
	return(rat)

}

read.act <- function(file.name.and.path)
{
    # gets raw wrist file header data
  	head.data <- readLines(paste(file.name.and.path),n=10)
  	# get start time 
  	start.time <- head.data[3]
  	start.time <- (strsplit(start.time,split=" ")[[1]][3]) 
  	# get start date
  	start.date <- head.data[4]
  	start.date <- (strsplit(start.date,split=" ")[[1]][3])
  	# start time is now start.date + start.time
  	start.time <- as.POSIXlt(strptime(paste(start.date,start.time),"%m/%d/%Y %H:%M:%S"))
  	
  	
  	# read raw file - skip first 11 rows, comma-separated, column classes are all numeric
	data <- fread(file.name.and.path,skip=11,sep=",",header=F,colClasses=c("numeric","numeric","numeric"),showProgress=FALSE)

	n <- dim(data)[1] # number of rows in data
  	
	# final data = 'time': start.time + (0:num_rows-1)/80, data: data
  	full.data <- 
    	data.frame(time = start.time + (0:(n-1))/80,
            	  data)
  
  	return(full.data)

}

read.actBiostamp <- function(file.name.and.path)
{

  # read raw file
  data <- fread(file.name.and.path, skip=1, sep=",", header=F, data.table = FALSE, showProgress = FALSE) 
  # get times
  times <- strtoi(substr(data$V1, 1, 10))
  
  write.csv(data.frame((time = as.POSIXct(times, origin="1970-01-01"))), "times.csv")

  n <- dim(data)[1] # number of rows in data
  
  # final data = 'time': start.time + (0:num_rows-1)/80, data: data
  full.data <- data.frame(time = as.POSIXct(times, origin="1970-01-01"), data[,c('V2', 'V3', 'V4')])
  
  return(full.data)
  
}

read.act.2 <- function(file.name.and.path,start,stop)
{
  	head.data <- readLines(paste(file.name.and.path),n=10)
  	start.time <- head.data[3]
  	start.time <- (strsplit(start.time,split=" ")[[1]][3])
  	start.date <- head.data[4]
  	start.date <- (strsplit(start.date,split=" ")[[1]][3])
  	start.time <- as.POSIXlt(strptime(paste(start.date,start.time),"%m/%d/%Y %H:%M:%S"))
  	
  	diff.1 <- as.numeric(stop-start)
  	diff.2 <- as.numeric(stop-start.time)
	diff <- min(c(diff.2,diff.1))

	n.to.read <- diff*24*60*60*80
  	
	data <- fread(file.name.and.path,skip=11,sep=",",header=F,colClasses=c("numeric","numeric","numeric"),showProgress=FALSE,nrows=n.to.read)

	n <- dim(data)[1] # number of rows in data
  	
  	full.data <- 
    	data.frame(time = start.time + (0:(n-1))/80,
            	  data)
  
  	return(full.data)

}


read.actigraph.no.var.names <- function(file.name.and.path,start.time="12:00:00",start.date="8/18/2014") # start time & date are just placeholders
{
# This function that reads an actigraph file (located in "file.name.and.path") and
# creates a file with rows like these:
# subject                time counts                 min             ten.sec
#1     184 2010-01-26 15:50:00      4 2010-01-26 15:50:00 2010-01-26 15:50:00
#2     184 2010-01-26 15:50:01      0 2010-01-26 15:50:00 2010-01-26 15:50:00
#3     184 2010-01-26 15:50:02      0 2010-01-26 15:50:00 2010-01-26 15:50:00
# See above for the format of the actigraph file that the function expects.

  # add start time (these could be read from he header automatically)
  start.time <- as.POSIXlt(strptime(paste(start.date,start.time),"%m/%d/%Y %H:%M:%S"))

	# read acceleration data
	data <- read.csv(file.name.and.path,header=F,skip=10)
	
  	n <- dim(data)[1] # number of rows in data
  	full.data <- 
    	data.frame(time = start.time + (0:(n-1))/80,
            	  data)
  
  return(full.data)
}

read.actigraph.with.var.names <- function(file.name.and.path,start.time="12:00:00",start.date="8/18/2014")
{


	# read header and start time
  start.time <- as.POSIXlt(strptime(paste(start.date,start.time),"%m/%d/%Y %H:%M:%S"))

	# read acceleration data
	data <- read.csv(file.name.and.path,header=F,skip=11)
	
  	n <- dim(data)[1] # number of rows in data
  	full.data <- 
    	data.frame(time = start.time + (0:(n-1))/80,
            	  data)
  
  return(full.data)
}
