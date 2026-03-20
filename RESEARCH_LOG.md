## Commit 8: implementação dos contadores de ciclos e do HITL

As alterações feitas nessa etapa foram:
1. Adicionei os contadores de ciclos dentro dos próprios nós `analyst` e `reviewer`.
2. Criação de um novo nó `human_intervention`. Decidi mapear nesse nó qual o ciclo que chegou no limite de execuções, dessa forma, o usuário tem um contexto melhor do problema para tomar uma decisão. Esse mapeamento também altera o espaço de ações do usuário. Essa função foi implementada 100% pelo Gemini e conferida por mim posteriormente, já que tinham muitos prints, e eu não queria perder tempo escrever muito print e pouca lógica.
3. Adicionei a aresta condicional e coloquei as funções condicionais do analista e do revisor para apontarem para o nó `human_intervention` quando o limite de ciclos fosse antigido.
4. Adicionei uma função no prórpio arquivo `agent.py` para salvar o relatório como um arquivo md na pasta `intelligence_reports`. Sei que não é uma boa prática colocar funções auxiliares no código principal mas fiz isso para não ter que criar um novo código e adicionar apenas uma função nele, atrapalhando a minha arquitetura de pastas.
5. Alterei o código da função `main` para que o usuário possa injetar o tópico como input.


## Next Steps:
Rodar alguns tópicos para validar o sistema
Analisar a possibilidade de colocar um calculador de custo no sistema
Corrigir bugs e fazer as últimas alterações para entregar o sistema