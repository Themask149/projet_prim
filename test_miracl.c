#include "core/c_arm/ecp_C25519.h"
#include "core/c_arm/big_256_29.h"
#include "core/c_arm/core.h"

extern void init_SYSCLK();
extern void init_Cortex();

#define KK 32

volatile int nbtest=1;
core_aes a;    
char key[32]={0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                         0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                         0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                         0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
char iv[16]={0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                         0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};
char s[32]={0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                         0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                         0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
                         0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x02};
ECP_C25519 res;
BIG_256_29 res_in_big;

void multiply(char s[32], ECP_C25519 *res){
    BIG_256_29 r;
    BIG_256_29_fromBytesLen(r, s,32);
    ECP_C25519_generator(res);
    // put Syscnt to 0 ARRET
    ECP_C25519_mul(res, r);
    // gather Syscnt ARRET
}
void clamping(char key[32]){
    key[31]&=0xF8;
    key[0]&=0x7F;
    key[0]|=0x40;
}

void random_aes(core_aes *a, char random[32]){
    // on veut à partir d'une clé et d'un iv généré par python
    // clé 32 bytes mais on veut la sortie de AES = 32 bytes
    AES_encrypt(a,random);
    AES_encrypt(a,random+16);
    clamping(random);
}

int min(int a, int b){
    if (a<b){
        return a;
    }
    return b;
}


int main() {
    //init nbround here
    init_SYSCLK();
    init_Cortex();
    while (nbtest>0){
        //here init key iv at random with python ARRET
        AES_init(&a,CTR16,KK,key,iv);
        for (int i=0; i<min(nbtest,100); i++){
            random_aes(&a,s);
            ECP_C25519 res;
            multiply(s,&res);
            BIG_256_29 res_in_big;
            ECP_C25519_get(res_in_big, &res);
            BIG_256_29_toBytes(s, res_in_big);     
        }
        nbtest=nbtest-min(nbtest,100);
        AES_end(&a);
    }

    // for (int i=0; i<nbtest; i++){
    //     multiply(s,&res);
    //     ECP_C25519_get(res_in_big, &res);
    //     BIG_256_29_toBytes(s, res_in_big);
    // }
    return 0;
}



