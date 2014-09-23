
#' Plot a single RSML
#' @param rsml   rsml$raw$image object, previously imported using the oneRSMLToList function. Mandatory.
#' @param rev    Reverse the orizntation of the root system (y axis)
#' @keywords rsml
#' @import XML 
#' @examples
#' plotRSML()
plot.rsml <- function(rsml, rev=T, combine = F){  
  
  #rsml <- rs1$raw
  images <- names(rsml)
  
  if(combine){
    # Find best display fo the graphs
    l <- length(images)  
    for(i in 1:10) if((l/i) >= i) row <- i
    col <- ceiling(l/row)
    par(mfrow=c(row, col))
  }
  
  for(im in images){
    print(paste("Plotting image ",im,sep=""))
    plant <- rsml[[im]]$scene
  
    coeff = 1
    if(rev) coeff = -1

    # Get the boundaries for the plot
    xmin = Inf; xmax = -Inf; ymin = Inf; ymax = -Inf
    for(r0 in plant){
    for(r1 in r0){
      if("geometry" %in% names(r1)){
        p <- r1$geometry$polyline
        for(i in 1:length(p)){
          xmin = min(as.numeric(p[i][[1]][1]), xmin)
          xmax = max(as.numeric(p[i][[1]][1]), xmax)
          ymin = min(as.numeric(p[i][[1]][2])*coeff, ymin)
          ymax = max(as.numeric(p[i][[1]][2])*coeff, ymax)
        }
        if("root" %in% names(r1)){
          for(r2 in r1){  
            if("geometry" %in% names(r2)){
              p <- r2$geometry$polyline
              for(i in 1:length(p)){
                xmin = min(as.numeric(p[i][[1]][1]), xmin)
                xmax = max(as.numeric(p[i][[1]][1]), xmax)
                ymin = min(as.numeric(p[i][[1]][2])*coeff, ymin)
                ymax = max(as.numeric(p[i][[1]][2])*coeff, ymax)
              }
              if("root" %in% names(r2)){
                for(r3 in r2){
                  if("geometry" %in% names(r3)){
                    p <- r3$geometry$polyline
                    for(i in 1:length(p)){
                      xmin = min(as.numeric(p[i][[1]][1]), xmin)
                      xmax = max(as.numeric(p[i][[1]][1]), xmax)
                      ymin = min(as.numeric(p[i][[1]][2])*coeff, ymin)
                      ymax = max(as.numeric(p[i][[1]][2])*coeff, ymax)
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  
    # Plot the structure
    plot(c(xmin,xmax), c(ymin, ymax), type="n", xlab="", ylab="", main=im)
    for(r0 in plant){
    for(r1 in r0){
      if("geometry" %in% names(r1)){
        p <- r1$geometry$polyline
        x <- rep(0, length(p))
        y <- x
        for(i in 1:length(p)){
          x[i] <- p[i][[1]][1]
          y[i] <- as.numeric(p[i][[1]][2]) * coeff
        }
        lines(x, y)
        if("root" %in% names(r1)){
          for(r2 in r1){  
            if("geometry" %in% names(r2)){
              p <- r2$geometry$polyline
              x <- rep(0, length(p))
              y <- x
              for(i in 1:length(p)){
                x[i] <- p[i][[1]][1]
                y[i] <- as.numeric(p[i][[1]][2]) * coeff
              }
              lines(x, y, col="green")
              if("root" %in% names(r2)){
                for(r3 in r2){
                  if("geometry" %in% names(r3)){
                    p <- r3$geometry$polyline
                    x <- rep(0, length(p))
                    y <- x
                    for(i in 1:length(p)){
                      x[i] <- p[i][[1]][1]
                      y[i] <- as.numeric(p[i][[1]][2]) * coeff
                    }
                    lines(x, y, col="green")
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  
  
  }
}
