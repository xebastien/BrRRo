/*
 * MATLAB Compiler: 6.6 (R2018a)
 * Date: Thu Feb 11 13:47:27 2021
 * Arguments:
 * "-B""macro_default""-W""lib:MultiRegimes""-T""link:lib""-d""C:\Users\sberu\Do
 * cuments\matlab\Finance\MultiRegimesPy\for_testing""-v""C:\Users\sberu\Documen
 * ts\matlab\Finance\Matlab\Regimes_sb\CalcRegimeProbAtT.m""C:\Users\sberu\Docum
 * ents\matlab\Finance\Matlab\Solutions_sb\General_Solution_py.m"
 */

#ifndef __MultiRegimes_h
#define __MultiRegimes_h 1

#if defined(__cplusplus) && !defined(mclmcrrt_h) && defined(__linux__)
#  pragma implementation "mclmcrrt.h"
#endif
#include "mclmcrrt.h"
#ifdef __cplusplus
extern "C" {
#endif

/* This symbol is defined in shared libraries. Define it here
 * (to nothing) in case this isn't a shared library. 
 */
#ifndef LIB_MultiRegimes_C_API 
#define LIB_MultiRegimes_C_API /* No special import/export declaration */
#endif

/* GENERAL LIBRARY FUNCTIONS -- START */

extern LIB_MultiRegimes_C_API 
bool MW_CALL_CONV MultiRegimesInitializeWithHandlers(
       mclOutputHandlerFcn error_handler, 
       mclOutputHandlerFcn print_handler);

extern LIB_MultiRegimes_C_API 
bool MW_CALL_CONV MultiRegimesInitialize(void);

extern LIB_MultiRegimes_C_API 
void MW_CALL_CONV MultiRegimesTerminate(void);

extern LIB_MultiRegimes_C_API 
void MW_CALL_CONV MultiRegimesPrintStackTrace(void);

/* GENERAL LIBRARY FUNCTIONS -- END */

/* C INTERFACE -- MLX WRAPPERS FOR USER-DEFINED MATLAB FUNCTIONS -- START */

extern LIB_MultiRegimes_C_API 
bool MW_CALL_CONV mlxCalcRegimeProbAtT(int nlhs, mxArray *plhs[], int nrhs, mxArray 
                                       *prhs[]);

extern LIB_MultiRegimes_C_API 
bool MW_CALL_CONV mlxGeneral_Solution_py(int nlhs, mxArray *plhs[], int nrhs, mxArray 
                                         *prhs[]);

/* C INTERFACE -- MLX WRAPPERS FOR USER-DEFINED MATLAB FUNCTIONS -- END */

/* C INTERFACE -- MLF WRAPPERS FOR USER-DEFINED MATLAB FUNCTIONS -- START */

extern LIB_MultiRegimes_C_API bool MW_CALL_CONV mlfCalcRegimeProbAtT(int nargout, mxArray** Y_t_t, mxArray** Y_t_1_t, mxArray** smoothed_prob, mxArray* returns, mxArray* A, mxArray* B, mxArray* P, mxArray* predictor, mxArray* var_cov, mxArray* pi_inf);

extern LIB_MultiRegimes_C_API bool MW_CALL_CONV mlfGeneral_Solution_py(int nargout, mxArray** alpha_perc, mxArray** Ct_Wt_perc, mxArray** coefficients, mxArray* gamma1, mxArray* horizon, mxArray* pi_t, mxArray* parameters, mxArray* coefficients_in1);

#ifdef __cplusplus
}
#endif
/* C INTERFACE -- MLF WRAPPERS FOR USER-DEFINED MATLAB FUNCTIONS -- END */

#endif
