# Re-execute the reference calibration settings for the flagged input points.
# This is a maintainer diagnostic, not a dependency of the Python implementation.
cases <- read.csv('.local/merton-discrepancy-cases.csv')
for (i in seq_len(nrow(cases))) {
  q <- cases[i, ]
  E0 <- q$equity; se <- q$equity_vol; rf <- q$rate
  TT <- q$maturity; D <- q$debt
  errors <- function(x) {
    V0 <- x[1]; sv <- x[2]
    d1 <- (log(V0/D)+(rf+sv^2/2)*TT)/(sv*sqrt(TT))
    d2 <- d1-sv*sqrt(TT)
    c(V0*pnorm(d1)-D*exp(-rf*TT)*pnorm(d2)-E0,
      pnorm(d1)*sv*V0-se*E0)
  }
  start_V0 <- E0+D*exp(-rf*TT)
  start_sv <- se*E0/start_V0
  solution <- optim(c(start_V0,start_sv),function(x)sum(errors(x)^2),
    method='L-BFGS-B',lower=c(1e-6,1e-6),
    control=list(parscale=c(10,0.2),ndeps=c(1e-6,1e-8)))
  V0 <- solution$par[1]; sv <- solution$par[2]
  d2 <- (log(V0/D)+(rf-sv^2/2)*TT)/(sv*sqrt(TT))
  cases$R_rerun_PD[i] <- pnorm(-d2)
  cases$R_max_residual[i] <- max(abs(errors(solution$par)))
  cases$R_objective[i] <- sum(errors(solution$par)^2)
  cases$R_convergence[i] <- solution$convergence
  stopifnot(abs(cases$R_rerun_PD[i]-cases$R_PD[i])<1e-10)
}
write.csv(cases,'.local/merton-optimizer-diagnostics.csv',row.names=FALSE)
print(cases[,c('Object','Index','R_max_residual','Python_residual','difference_bps')])
