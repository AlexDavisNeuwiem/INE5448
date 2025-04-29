#include <iostream>
#include "teste.h"

int main() {
    std::cout << "Iniciando o programa principal...\n";

    int resultado = soma(10, 20);
    std::cout << "Resultado da soma: " << resultado << std::endl;

    imprime_mensagem("Teste concluído!");

    return 0;
}
