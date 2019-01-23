library(pracma)
source("/Users/samhsu/Documents/THESIS/Code/getPostureData.R")

once <- 1
# Set this to location of criterion file
ground_dir <- "/Users/samhsu/Documents/THESIS/Data/"

# Set this to where you want second-by-second files to be output
outdir <- "/Users/samhsu/Documents/THESIS/Out/"

# read in behaviors and postures
behaviors_sheet <- read.csv(paste(ground_dir, 'coding_options_20180729_behaviors.csv', sep=''), stringsAsFactors = F)

behaviors <- tolower(gsub(" ", "", behaviors_sheet$Behavior))

exercise <- 'EX- participating in sport, exercise or recreation'
work <- c('WRK- general', 'WRK- screen based')
behavior <- ''
behavior_timeRel <- 0
behavior_duration <- 0

posture <- ''

# Read in criterion
ground_truth <- read.csv(paste(ground_dir, 'best_obs_onesheet_Sam.csv', sep=''), stringsAsFactors = F)

# Read in DO_log
DO_log <- read.csv(paste(ground_dir, 'final_dolog_20181002.csv', sep=''), stringsAsFactors = F)
DO_log_copyB <- c("AM02DO2", "AM08DO1", "AM11DO1", "AM11DO2", "AM12DO2", "AM15DO2", "AM26DO2")

# these observations are excluded because of missing codings
exclude_obs <- c("AM10DO1_R_FINAL_C", "AM02DO2_J_copyB_FINAL_R", "AM11DO1_N_copyB_FINAL_C", "AM15DO2_M_copyB_FINAL_C", "AM15DO2_N_copyB_FINAL")

# For each observation session, make a separate second-by-second file
observations <- unique(ground_truth$Observation) # observations = list of observation sessions "A_AM02DO2_J", "A_AM04DO2_J",...
transition <- 0

