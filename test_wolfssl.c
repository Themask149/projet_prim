#include "wolfssl/wolfssl/options.h"
#include "wolfssl/wolfssl/wolfcrypt/settings.h"
#include "wolfssl/wolfssl/wolfcrypt/curve25519.h"
#include "wolfssl/wolfssl/wolfcrypt/aes.h"
#define CURVE25519_KEYSIZE 32

extern void init_SYSCLK();
extern void init_Cortex();

static const word32 kCurve25519BasePoint[CURVE25519_KEYSIZE/sizeof(word32)] = {
#ifdef BIG_ENDIAN_ORDER
    0x09000000
#else
    9
#endif
};

volatile int nbtest=10;
byte in[32] = {0};
byte out[32];
byte aes_key[AES_256_KEY_SIZE] = {0}; 
byte iv[AES_BLOCK_SIZE] = {0};

void clamping(byte *key){
    key[31]&=0xF8;
    key[0]&=0x7F;
    key[0]|=0x40;
}

int main(void){
    int ret=0;
    Aes aes;
    //Set aes_key and iv via python before;
    init_SYSCLK();
    init_Cortex();
    ret=wc_AesSetKey(&aes, aes_key, sizeof(aes_key), iv, AES_ENCRYPTION);
    if (ret!=0){
        for(;;){}
    };
    for (int i =0;i<nbtest;i++){
        //pseudo aleatoire in
        ret=wc_AesCbcEncrypt(&aes, in, in, sizeof(in));
        if (ret!=0){
            for(;;){}
            };
        clamping(in);
        ret = curve25519(out, in, (byte*)kCurve25519BasePoint);
        if (ret!=0){
            for(;;){}
            }
    }
    return ret;
}