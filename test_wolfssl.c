#include "wolfssl/wolfssl/options.h"
#include "wolfssl/wolfssl/wolfcrypt/settings.h"
#include "wolfssl/wolfssl/wolfcrypt/curve25519.h"
#define CURVE25519_KEYSIZE 32

static const word32 kCurve25519BasePoint[CURVE25519_KEYSIZE/sizeof(word32)] = {
#ifdef BIG_ENDIAN_ORDER
    0x09000000
#else
    9
#endif
};

int main(void){
    int ret;
    byte in[32] = {0};
    byte out[32];

    in[31]=1;
    fe_init();

    SAVE_VECTOR_REGISTERS(return _svr_ret;);

    ret = curve25519(out, in, (byte*)kCurve25519BasePoint);

    RESTORE_VECTOR_REGISTERS();
    for (;;){

    }
    return ret;
}