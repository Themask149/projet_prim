#include "core/c_arm/ecp_C25519.h"
#include "core/c_arm/big_256_29.h"

extern void init_SYSCLK();
extern void init_Cortex();

ECP_C25519 multiply(char s[32]){
    ECP_C25519 G;
    BIG_256_29 r;
    BIG_256_29_fromBytesLen(r, s,32);
    ECP_C25519_generator(&G);
    ECP_C25519_mul(&G, r);
    return G;
}

int main() {
    volatile int nbtest=1;
    init_SYSCLK();
    init_Cortex();
    char s[32]={0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                         0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                         0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                         0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x02};
    for (int i=0; i<nbtest; i++){
        ECP_C25519 res = multiply(s);
        BIG_256_29 res_in_big;
        ECP_C25519_get(res_in_big, &res);
        int dumb = BIG_256_29_comp(res_in_big, res_in_big);
        if (dumb){
            return 1;
        }
    }
    return 0;
}