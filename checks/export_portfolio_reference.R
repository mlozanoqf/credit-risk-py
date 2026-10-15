# Maintainer-only. Execute reference calculations without rendering or writing in R repo.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==2)
root <- normalizePath(args[1],mustWork=TRUE)
out <- normalizePath(args[2],mustWork=TRUE)
libs <- list.files(file.path(root,'renv/library'),pattern='^jsonlite$',recursive=TRUE,full.names=TRUE,include.dirs=TRUE)
stopifnot(length(libs)>0)
.libPaths(c(dirname(libs[1]),.libPaths()))
setwd(root)
companion_kable <- function(x,...) invisible(x)
for (id in c('04-credit-spreads-cds','06-climate-credit-risk')) {
  text <- readLines(file.path('chapters',id,'chapter.qmd'),warn=FALSE)
  starts <- grep('^```\\{r ',text)
  for (start in starts) {
    end <- which(seq_along(text)>start & text=='```')[1]
    code <- text[(start+1):(end-1)]
    if(grepl('companion-setup|companion-results',text[start]) || any(grepl('^#\\| eval: false',code))) next
    invisible(eval(parse(text=code),envir=.GlobalEnv))
  }
  if(id=='04-credit-spreads-cds') {
    export <- list(comparison=rv_comparison,h=lapply(rv_results,function(x)x$h),
      all_bond_yields=vapply(rv_bonds,function(b)b$yield,numeric(1)),
      all_accrued=vapply(rv_bonds,function(b)b$accrued,numeric(1)),
      all_dv01=vapply(rv_bonds,function(b)b$dv01,numeric(1)),
      sensitivity=rv_sensitivity,components=rv_components_cco,
      sensitivity_ranges=rv_sensitivity_summary,hull_components=hull_components,
      rv_purchase_limit=rv_purchase_limit,rv_deduction=rv_deduction)
  } else {
    export <- list(climate_credit=climate_credit,horizon_loss=horizon_loss,
      portfolio_horizon_loss=portfolio_horizon_loss,daps_summary=daps_summary,
      spread_bridge=spread_bridge_gap,simulation_input=simulation_input,loss_summary=loss_summary,
      coal_survival=coal_hwtp_survival_start,coal_marginal=coal_hwtp_marginal_pd,
      coal_pv=coal_hwtp_pv_el)
  }
  jsonlite::write_json(export,file.path(out,paste0(id,'-reference.json')),digits=16,
    auto_unbox=TRUE,matrix='rowmajor',na='null')
  cat('Recomputed',id,'without changing R files.\n')
}
