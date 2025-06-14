pragma circom 2.0.0;

// Template para o cálculo do produto escalar entre dois vetores
template DotProduct(n) {
    signal input a[n];
    signal input b[n];
    signal output out;
    
    signal products[n];
    signal partial_sums[n];
    
    // Calcula produtos elemento por elemento
    for (var i = 0; i < n; i++) {
        products[i] <== a[i] * b[i];
    }
    
    // Soma acumulativa dos produtos
    partial_sums[0] <== products[0];
    for (var i = 1; i < n; i++) {
        partial_sums[i] <== partial_sums[i-1] + products[i];
    }
    
    out <== partial_sums[n-1];
}

// Template para calcular a norma de um vetor
template VectorNorm(n) {
    signal input vec[n];
    signal output norm_squared;
    
    signal squares[n];
    signal partial_sums[n];
    
    // Calcula o quadrado de cada elemento
    for (var i = 0; i < n; i++) {
        squares[i] <== vec[i] * vec[i];
    }
    
    // Soma acumulativa dos quadrados
    partial_sums[0] <== squares[0] * squares[0];
    for (var i = 1; i < n; i++) {
        partial_sums[i] <== partial_sums[i-1] + squares[i];
    }
    
    norm_squared <== partial_sums[n-1];
}

// Template principal para verificar similaridade de cossenos
template CosineSimilarity(n) {
    // Sinais de entrada
    signal input embedding1[n];
    signal input embedding2[n];
    signal input threshold;
    
    // Sinal de saída público (1 se passou no teste, 0 caso contrário)
    signal output result;
    
    // Componentes para cálculos
    component dot_product = DotProduct(n);
    component norm1 = VectorNorm(n);
    component norm2 = VectorNorm(n);
    
    // Conecta as embeddings aos componentes
    for (var i = 0; i < n; i++) {
        dot_product.a[i] <== embedding1[i];
        dot_product.b[i] <== embedding2[i];
        norm1.vec[i] <== embedding1[i];
        norm2.vec[i] <== embedding2[i];
    }
    
    // Calcula produto escalar e normas
    signal dot_prod <== dot_product.out * 10; // Ajuste necessário, ver model/code/enums.py
    signal norm1_sq <== norm1.norm_squared;
    signal norm2_sq <== norm2.norm_squared;
    
    // Calcula o produto das normas
    signal norms_product <== norm1_sq * norm2_sq;
    
    // Para evitar o cálculo da divisão e raiz, comparamos:
    // dot_prod / sqrt(norm1_sq * norm2_sq) >= threshold
    // Equivalente a: dot_prod >= threshold * sqrt(norm1_sq * norm2_sq)
    // Elevando ao quadrado: dot_prod² >= threshold² * norm1_sq * norm2_sq
    signal left_side <== dot_prod * dot_prod;

    signal threshold_squared <== threshold * threshold;
    signal right_side <== threshold_squared * norms_product;
    
    // Verifica se left_side >= right_side
    component ge_check = GreaterEqThan(252);
    ge_check.in[0] <== left_side;
    ge_check.in[1] <== right_side;
    
    result <== ge_check.out;
}

// Templates auxiliares retirados do circomlib (não sei importar kkkk)
template Num2Bits(n) {
    signal input in;
    signal output out[n];
    var lc1=0;

    var e2=1;
    for (var i = 0; i<n; i++) {
        out[i] <-- (in >> i) & 1;
        out[i] * (out[i] -1 ) === 0;
        lc1 += out[i] * e2;
        e2 = e2+e2;
    }

    lc1 === in;
}

template LessThan(n) {
    assert(n <= 252);
    signal input in[2];
    signal output out;

    component n2b = Num2Bits(n+1);

    n2b.in <== in[0]+ (1<<n) - in[1];

    out <== 1-n2b.out[n];
}

template GreaterEqThan(n) {
    signal input in[2];
    signal output out;

    component lt = LessThan(n);

    lt.in[0] <== in[1];
    lt.in[1] <== in[0]+1;
    lt.out ==> out;
}

// Instância do circuito principal
// Parâmetro: dimensão das embeddings = 512
component main {public [threshold]} = CosineSimilarity(512);

/*
EXPLICAÇÃO DO CIRCUITO:

1. **Entradas Privadas**: Duas embeddings de dimensão n

2. **Cálculo da Similaridade de Cossenos**:
   - Calcula o produto escalar (dot product) entre as duas embeddings
   - Calcula a norma (magnitude) de cada embedding
   - Compara se dot_product / (norm1 * norm2) >= threshold

3. **Evitando Divisão**: 
   - Como divisão é cara em circuitos, reformulamos a comparação
   - Em vez de A/B >= C, verificamos se A >= B*C
   - Elevamos ao quadrado para evitar raiz quadrada

4. **Saída**: 
   - 1 se a similaridade >= threshold
   - 0 caso contrário

5. **Zero-Knowledge**: 
   - As embeddings são sinais privados
   - Apenas o resultado da comparação é público
   - Prova que você tem embeddings similares sem revelá-las
*/