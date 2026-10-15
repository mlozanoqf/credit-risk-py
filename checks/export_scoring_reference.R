# Maintainer-only export. Writes restricted validation artifacts outside Git.
args <- commandArgs(trailingOnly=TRUE)
stopifnot(length(args)==2)
root <- normalizePath(args[1], mustWork=TRUE)
out <- normalizePath(args[2], mustWork=TRUE)
loc <- list.files(file.path(root,'renv/library'), pattern='^jsonlite$',
 recursive=TRUE, full.names=TRUE, include.dirs=TRUE)
stopifnot(length(loc)>0)
.libPaths(c(dirname(loc[1]), .libPaths()))
setwd(root)
source('chapters/02-tree-based/helpers/models.R')
xgboost::xgb.save(xgb_model,file.path(out,'r-xgb-reference.ubj'))
jsonlite::write_json(xgboost::xgb.config(xgb_model),file.path(out,'r-xgb-config.json'),auto_unbox=TRUE,pretty=TRUE)
write.csv(data.frame(file_row=c(as.integer(rownames(train)),as.integer(rownames(test))),
 split=c(rep('train',nrow(train)),rep('test',nrow(test)))),
 file.path(out,'reference-split.csv'),row.names=FALSE)
save_reference <- function(id) {
 x <- readRDS(file.path(root,'output',id,'numeric-results.rds'))
 x <- lapply(x,function(v) {
   if (inherits(v,'table')) { class(v)<-NULL; return(v) }
   if (is.object(v) && is.numeric(v) && !is.data.frame(v)) {
     if(is.null(dim(v))) return(as.numeric(v)) else return(unclass(v))
   }
   v
 })
 jsonlite::write_json(x,file.path(out,paste0(id,'.json')),auto_unbox=TRUE,
   digits=16,pretty=FALSE,matrix='rowmajor',na='null')
}
for(id in c('00-foundations','01-logistic','02-tree-based')) save_reference(id)
models <- list(age=logi_age,int=logi_int,multi=logi_multi,full=logi_full)
tight_models <- lapply(models,function(m) update(m,control=glm.control(epsilon=1e-12,maxit=100)))
reference <- list(
 factors=lapply(dat[vapply(dat,is.factor,logical(1))],levels),
 columns=colnames(xgb_train_matrix),
 coefficients=lapply(models,coef),
 coefficient_names=lapply(models,function(m)names(coef(m))),
 standard_errors=lapply(models,function(m)summary(m)$coefficients[,2]),
 p_values=lapply(models,function(m)summary(m)$coefficients[,4]),
 aic=lapply(models,AIC),
 tight_standard_errors=lapply(tight_models,function(m)summary(m)$coefficients[,2]),
 tight_p_values=lapply(tight_models,function(m)summary(m)$coefficients[,4]),
 predictions=lapply(models,function(m)predict(m,test,type='response')),
 tree=pred_tree_simple,xgb=pred_xgb,
 train_matrix=xgb_train_matrix,test_matrix=xgb_test_matrix,
 train_y=xgb_train_label,test_y=xgb_test_label,
 train_rows=as.integer(rownames(train)),test_rows=as.integer(rownames(test)),
 model_metrics=model_metrics,strategy=strategy_comparison,
 calibration=calibration_comparison,importance=xgb_importance,
 shap_importance=xgb_shap_importance,pdp=partial_dependence_data,
 learning=xgb_learning_curve,
 tree_leaves=sum(simple_tree$frame$var=='<leaf>'),
 xgb_version=as.character(packageVersion('xgboost')))
jsonlite::write_json(reference,file.path(out,'scoring-reference.json'),
 auto_unbox=TRUE,digits=16,pretty=FALSE,matrix='rowmajor',na='null')
cat('Exported reference matrices, predictions, metrics, split and snapshots.\n')
cat('XGBoost',as.character(packageVersion('xgboost')),'\n')
