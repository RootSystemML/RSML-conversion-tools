#' Append 2 rsml files
#' @param rsml1    The first RSML object. Mandatory.
#' @param rsml2    The second RSML object. Mandatory.
#' @keywords rsml
#' @export
#' @examples
#' append.rsml()
append.rsml<- function(rsml1, rsml2){
  rs <- list()
  rs$processed <- rbind(rsml1$processed, rsml2$processed)
  rs$files.list <- c(rsml1$files.list, rsml2$files.list)
  for(n in rsml1$files.list) rs$raw[[n]] <- rsml1$raw[[n]]  
  for(n in rsml2$files.list) rs$raw[[n]] <- rsml2$raw[[n]]  
  return(rs)
}
