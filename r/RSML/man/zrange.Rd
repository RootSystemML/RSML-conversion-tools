% Generated by roxygen2 (4.0.2): do not edit by hand
\name{zrange}
\alias{zrange}
\title{Compute the xrange of the root}
\usage{
zrange(obj)
}
\arguments{
\item{obj}{of class root}
}
\value{
c(y1,y2) where y1 and y2 are the y limits of the root
}
\description{
Compute the xrange of the root
}
\examples{
data(lupin)
r <- lupin$roots[[1]]
zrange(r)
}
\keyword{rsml}

