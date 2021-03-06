% Generated by roxygen2 (4.0.2): do not edit by hand
\name{totalLength}
\alias{totalLength}
\title{Compute the length of the root and its children based on the coordinates of its nodes}
\usage{
totalLength(obj)
}
\arguments{
\item{obj}{of class root}
}
\value{
the total lenght of the root and children
}
\description{
Compute the length of the root and its children based on the coordinates of its nodes
}
\examples{
data(lupin)
r <- lupin$roots[[1]]
totalLength(r)
}
\author{
Guillaume Lobet - guillaume.lobet(at)ulg.ac.be
}
\keyword{rsml}

