
#' Import a bunch of RSML file into a List
#' @param rsml.path    The path to the directory containing all the rsml files. Mandatory.
#' @param store.raw    Do you want to store the raw RSML data into the rsml object? Take much more space. Defaults to FALSE
#' @keywords rsml
#' @export 
#' @examples
#' rsmlToList()
rsmlToList <- function(all.path, store.raw = F){
  
  all.rsml <- list.files(all.path)
  
  if(length(all.rsml) > 0) rs <- oneRsmlToList(paste(all.path, all.rsml[1], sep=""), store.raw = store.raw)
  
  
  for(i in 2:length(all.rsml)){
    temp <- oneRsmlToList(paste(all.path, all.rsml[i], sep=""), store.raw = store.raw)
    rs$processed <- rbind(rs$processed, temp$processed)
    rs$files.list <- c(rs$files.list, temp$files.list)
    if(store.raw) rs$raw[[temp$files.list]] <- temp$raw[[temp$files.list]]
  }
  
  return(rs)
}

