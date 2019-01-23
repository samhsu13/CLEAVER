ground_dir <- "/Users/samhsu/Documents/THESIS/Data/"
behaviors_sheet <- read.csv(paste(ground_dir, 'coding_options_20180729_behaviors.csv', sep=''), stringsAsFactors = F)
behaviors <- tolower(gsub(" ", "", behaviors_sheet$Behavior))

sed_postures <- c("sb-lying", "sb-sitting", "la-kneeling/squatting", "la-stretching", "la-squatting", "la-bending")
light_postures <- c("la-stand", "la-standandmove", "la-standandmovewithupperbodymovement", "wa-walk", "wa-walkwithload",
                    "sp-kick", "sp-throw", "sp-jump", "sp-othersportmovement")
moderate_postures <- c("wa-running", "wa-ascendstairs", "wa-descendstairs", "sp-bike")
private_postures <- c("private/notcoded")

exercise <- 'EX- participating in sport, exercise or recreation'
work <- c('WRK- general', 'WRK- screen based')


getNextBehaviorRow <- function(i, state_start, behavior, time_rel, duration) {
  beh <- getNextCoding(i, state_start)
  
  if (strcmpi(beh, exercise) == TRUE) { # if the behavior is exercise, fill it with Modifier_2 actual sport
    sport <- getSportMod(i, state_start)
    next_behavior <- paste('EX-', sport)
    b <- tolower(gsub(" ", "", next_behavior))
  }
  else if (beh %in% work == TRUE) { # if behavior is work, fill it with Modifier_4
    work_mod <- getWorkMod(i, state_start)
    next_behavior <- paste(beh, " - ", work_mod, sep = "")
    b <- tolower(gsub(" ", "", next_behavior))
  }
  else {
    b <- tolower(gsub(" ", "", beh))
  }
  b_timeRel <- state_start[i, 'Time_Relative_sf']
  b_duration <- state_start[i, 'Duration_sf']

  #print(paste("current =", behavior, sep = " "))
  #print(paste("b =", b, sep = " "))
  
  print(paste("b =", b, "behavior =", behavior, sep = " "))
  
  while (((b %in% behaviors == FALSE) # if posture row
          | ((b == behavior) & (b_timeRel == time_rel) & (b_duration == duration))) # or if re-reading same behavior that was already read while moving through posture duration
          & (i < nrow(state_start))){ # and still within the criterion - skip and get behavior
                                                         
    i = i + 1
    b <- tolower(gsub(" ", "", state_start[i, 'Behavior']))
  }

  return(i)
}

getNextPostureRow <- function(i, state_start, behaviors) {
  p <- tolower(gsub(" ", "", state_start[i, 'Behavior']))

  while ((p %in% behaviors == TRUE) & (i < nrow(state_start))) { # if it's a behavior row, skip and get posture
    i = i + 1
    p <- tolower(gsub(" ", "", state_start[i, 'Behavior']))
  }
  
  return(i)
}

getNextCoding <- function(i, state_start) {
  coding <- state_start[i, 'Behavior']
  return(coding)
}

getUpperBodyMod <- function(i, state_start) {

  mod1 <- tolower(gsub(" ", "", state_start[i, 'Modifier_1']))
  sprintf("mod1 = %s", mod1)
  
  if (mod1 %in% c("yesmovement")) {
    upperbody <- "yes"
  }
  else if (mod1 %in% c("nomovement")) {
    upperbody <- "no"
  }
  else if (mod1 %in% c("typing")) {
    upperbody <- mod1
  }
  else {
    upperbody <- "unknown"
  }
  
  return(upperbody)
}
  
getSportMod <- function(i, state_start) {
  sport <- state_start[i, 'Modifier_2']
  return(sport)
}
  
