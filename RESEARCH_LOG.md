## Commit 9: correção nos system prompts, na seleção dos modelos das LLMs e ajuste na lógica HITL

Após achar que estava tudo funcionando, acabei caindo em um erro um pouco misterioso. Basicamente, o analista até aprovava o pesquisador no primeiro ciclo, mas depois que o relatório chegava no revisor, o revisor sempre reprovava por falta de dados, fazia um long-cycle e depois entrava em um loop infinito do pesquisador e do analista até chegar a intervenção humana. Após analisar o que o analista estava reprovando do pesquisador, percebi que o analista estava apontando e reprovando qualquer lacuna de informação, coisas que as vezes não encontramos nas fontes mesmo e isso é normal. Percebi então que tanto o system prompt do analista quanto do revisor estavam muito rígidos, impossibilitando o pesquisador e o revisor de serem aprovados.

Não só isso, como também pensei que poderia haver uma limitação nos agentes devido ao modelo que escolhi inicialmente `gpt-4o-mini`. Como o trabalho do redator e do revisor exigem menos abstração e possuem tarefas mais simples, optei por manter o `gpt-4o-mini` para eles e colocar o `gpt-4o` para o pesquisador e o analista.

A solução que pensei para os system prompts foi:
1. Pedir para que o analista sempre gerasse uma análise crítica. Dessa forma, mesmo que o primeiro ciclo chegue no limite de execuções, o humano pode intervir e verificar se é um erro de dados leve ou ruim, permitindo o redator escrever com aquela análise crítica. Decidi não abaixar a régua para forçar o pesquisador a manter o padrão de qualidade no maior nível possível, deixando essa decisão na mão do usuário. O custo dessa decisão é que acabamos forçando o modelo a "sempre" repetir o primeiro ciclo, o que gasta mais chamadas de API.
2. Mas para o revisor final, eu realmente tive que abaixar a régua em relação aos dados. Alterei o critério da categoria `DATA_ERROR` de forma que ele só possa classificar o texto com isso quando o texto tiver uma falha muito grande de dados ou alucinação. Dessa forma, o revisor fica mais focado em avaliar a escrita do redator do que o trabalho do pesquisador e do analista.

Rodei de novo e tive mais um problema: dessa vez de TPM (Tokens Per Minute). Minha conta da OpenAI tem um limite de 30k tokens para o modelo `gpt-4o` e 200k para o `gpt-4o-mini`, por isso não tinha tido esse problema até agora.
Dei uma olhada no preço do `gpt-4o` e vi que eu não conseguiria arcar com os custos também, então optei por voltar para o `gpt-4o-mini`.

Rodei novamente e percebi que o problema aqui pode estar realmente no pesquisador depois do primeiro ciclo. Isso porque ele sempre passa de primeira no analista, e depois do long-cycle ele começa a ter problemas até dar o limite de 3 ciclos. Pesquisei sobre isso e parece que o erro pode estar relacionado ao fato de que o ciclo ReAct pode forçar o modelo a encontrar uma informação muito difícil, e depois de muitas tentativas ele pode acabar alucinando, como se fosse uma desistência de encontrar tal estatística.

Para solucionar isso, decidi por fim, abaixar a régua do analista e aceitar os dados casos eles estejam majoritariamente sólidos. Não só isso como eu também adicionei uma regra para o agente pesquisador na qual ele pode chamar no máximo 3 vezes uma ferramenta para encontrar um informação, depois disso ele deve colocar o dado como dado indisponível. Agora o analista e o revisor saberão que um dado está indisponível e não pedirão mais ele.

### Resultado final:
Para o meu tópico de teste principal, que foi "A bolha da IA", até mesmo abaixando a régua dos modelos, eu tive que aprovar o relatório manualmente pelo HITL. Isso porque o modelo não estava conseguindo alguns dados e o Revisor não estava aprovando em hipótese alguma. Mesmo assim, ao comparar o relatório final gerado após abaixar a régua com o relatório que os agentes super exigentes produziram, ele ainda produziu um bom relatório. O processo repetitivo de julgamento do relatório acabou deixando o texto com um tom defensivo e pouco executivo, como se o modelo estivesse afirmando mas sem depositar suas fichas no que está falando.
Testei para outros tópicos também e vi que o resultado realmente foi melhor depois de abaixar a régua pois o sistema agora é mais generalista. Um mesmo tópico que tinha falhado infinitamente antes, agora passou de primeira, enquanto alguns tópicos estão sofrendo um pouco pra passar pelas revisões. Isso não é ruim, na verdade é o certo, pois se estivesse tudo passando 100% das vezes, os validadores não estariam sendo úteis.
Minha conclusão final é de que essa solução foi um sucesso, mesmo que não tenha tornado o sistema em algo 100% acertivo.

## Next Steps:
Formatar o código
Criar o README.md
Gravar o vídeo utilizando o sistema