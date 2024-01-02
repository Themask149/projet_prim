#include <libecc/libec.h>


int main(void){
    ec_str_params *ec_str_params;
    ec_curve_type ec_type;
    ec_params curve_params;
    nn_t private_key;
    ec_type=X25519;
    ec_get_curve_params_by_type(ec_type,&ec_str_params);
    int ret = import_params(ec_str_params, &curve_params);
    if (ret) {
        printf("Unable to import curve parameters\n");
        return -1;
    }
    nn_init(&private_key,0);
    nn_set_word_value(&private_key,2);
    prj_pt Q;
    ret = prj_pt_init(&Q, &(curve_params.ec_curve));
    ret = prj_pt_mul(&Q, private_key,&(curve_params.ec_gen));
    aff_pt_t out;
    prj_pt_to_aff_pt(&out, &Q, &(curve_params.ec_curve));
    
}