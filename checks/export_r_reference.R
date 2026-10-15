# Maintainer-only comparison; R is not required to run the Python chapter.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args) == 2)
reference_root <- normalizePath(args[1], mustWork=TRUE)
output_file <- args[2]
renv_lib <- list.dirs(file.path(reference_root, 'renv/library/windows'), recursive=TRUE)
candidate <- renv_lib[grepl('x86_64', renv_lib) & !grepl('jsonlite', renv_lib)]
# Use the approved reference library, never install or modify packages here.
jsonlite_locations <- list.files(file.path(reference_root, 'renv/library'),
                                 pattern='^jsonlite$', recursive=TRUE, full.names=TRUE,
                                 include.dirs=TRUE)
if(length(jsonlite_locations)) .libPaths(c(dirname(jsonlite_locations[1]), .libPaths()))
x <- readRDS(file.path(reference_root, 'output/03-merton/numeric-results.rds'))
names_needed <- c('V0','sv','pd_merton','pd1','d1','d2','Nd1','Nd2','start_V0','start_sv',
 'merton_default_threshold','market_value_debt','pv_promised_payment_debt','credit_value_gap',
 'implied_loss_rate','implied_lgd','implied_recovery_rate','reconstructed_debt_value',
 'merton_implied_debt_yield','merton_implied_spread','gbm_example_value',
 'FG.V0','FG.sv','pd.E','pd.rf','pd.D','pd.T','pd.se',paste0('E',1:5),paste0('T',1:5),
 'pd_scenario_2_initial','pd_scenario_3_initial','scenario1_reduce_D','scenario1_raise_E',
 'scenario2_reduce_D','scenario2_raise_E','scenario3_more_debt','scenario3_more_time')
stopifnot(all(names_needed %in% names(x)))
out <- x[names_needed]
out$pd_surface_50 <- t(matrix(x$pd_grid$risk_neutral_pd, nrow=50))
out$pd_surface_40 <- t(x$p_E_se)
jsonlite::write_json(out, output_file, auto_unbox=TRUE, digits=16, pretty=TRUE, matrix='rowmajor')
cat('Exported',length(out),'numeric reference groups.\n')
