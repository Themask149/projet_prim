#include "core/c_arm/ecp_C25519.h"
#include "core/c_arm/big_256_29.h"

extern void init_SYSCLK();
extern void init_Cortex();

// not enough space on the stack!!!!! Always use global vars for an embedded target. There was a stack overflow in the code!!!
int nbtest=1;

ECP_C25519 G;
BIG_256_29 res_in_big;
char s[32]={
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
    0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x02
};

void multiply(ECP_C25519* G, char s[32]) {
    BIG_256_29 r;
    BIG_256_29_fromBytesLen(r, s, 32);
    ECP_C25519_generator(G);
    ECP_C25519_mul(G, r);
}

int main() {
    init_SYSCLK();
    init_Cortex();

    for (int i=0; i<nbtest; i++){
        multiply(&G, s);

        ECP_C25519_get(res_in_big, &G); // extract x
        /*int dumb = BIG_256_29_comp(res_in_big, res_in_big);
        if (dumb){ // pourquoi ?
            return 1;
        }*/
        BIG_256_29_toBytes(s, res_in_big);
    }
    return 0;
}