getIntensityMod <- function(i, state_start, posture) {
  mod3 <- tolower(gsub(" ", "", state_start[i, 'Modifier_3']))
  
  p <- tolower(gsub(" ", "", posture))
  
  if (mod3 == "") {
    if (p %in% sed_postures) {
      intensity <- "sedentary"
    }
    else if (p %in% light_postures) {
      intensity <- "light"
    }
    else if (p %in% moderate_postures) {
      intensity <- "moderate"
    }
    else if (p %in% private_postures) {
      intensity <- "private/not coded"
    }
    else {
      intensity <- "None"
    }
  }
  else {
    intensity <- state_start[i, 'Modifier_3']
  }
  
  return(intensity)
}

getWorkMod <- function(i, state_start) {
  work_mod <- state_start[i, 'Modifier_4']
  return(substr(work_mod, 5, nchar(work_mod)))
}

determineBehaviorTransitionSplit <- function(behavior_second_fraction, behavior, next_behavior) {
  if (behavior_second_fraction < 0.8) {
    if (behavior_second_fraction >= 0.5) { # if this is the primary behavior
      primary_behavior <- behavior
      secondary_behavior <- next_behavior
    }
    else if (behavior_second_fraction > 0.2) { # if this is the secondary behavior
      primary_behavior <- next_behavior
      secondary_behavior <- behavior
    }
    else { # if next behavior is the majority behavior of this second
      primary_behavior <- next_behavior
    }
  }
  else {
    primary_behavior <- behavior
    secondary_behavior <- "None"
  }
  
  return(data.frame("primary_behavior" = primary_behavior, "secondary_behavior" = secondary_behavior))
}


determinePostureTransitionSplit <- function(second_fraction, posture, upperbody, intensity,
                                     next_posture, next_upperbody, next_intensity) {
  if (second_fraction < 0.8) {
    if (second_fraction >= 0.5) { # if this is the primary behavior
      primary_posture <- posture
      primary_upperbody <- upperbody
      primary_intensity <- intensity
      
      secondary_posture <- next_posture
      secondary_upperbody <- next_upperbody
      secondary_intensity <- next_intensity
    }
    else if (second_fraction > 0.2) { # if this is the secondary behavior
      primary_posture <- next_posture
      primary_upperbody <- next_upperbody
      primary_intensity <- next_intensity
      
      secondary_posture <- posture
      secondary_upperbody <- upperbody
      secondary_intensity <- intensity
    }
    else { # if next behavior is the majority behavior of this second
      primary_posture <- next_posture
      primary_upperbody <- next_upperbody
      primary_intensity <- next_intensity
    }
  }
  else {
    primary_posture <- posture
    primary_upperbody <- upperbody
    primary_intensity <- intensity
    secondary_posture <- "None"
    secondary_upperbody <- "None"
    secondary_intensity <- "None"
  }
  
  return(data.frame("primary_posture" = primary_posture, "primary_upperbody" = primary_upperbody,
                    "primary_intensity" = primary_intensity, "secondary_posture" = secondary_posture,
                    "secondary_upperbody" = secondary_upperbody, "secondary_intensity" = secondary_intensity,
                    stringsAsFactors = FALSE))
}


getTop2Postures <- function(fractions, state_start) {
  sorted_fractions <- fractions[with(fractions, order(-time)),]
  
  primary_fraction <- sorted_fractions[1,1]
  i <- sorted_fractions[1,2]
  primary_posture <- getNextCoding(i, state_start)
  primary_upperbody <- getUpperBodyMod(i, state_start)
  primary_intensity <- getIntensityMod(i, state_start, primary_posture)
  
  next_i <- sorted_fractions[2,2]
  next_posture <- getNextCoding(next_i, state_start)
  next_upperbody <- getUpperBodyMod(next_i, state_start)
  next_intensity <- getIntensityMod(next_i, state_start, next_posture)
  
  return(data.frame("top_fraction" = primary_fraction, "posture" = primary_posture,
                    "upperbody" = primary_upperbody, "intensity" = primary_intensity,
                    "next_posture" = next_posture, "next_upperbody" = next_upperbody,
                    "next_intensity" = next_intensity))
}