# Make second-by-second files
for(obs in observations) {
  if (!(obs %in% exclude_obs)) {
  #if (obs == "AM27DO1_R_FINAL_C") {
  last_time <- -1 # to make sure no second is repeated
  first <- 0 # for incrementing actual time
  next_i <- 0
  b_next_i <- 0
  
  # get actual start time data
  DO_log_ob <- substr(obs, 1, 4) # "AM01"
  DO_log_sess <- substr(obs, 5, 7) # "DO1"
  session <- paste(DO_log_ob, DO_log_sess, sep="") # "AMO1DO1"
  DO_log_obs <- DO_log[DO_log$ID == DO_log_ob,] # get all of the DO log rows for this obs session
  
  if (session %in% DO_log_copyB) { # if there's a copy A and B, append "_a" or "_b" for
    DO_log_sess <- paste(DO_log_sess, "_", tolower(substr(obs, 15, 15)), sep="")
  }
  DO_log_session <- DO_log_obs[DO_log_obs$session == DO_log_sess,] # get the appropriate session for this obs   
  actual_time <- DO_log_session$Actual.Start
  
  ground_truth_obs <- ground_truth[ground_truth$Observation == obs,] # get the ground truth aka just THIS obs session
  # get the state start rows and only positive Time_Relative_sf rows (for negative copy B stuff)
  state.start <- ground_truth_obs[(ground_truth_obs$Time_Relative_sf >= 0.0) & (ground_truth_obs$Event_Type == 'State start'),]
  ground_truth_classes <- data.frame()
  
  for(i in 1:nrow(state.start)) { # for each state start row
    print(paste("i =", i, "next_i =", next_i, sep=" "))
    observation <- state.start[i, 'Observation']
    date <- paste(DO_log_session$start_month, DO_log_session$start_day, DO_log_session$start_year, sep="/")
    #date <- state.start[i, 'Date_dmy']
    duration <- state.start[i, 'Duration_sf']
    end <- 0
    behavior_end <- 0
    
    b <- tolower(gsub(" ", "", state.start[i, 'Behavior']))
    
    if (b %in% behaviors == TRUE) { # if it's a behavior row, save behavior
      if (i >= b_next_i) {
        behavior <- state.start[i, 'Behavior']
        behavior_timeRel <- state.start[i, 'Time_Relative_sf']
        behavior_duration <- duration
        
        if (strcmpi(behavior, exercise) == TRUE) { # if the behavior is exercise, fill it with Modifier_2 actual sport
          sport <- getSportMod(i, state.start)
          behavior <- paste('EX-', sport)
        }
        if (behavior %in% work == TRUE) {
          work_mod <- getWorkMod(i, state.start)
          behavior <- paste(behavior, " - ", work_mod, sep = "")
          print(paste("i =", i, "behavior =", behavior, sep = " "))
        }
      }
    }
    else { # posture, grab everything to fill sec-by-sec row 
      if (i >= next_i) {
        posture <- state.start[i, 'Behavior']
        upperbody <- getUpperBodyMod(i, state.start)
        intensity <- getIntensityMod(i, state.start, posture)
        
        for(j in 0:(duration)) { # for every second for this state start's duration
          transition <- 0
          num_postures <- 1
          
          if (end == 0) {
            time_rel <- state.start[i, 'Time_Relative_sf']
            time <- ceiling(time_rel) + j #time index within a person's state start row's duration
            
            if (time > last_time) {
              if (first == 0) {
                actual_time <- substr(strptime(actual_time, format = "%H:%M:%S") + 0, 12, 20)
                first <- 1
              }
              else {
                actual_time <- substr(strptime(actual_time, format = "%H:%M:%S") + 1, 12, 20)
              }
              
              # init primary and secondary behaviors and postures
              primary_behavior <- behavior
              secondary_behavior <- "None"
              primary_posture <- posture
              primary_upperbody <- upperbody
              primary_intensity <- intensity
              secondary_posture <- "None"
              secondary_upperbody <- "None"
              secondary_intensity <- "None"
              
              if (time + 1 >= time_rel + duration) { # if time is the last full second of this duration
                if (time + 1 > time_rel + duration) {
                  num_postures <- 2
                }
                transition <- 1

                second_fraction <- time_rel + duration - floor(time_rel + duration)
                next_duration <- 0
                
                if (i >= nrow(state.start)) { # if we reached the end of the observation
                  next_posture <- "None"
                  next_upperbody <- "None"
                  next_intensity <- "None"
                }
                else { #if (i < nrow(state.start))
                  # get data for next posture sharing this second
                  next_i <- getNextPostureRow(i+1, state.start, behaviors)
                  
                  if (next_i <= nrow(state.start)) { # if we haven't reached the end of the observation session
                    next_posture <- getNextCoding(next_i, state.start)
                    next_upperbody <- getUpperBodyMod(next_i, state.start)
                    next_intensity <- getIntensityMod(next_i, state.start, next_posture)
                    next_duration <- state.start[next_i, 'Duration_sf']
                  }
                }
                
                if (second_fraction + next_duration >= 1) { # if the next posture goes past this current second
                  transition_split <- determinePostureTransitionSplit(second_fraction, posture, upperbody, intensity,
                                                                      next_posture, next_upperbody, next_intensity)
                  
                  primary_posture <- transition_split$primary_posture
                  primary_upperbody <- transition_split$primary_upperbody
                  primary_intensity <- transition_split$primary_intensity
                  secondary_posture <- transition_split$secondary_posture
                  secondary_upperbody <- transition_split$secondary_upperbody
                  secondary_intensity <- transition_split$secondary_intensity
                }
                else { # if second_fraction + next_duration < 1 aka this second belongs to more than two postures
                  fractions <- data.frame("time" = second_fraction, "i" = i, stringsAsFactors = FALSE)
                  
                  while ((sum(fractions$time) + next_duration < 1) & (next_duration != -1)) { # while this second has not been completely claimed
                    fractions <- rbind(fractions, list(next_duration, next_i)) # compile df of (the fractions of this second each posture holds, state start row index) 
                    next_i <- getNextPostureRow(next_i+1, state.start, behaviors)
                    
                    if (next_i <= nrow(state.start)) { # if we haven't reached the end of the observation
                      next_duration <- state.start[next_i, 'Duration_sf']
                    }
                    else { # we went out of bounds of the observation
                      next_duration <- -1
                    }
                  }
                  
                  if (next_duration != -1) { # if we didn't go out of bounds and end the observation, calculate the last fraction and add to df
                    last_fraction <- 1 - sum(fractions$time)
                    fractions <- rbind(fractions, list(last_fraction, next_i))
                  }
                  num_postures <- nrow(fractions)
                  top2 <- getTop2Postures(fractions, state.start)
                  transition_split <- determinePostureTransitionSplit(top2$top_fraction, top2$posture, top2$upperbody,
                                           top2$intensity, top2$next_posture, top2$next_upperbody,
                                           top2$next_intensity)
                  primary_posture <- transition_split$primary_posture
                  primary_upperbody <- transition_split$primary_upperbody
                  primary_intensity <- transition_split$primary_intensity
                  secondary_posture <- transition_split$secondary_posture
                  secondary_upperbody <- transition_split$secondary_upperbody
                  secondary_intensity <- transition_split$secondary_intensity
                }
                posture <- next_posture
                upperbody <- next_upperbody
                intensity <- next_intensity
                end <- 1
              }
              
              if ((time + 1 >= behavior_timeRel + behavior_duration) & (behavior_end == 0)) { # if last full second of current behavior's dur
                behavior_second_fraction <- behavior_timeRel + behavior_duration - floor(behavior_timeRel + behavior_duration)
  
                # if not last state start row of this observation
                if (i >= nrow(state.start) | b_next_i >= nrow(state.start)) {
                  next_behavior <- "None"
                }
                else { # if (i < nrow(state.start))  
                  # get data for next behavior sharing this second
                  new_i <- max(i, b_next_i)
                  b_next_i <- getNextBehaviorRow(new_i+1, state.start, tolower(gsub(" ", "", behavior)), behavior_timeRel, behavior_duration)
                  print(b_next_i)
                  if (b_next_i <= nrow(state.start)) {
                    next_behavior <- getNextCoding(b_next_i, state.start)
  
                    if (strcmpi(next_behavior, exercise) == TRUE) { # if the behavior is exercise, fill it with Modifier_2 actual sport
                      sport <- getSportMod(b_next_i, state.start)
                      next_behavior <- paste('EX-', sport)
                    }
                    if (next_behavior %in% work == TRUE) {
                      work_mod <- getWorkMod(b_next_i, state.start)
                      next_behavior <- paste(next_behavior, " - ", work_mod, sep = "")
                    }
                  }
                  else {
                    next_behavior <- "None"
                  }
                  
                  print(paste("i = ", i, "time = ", time, "next behavior = ", next_behavior, sep = " "))
                }
                
                # if current behavior is majority of the second, then do nothing b/c initial primary, 2ndary behaviors remain
                behavior_transition_split <- determineBehaviorTransitionSplit(behavior_second_fraction, behavior, next_behavior)
                primary_behavior <- behavior_transition_split$primary_behavior
                secondary_behavior <- behavior_transition_split$secondary_behavior
                
                behavior <- next_behavior
                behavior_duration <- state.start[b_next_i, "Duration_sf"]
                behavior_timeRel <- state.start[b_next_i, "Time_Relative_sf"]
              }
              
              if (primary_intensity == 'sedentary') {
                coding = 'sedentary'
              }
              else {
                coding = 'non-sedentary'
              }
              
              sec_obs <- data.frame(observation, date, coding,
                                    primary_behavior, primary_posture, primary_upperbody, primary_intensity,
                                    secondary_behavior, secondary_posture, secondary_upperbody, secondary_intensity,
                                    num_postures, transition, actual_time, time)
  
              ground_truth_classes <- rbind(ground_truth_classes, cbind(sec_obs))
              
              last_time <- time
            }
          }
        }
      }
    }
  }
  csvname <- paste(obs, '_second_codings.csv', sep="")
  print(csvname)
  write.csv(ground_truth_classes, paste(outdir, csvname, sep=""))
  #}
  }
}

