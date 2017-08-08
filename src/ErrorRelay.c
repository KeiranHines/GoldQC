/*
Returning Error Message from External Functions

This function is copied from the GoldSim User's Guide ---
see Appendix C, p. 1045 - 1046 in Volume II of the User's Guide.

From this Appendix:

"To help GoldSim users debug problems with DLL external functions, GoldSim
lets users send an error message from the DLL back to GoldSim through the
External element interface when the call to an external function fails. The 
error message is then displayed to the user in a pop-up dialog.

The DLL external function signals the presence of an error message by returning
a status value of -2. When GoldSim processes the results of the DLL external
function call, it will interpret the first element of the output arguments 
arrray (outargs in our source-code example) as a pointer to a memory location 
where the error string can be found. The memory containing the string must 
have static scope, so that it will still be available when GoldSim retrieves 
the string. The string must also be NULL-terminated, even when returning from 
a FORTRAN DLL. If either of these recommendations are not followed, GoldSim 
will likely crash when it tries to display the error message."

The function code in the appendix is an example of a C language function that 
will properly handle passing a message from a DLL external function to GoldSim.
The ULONG_PTR is cast to different types on 64-bit (unsigned long) and 32-bit 
(unsigned __int64), so that it will work for building both 32-bit and 64-bit
binaries. In this case, the compilation is done with gcc and the compilation
should produce a 32 bit binary for the dll. As a result, ULONG_PTR is 
replaced with unsigned long int.

*/

#include "ErrorRelay.h"
#include <string.h>

// Utility method used to simplify sending an error message to GoldSim
void CopyMsgToOutputs(const char* sMsg, double* outargs) {
    // Static character array used to hold the error message.
    // For the current incarnation of GoldSim, this is OK.
    // However, it will not be threadsafe if GoldSim simulations
    // become multithreaded.
    static char sBuffer[81];
    // Clear out any old data from the buffer
    memset(sBuffer, 0, sizeof(sBuffer));
    // Cast the first output array element as a pointer.
    // ULONG_PTR is used because it will work for both
    // 32-bit and 64-bit DLLs
    unsigned long int * pAddr = (unsigned long int*) outargs;
    // Copy the string data supplied into the static buffer.
    strncpy(sBuffer, sMsg, sizeof(sBuffer) - 1);
    // Copy the static buffer pointer to the first output array
    // element.
    *pAddr = (unsigned long int*) sBuffer;
}

//EOF