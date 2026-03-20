## Commit 4: implementação das tools e loop ReAct para o researcher

Nessa etapa, tive que tomar uma decisão baseada no meu tempo restante de finalização do projeto. A documentação fornece uma estrutura base para a implementação de um subgrafo, que seria a base para o loop ReAct do researcher. Entretanto, se eu fosse pegar essa base e fosse implementar de forma funcional o loop ReAct com as tools na mão, passando por todas as condições e estrutura de chamadas das tools da LLM eu perderia muito tempo em algo que já foi resolvido na indústria. É claro que isso coloca o loop do agente pesquisador em uma caixa preta no código, mas devido a minha restrição de tempo para entrega do projeto, optei por usar uma função do framework própria pra isso `create_react_agent`.

Sobre a busca na web do researcher, eu optei por separar em 2 tools com funções parecidas mas diferentes:
1. A primeira tool coleta urls (sobre um subtópico definido pela LLM) e com breves descrições de cada uma.
2. A segunda tool entra nos sites, faz o scraping, limpa o lixo (anúncios, menus) e devolve o texto útil direto para a LLM.

A ideia de separar essas 2 tools é deixar a LLM com uma tomada de decisão extra: quais fontes são úteis ou não? Se colocássemos ela apenas para fazer o scrapping de várias fontes, estaríamos gastando mais chamadas de API e ainda estaríamos coletando muito lixo e informações redundantes. Com a separação das tools, a LLM consegue definir se uma fonte será útil para ela e se vale à pena fazer o scrapping. Não só isso, mas também podemos aumentar muito o tamanho da busca, já que podemos olhar dezenas de urls e descrições sem precisar coletar aquele tanto de dado inútil.

O melhor de tudo isso é que eu encontrei uma API de busca perfeita que já contém essas 2 funcionalidades. O nome é Tavily e foi a API de busca que eu escolhi para o meu sistema.

Sobre a questão da memória privada, decidi criar uma nova lista no GlobalState. Essa lista funcionará como a memória privada do researcher, mas eliminando todo o "lixo" gerado pelo ciclo ReAct, já que nela, eu adiciono apenas o texto gerado e as revisões de cada ciclo.

Para os próximos, ainda irei definir individualmente quais agentes terão memória privada. Os que eu achar que não é necessário, eu não adicionarei.

## Problemas enfrentados:

1. Atualização da biblioteca: a função create_react_agent atualizou e acabou mudando de lugar e de parâmetros, o que não estava atualizado nos códigos da documentação. Com a ajuda do Gemini consegui encontrar os novos parâmetros e novo local da função na biblioteca.

2. Coesão dos prompts: mesmo depois te tudo pronto, o analista estava recusando os dados do pesquisador e entrando em um ciclo infinito. Percebi que isso estava sendo causado porque o system prompt do pesquisador não fornecia as especificações de como o analista queria os dados. Então o que eu fiz foi alterar os prompts dos agentes para que eles se conectassem melhor.

3. Falta do long-cycle: depois de arrumar o problema 2, caímos em outro problema, o revisor nunca aprova o relatório de inteligência do redator. Isso está acontecendo por 2 motivos: o revisor é muito exigente em relação aos dados e o redator não consegue buscar mais dados. A única forma do redator obter mais dados é a partir do long-cycle, que ainda não está implementado. Decidi deixar isso de lado e não resolver esse problema até chegar na parte do redator e do revisor.

## Next Steps:
Determinar se o analista precisa ou não de memória privada
Adicionar a revisão do revisor como input para o analista
Finalizar o analista
