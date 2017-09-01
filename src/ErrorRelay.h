/*
Header file for ErrorRelay.c

The header file is needed in this case for the Cython wrapping process which
wants and extern cdef declaration to interface the c language function with
the Cython and Python code.

*/
void CopyMsgToOutputs(const char* sMsg, double* outargs);

//EOF