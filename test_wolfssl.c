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
    key[0]&=0xF8;
    key[31]&=0x7F;
    key[31]|=0x40;
}

unsigned rev1(byte x) {
   x = (x & 0x55) <<  1 | (x & 0xAA) >>  1;
   x = (x & 0x33) <<  2 | (x & 0xCC) >>  2;
   x = (x & 0x0F) <<  4 | (x & 0xF0) >>  4;
   return x;
}

void reverse(byte *key){
    byte temp; 
    for (int i = 0; i<16;i++){
        temp = rev1(key[i]);
        key[i]=rev1(key[31-i]);
        key[31-i]=temp;
    }
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
        reverse(in);
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