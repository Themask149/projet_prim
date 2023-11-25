#include "./board/stm32f4xx.h"
#include "./board/core_board/core_cm4.h"


void init_SYSCLK(){

    // clock > 144MHZ

    RCC->APB1ENR |= RCC_APB1ENR_PWREN;
    PWR->CR &= ~PWR_CR_VOS_Msk;
    while ((PWR->CSR & PWR_CSR_VOSRDY));

    // PLL /2 * 21 to achieve an HSI of 168MHz
    RCC->PLLCFGR &= ~RCC_PLLCFGR_PLLM_Msk;
    RCC->PLLCFGR |= 2<< RCC_PLLCFGR_PLLM_Pos;
    RCC->PLLCFGR &= ~RCC_PLLCFGR_PLLN_Msk;
    RCC->PLLCFGR |= (21<< RCC_PLLCFGR_PLLN_Pos);

    // We need to divide APB2 by 2 and APB1 by 4 
    RCC->CFGR &= ~RCC_CFGR_PPRE1_Msk;
    RCC->CFGR |= RCC_CFGR_PPRE1_DIV4;
    RCC->CFGR &= ~RCC_CFGR_PPRE2_Msk;
    RCC->CFGR |= RCC_CFGR_PPRE2_DIV2;

    //ACTIVATE PLL on SW
    RCC->CR |= RCC_CR_PLLON;
    while(!(RCC->CR & RCC_CR_PLLRDY));

    //enable cache
    FLASH->ACR |= FLASH_ACR_ICEN;
    FLASH->ACR |= FLASH_ACR_DCEN;

    //5 waitstates

    FLASH->ACR |= FLASH_ACR_LATENCY_5WS;
    while (!(FLASH->ACR & FLASH_ACR_LATENCY_5WS));

    // Select PLL as system clock
    RCC->CFGR &= ~RCC_CFGR_SW_Msk;
    RCC->CFGR |= RCC_CFGR_SW_1;
    while(!(RCC->CFGR & RCC_CFGR_SWS_1));

}

void init_Cortex(){
    //DEMCR.TRCENA == 1
    CoreDebug->DEMCR &= ~CoreDebug_DEMCR_TRCENA_Msk;
    CoreDebug->DEMCR |= (1<<CoreDebug_DEMCR_TRCENA_Pos);

    // DWT_CTRL.CYCNTENA == 1 
    DWT->CTRL &= ~DWT_CTRL_CYCCNTENA_Msk;
    DWT->CTRL |= (1<<DWT_CTRL_CYCCNTENA_Pos);
}
