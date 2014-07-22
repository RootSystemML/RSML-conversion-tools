

all.path <- "/Users/guillaumelobet/Dropbox/research/projects/research/rsml/scripts/rsml_tests/"

rs <- rsmlToDataTable(all.path)
rs <- rsmlToList(all.path)
hist.rsml(rs)
hist.matrix.rsml(rs)

## ------------------------------------------------------------------------------------
## ------------------------------------------------------------------------------------


# Batch load of RSML files
rsmlToDataTable <- function(all.path){
  
  all.rsml <- list.files(all.path)
  
  if(length(all.rsml) > 0) rs <- oneRSMLToDataTable(paste(all.path, all.rsml[1], sep=""))
  
  for(i in 2:length(all.rsml)){
    rs <- rbind(rs, oneRSMLToDataTable(paste(all.path, all.rsml[i], sep="")))
  }
  
  return(rs)
}

# Batch load of RSML files
rsmlToList <- function(all.path){
  
  all.rsml <- list.files(all.path)
  
  if(length(all.rsml) > 0) rs <- oneRSMLToDataTable(paste(all.path, all.rsml[1], sep=""))
  
  for(i in 2:length(all.rsml)){
    rs <- rbind(rs, oneRSMLToDataTable(paste(all.path, all.rsml[i], sep="")))
  }
  
  return(as.list(rs))
}

# RSML to list
oneRSMLToList <- function(rsml.path){
  # Return the extended dataframe 
  return(as.list(rsmlToDataTable(rsml.path)))
}

# RSML to data table
oneRSMLToDataTable <- function(rsml.path){
  
  library("XML")
  
  rsml <- xmlToList(xmlParse(rsml.path))
  plants <- rsml$scene
  
  #️Get the properties used in this specific rsml file
  properties.list <- rsml$metadata$"property-definitions"
  properties.names <- vector(length = length(properties.list))
  for(i in 1:length(properties.list)){properties.names[i] <- properties.list[i]$"property-definition"$label}

  # Create the empty data frame
  rsml.data <- data.frame(file_id = rsml.path,
                        plant_id = "-1",
                        root_id = "-1",
                        parent_id = "-1",
                        root_order = -1)
  for(p in properties.names) rsml.data[[p]] <- -1
  rsml.data$root_id <- as.character(rsml.data$root_id)
  rsml.data$plant_id <- as.character(rsml.data$plant_id)
  rsml.data$parent_id <- as.character(rsml.data$parent_id)
  
  # Create the same data frame for temp storage
  template <- rsml.data[1,]
  
  # Remove the data from the dataframe to have a clean start
  rsml.data <- rsml.data[!1,]
  
  # Get the data from the rsml structure
  k <- 1
  for(r0 in plants){
    for(r1 in r0){
      if("properties" %in% names(r1)){
        # Send data
        temp <- template
        temp[["plant_id"]][1] <- k
        if(!is.null(r0$.attr[1])) temp[["plant_id"]][1] <- r0$.attr[1]
        temp[["root_id"]][1] <- r1$.attr[1]
        temp[["root_order"]][1] <- 0
        for(p in properties.names){
          if(!is.null(r1$properties[[p]])){ temp[[p]][1] <- r1$properties[[p]]}
        }
        rsml.data <- rbind(rsml.data, temp)
        
        if("root" %in% names(r1)){
          for(r2 in r1){  
            if("properties" %in% names(r2)){
              
              temp <- template
              temp[["plant_id"]][1] <- k
              if(!is.null(r0$.attr[1])) temp[["plant_id"]][1] <- r0$.attr[1]
              temp[["root_id"]][1] <- r2$.attr[1]
              temp[["parent_id"]][1] <- r1$.attr[1]
              temp[["root_order"]][1] <- 1
              for(p in properties.names){
                if(!is.null(r2$properties[[p]])){ temp[[p]][1] <- r2$properties[[p]]}
              }
              rsml.data <- rbind(rsml.data, temp)
              
              if("root" %in% names(r2)){
                for(r3 in r2){
                  if("properties" %in% names(r3)){
                    
                    temp <- template
                    temp[["plant_id"]][1] <- k
                    if(!is.null(r0$.attr[1])) temp[["plant_id"]][1] <- r0$.attr[1]
                    temp[["root_id"]][1] <- r3$.attr[1]
                    temp[["parent_id"]][1] <- r2$.attr[1]
                    temp[["root_order"]][1] <- 2
                    for(p in properties.names){
                      if(!is.null(r3$properties[[p]])){ temp[[p]][1] <- r3$properties[[p]] }
                    }
                    rsml.data <- rbind(rsml.data, temp)
                    
                  }
                }
              }
            }
          }
        }
      }
    }
    k <- k+1
  }
  for(p in properties.names) rsml.data[[p]] <- as.numeric(rsml.data[[p]])
  
  #remove(r0); remove(r1); remove(r2); remove(r3); remove(temp); remove(i); remove(k); remove(p)
  
  # Return the extended dataframe 
  return(rsml.data)
}

# Histgram with all the variables
hist.rsml<- function(rs){  
  
  if(is.list(rs)) rs <- data.frame(rs)
  properties <- colnames(rs)[6:length(colnames(rs))]

  l <- 0
  for(n in properties){
    if(nrow(rs[rs[[n]] > 0,]) > 5) l <- l + 1
    else rs[[n]] <- NULL
  }
  properties <- colnames(rs)[6:length(colnames(rs))]
  
  
  # Find best display fo the graphs
  for(i in 1:10) if((l/i) >= i) row <- i
  col <- ceiling(l/row)
  
  par(mfrow=c(row,col))
  for(n in properties){
    rs[[n]] <- as.numeric(rs[[n]])
    temp <- rs[rs[[n]] > -1,]
    if(nrow(temp) > 3){
      hist(temp[[n]], main=n, xlab=n, breaks=20)
    }
  }
}

# Histgram and regression with all the variables
hist.matrix.rsml<- function(rs){
  
  library(car)
  
  if(is.list(rs)) rs <- data.frame(rs)
  properties <- colnames(rs)[6:length(colnames(rs))]
  
  l <- 0
  for(n in properties){
    if(nrow(rs[rs[[n]] > 0,]) > 5) l <- l + 1
    else rs[[n]] <- NULL
  }
  properties <- colnames(rs)[6:length(colnames(rs))]
  
  scatterplotMatrix(rs[6:ncol(rs)])
}



