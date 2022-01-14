/*
 * MATLAB Compiler: 6.6 (R2018a)
 * Date: Thu Feb 11 13:47:27 2021
 * Arguments:
 * "-B""macro_default""-W""lib:MultiRegimes""-T""link:lib""-d""C:\Users\sberu\Do
 * cuments\matlab\Finance\MultiRegimesPy\for_testing""-v""C:\Users\sberu\Documen
 * ts\matlab\Finance\Matlab\Regimes_sb\CalcRegimeProbAtT.m""C:\Users\sberu\Docum
 * ents\matlab\Finance\Matlab\Solutions_sb\General_Solution_py.m"
 */

#include <stdio.h>
#define EXPORTING_MultiRegimes 1
#include "MultiRegimes.h"

static HMCRINSTANCE _mcr_inst = NULL;

#if defined( _MSC_VER) || defined(__LCC__) || defined(__MINGW64__)
#ifdef __LCC__
#undef EXTERN_C
#endif
#include <windows.h>

static char path_to_dll[_MAX_PATH];

BOOL WINAPI DllMain(HINSTANCE hInstance, DWORD dwReason, void *pv)
{
    if (dwReason == DLL_PROCESS_ATTACH)
    {
        if (GetModuleFileName(hInstance, path_to_dll, _MAX_PATH) == 0)
            return FALSE;
    }
    else if (dwReason == DLL_PROCESS_DETACH)
    {
    }
    return TRUE;
}
#endif
#ifdef __cplusplus
extern "C" {
#endif

static int mclDefaultPrintHandler(const char *s)
{
    return mclWrite(1 /* stdout */, s, sizeof(char)*strlen(s));
}

#ifdef __cplusplus
} /* End extern "C" block */
#endif

#ifdef __cplusplus
extern "C" {
#endif

static int mclDefaultErrorHandler(const char *s)
{
    int written = 0;
    size_t len = 0;
    len = strlen(s);
    written = mclWrite(2 /* stderr */, s, sizeof(char)*len);
    if (len > 0 && s[ len-1 ] != '\n')
        written += mclWrite(2 /* stderr */, "\n", sizeof(char));
    return written;
}

#ifdef __cplusplus
} /* End extern "C" block */
#endif

/* This symbol is defined in shared libraries. Define it here
 * (to nothing) in case this isn't a shared library. 
 */
#ifndef LIB_MultiRegimes_C_API
#define LIB_MultiRegimes_C_API /* No special import/export declaration */
#endif

LIB_MultiRegimes_C_API 
bool MW_CALL_CONV MultiRegimesInitializeWithHandlers(
    mclOutputHandlerFcn error_handler,
    mclOutputHandlerFcn print_handler)
{
    int bResult = 0;
    if (_mcr_inst != NULL)
        return true;
    if (!mclmcrInitialize())
        return false;
    if (!GetModuleFileName(GetModuleHandle("MultiRegimes"), path_to_dll, _MAX_PATH))
        return false;
    {
        mclCtfStream ctfStream = 
            mclGetEmbeddedCtfStream(path_to_dll);
        if (ctfStream) {
            bResult = mclInitializeComponentInstanceEmbedded(&_mcr_inst,
                                                             error_handler, 
                                                             print_handler,
                                                             ctfStream);
            mclDestroyStream(ctfStream);
        } else {
            bResult = 0;
        }
    }  
    if (!bResult)
    return false;
    return true;
}

LIB_MultiRegimes_C_API 
bool MW_CALL_CONV MultiRegimesInitialize(void)
{
    return MultiRegimesInitializeWithHandlers(mclDefaultErrorHandler, 
                                            mclDefaultPrintHandler);
}

LIB_MultiRegimes_C_API 
void MW_CALL_CONV MultiRegimesTerminate(void)
{
    if (_mcr_inst != NULL)
        mclTerminateInstance(&_mcr_inst);
}

LIB_MultiRegimes_C_API 
void MW_CALL_CONV MultiRegimesPrintStackTrace(void) 
{
    char** stackTrace;
    int stackDepth = mclGetStackTrace(&stackTrace);
    int i;
    for(i=0; i<stackDepth; i++)
    {
        mclWrite(2 /* stderr */, stackTrace[i], sizeof(char)*strlen(stackTrace[i]));
        mclWrite(2 /* stderr */, "\n", sizeof(char)*strlen("\n"));
    }
    mclFreeStackTrace(&stackTrace, stackDepth);
}


LIB_MultiRegimes_C_API 
bool MW_CALL_CONV mlxCalcRegimeProbAtT(int nlhs, mxArray *plhs[], int nrhs, mxArray 
                                       *prhs[])
{
    return mclFeval(_mcr_inst, "CalcRegimeProbAtT", nlhs, plhs, nrhs, prhs);
}

LIB_MultiRegimes_C_API 
bool MW_CALL_CONV mlxGeneral_Solution_py(int nlhs, mxArray *plhs[], int nrhs, mxArray 
                                         *prhs[])
{
    return mclFeval(_mcr_inst, "General_Solution_py", nlhs, plhs, nrhs, prhs);
}

LIB_MultiRegimes_C_API 
bool MW_CALL_CONV mlfCalcRegimeProbAtT(int nargout, mxArray** Y_t_t, mxArray** Y_t_1_t, 
                                       mxArray** smoothed_prob, mxArray* returns, 
                                       mxArray* A, mxArray* B, mxArray* P, mxArray* 
                                       predictor, mxArray* var_cov, mxArray* pi_inf)
{
    return mclMlfFeval(_mcr_inst, "CalcRegimeProbAtT", nargout, 3, 7, Y_t_t, Y_t_1_t, smoothed_prob, returns, A, B, P, predictor, var_cov, pi_inf);
}

LIB_MultiRegimes_C_API 
bool MW_CALL_CONV mlfGeneral_Solution_py(int nargout, mxArray** alpha_perc, mxArray** 
                                         Ct_Wt_perc, mxArray** coefficients, mxArray* 
                                         gamma1, mxArray* horizon, mxArray* pi_t, 
                                         mxArray* parameters, mxArray* coefficients_in1)
{
    return mclMlfFeval(_mcr_inst, "General_Solution_py", nargout, 3, 5, alpha_perc, Ct_Wt_perc, coefficients, gamma1, horizon, pi_t, parameters, coefficients_in1);
}

