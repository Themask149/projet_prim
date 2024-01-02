#include "wolfssl/wolfssl/options.h"
#include "wolfssl/wolfssl/wolfcrypt/settings.h"
#include "wolfssl/wolfssl/wolfcrypt/curve25519.h"

int main(void){
    int ret;
    curve25519_key key;
    byte in[32] = {0};
    byte out[32];

    ret = wc_curve25519_init(&key);
    if (ret != 0) {
        printf("wc_curve25519_init failed with error %d\n", ret);
        return ret;
    }
    in[0] = 1;
    ret = wc_curve25519_mul(in,32,out,&key);
    if (ret != 0) {
        printf("wc_curve25519_mul failed with error %d\n", ret);
        wc_curve25519_free(&key);
        return ret;
    }

    wc_curve25519_free(&key);
}