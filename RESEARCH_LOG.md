## Commit 6: finalização do redactor

Para o redator, usei como base o que eu tinha feito no pesquisador para implementar a memória privada. A maior diferença aqui é que o redator não tem um ciclo interno e que ele recebe outros inputs.

Além disso, fiz um ajuste no prompt do redator, ressaltando principalmente os seguintes pontos:
1. Uma regra pra ele não inventar dados (evitando gastar ciclos atoa)
2. Manter um tom objetivo e profissional
3. Criar um texto COMPLETAMENTE NOVO todo ciclo

## Next Steps:
Estruturar a saída do revisor para definir se é um short ou long-cycle
Criar uma condição para o long-cycle
Escrever o prompt definitivo do revisor