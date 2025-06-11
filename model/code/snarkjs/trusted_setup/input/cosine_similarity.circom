pragma circom 2.0.0;

// Template principal
template SimilaridadeCossenos() {
    // Dimensões dos vetores
    var n = 512;
    
    // Entradas
    signal input embedding1[n];
    signal input embedding2[n];
    signal input threshold;
    
    // Saida
    signal output resultado; // 1 se similaridade > threshold, 0 caso contrário
    
    // Variáveis resultantes das somas
    var produto_escalar = 0;
    var norma1_quadrado = 0;
    var norma2_quadrado = 0;

    // Variáveis resultantes dos produtos
    var prod12 = 1;
    var prod11 = 1;
    var prod22 = 1;
    
    // 
    for (var i = 0; i < n; i++) {
        prod12 = embedding1[i] * embedding2[i];
        produto_escalar += prod12;
        prod11 = embedding1[i] * embedding1[i];
        norma1_quadrado += prod11;
        prod22 = embedding2[i] * embedding2[i];
        norma2_quadrado += prod22;
    }

    var quadrado_produto_escalar = produto_escalar * produto_escalar;

    var produto_normas_quadrado = norma1_quadrado * norma2_quadrado;

    // produto_normas_quadrado não pode ser zero
    var similaridade = quadrado_produto_escalar / produto_normas_quadrado;

    var limiar = threshold * threshold;
    
    // Se similaridade >= limiar, então resultado = 1, senão resultado = 0
    resultado <-- (similaridade >= limiar) ? 1 : 0;
    
    // Constraints para garantir integridade, o resultado é 0 ou 1
    resultado * (resultado - 1) === 0;
}

component main {public [threshold]} = SimilaridadeCossenos();