## Commit 2: montando os nodes para o walking skeleton

Decidi fazer a base de 3 códigos e subir para o github antes de completar o walking skeleton. Esses códigos são: nodes.py, prompts.py e state.py. No state.py eu apenas defini quais serão as variáveis do estado global e no prompts.py eu fiz uma função básica para chamar os System Prompts dos agentes. O código prompts.py não aparece na estrutura básica da documentação, mas decidi adicionar para não ter que colocar os prompts dentro do próprio código. Além disso, decidi escrever os prompts de verdade quando eu terminar a lógica básica do código.

OBS: A minha definição de GlobalState ainda vai ser alterada pois alguns agentes terão memória privada, então alguns campos do estado mudarão a tipagem ou sairão do estado global.

No arquivo nodes.py, implementei as 4 funções representando os 4 agentes. Nenhum deles tem memória privada de mensagens ainda e não pretendo implementar isso no walking skeleton, deixarei para implementar isso quando eu estiver iterando e chegar na parte de cada agente. O agente pesquisador, por exemplo, será um subgrafo, já que precisa de um loop ReAct interno, sendo assim, nem vou implementar as tools de busca na web antes da implementação subgrafo do pesquisador.

Durante a implementação dos nodes, tive um problema com a chamada da llm e com o retorno da função pois a documentação do LangGraph estava com algumas omissões que geraram erro no meu código. Tive que fazer uma revisão do código e reimplementar essas funções usando essa padronização de entrada e saída:

```
messages = [
        SystemMessage(content=system_prompt(agent)),
        HumanMessage(content=f"Topic: {get.state["topic"]}\n ...")
    ]

llm_answer = llm.invoke(messages)
```
