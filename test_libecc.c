#include <libecc/libec.h>

extern void init_SYSCLK();
extern void init_Cortex();

int main(void){
    init_SYSCLK();
    init_Cortex();
    const ec_str_params *ec_str_params;
    ec_params curve_params;
    // nn_t private_key = NULL;
    ec_get_curve_params_by_type(WEI25519 ,&ec_str_params);
    int ret = import_params(&curve_params, ec_str_params);
    if (ret) {
        for(;;){}
        return -1;
    }
    // nn_init(private_key,32);
    // nn_set_word_value(private_key,2);
    // prj_pt Q;
    // ret = prj_pt_init(&Q, &(curve_params.ec_curve));
    // ret = prj_pt_mul(&Q, private_key,&(curve_params.ec_gen));
    // aff_pt_t out;
    // prj_pt_to_aff_pt(&out, &Q, &(curve_params.ec_curve));
    return 0;

    
}