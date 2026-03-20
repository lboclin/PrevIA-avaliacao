## Commit 5: finalização do analyst

O analista já estava praticamente pronto na última etapa, fiz apenas alguns ajustes e tomei umas decisões sobre o que esse agente precisa receber como input.

O que eu fiz foi o seguinte:
1. Decidi que o analista não terá memória privada. Diferente do pesquisador e do redator, o analista precisa ter o mínimo de ruído possível, ele deve receber um texto bruto, julgar e extrair. Quanto mais informações que ele receber, como análises passadas, dados brutos anteriores, etc, maior a chance dele alucinar e não ter um julgamento e análise com precisão.
2. Pode parecer meio contraditório com o que acabei de falar, mas eu decidi adicionar pelo menos a revisão do revisor (no caso de um long-cycle) como input para o analista, pois é importante que ele saiba se faltou passar algo para o redator e o revisor acabou cobrando.
3. Adicionei uma nova condição na qual o analista não escreverá a análise crítica quando o trabalho do revisor não for aprovado, ele escreverá apenas a revisão. Isso é bom para economizar nos tokens de output.

## Next Steps:
Adicionar memória privada para o redator
Definir o prompt definitivo e finalizar o node do redator