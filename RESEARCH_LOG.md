## Commit 7: implementação do long-cycle e finalização do revisor

Essa foi uma das etapas mais importantes, pois defini o final do processo. 

Um dos problemas que eu tive foi decidir como o revisor vai modificar o estado de forma que o orquestrador saiba se deve fazer um short ou long cycle.
Minha ideial inicial era criar uma tabela binária de tipos de erros formando um bitmasking da seguinte forma:
1. [erro do redator]
2. [erro do redator]
4. [erro do redator]
8. [erro de dados]
16. [erro de dados]
...

O revisor veria quais tipos de erro o texto tem e iria somando apenas uma vez cada tipo e no final retornando essa soma.
Se a soma fosse 0, o texto estava aprovado e não haviam erros.
Se a soma fosse < 16, o erro havia sido apenas do redator, definindo um short-cycle
Se a soma fosse >= 16, o erro havia sido do pesquisador ou do analista, definindo um long-cycle

Isso seria perfeito, entretanto, ao apresentar essa ideia para o Gemini, ele me lembrou de um ponto muito importante: LLMs são ruins com somas. A LLM poderia errar e somar um mesmo valor 2 vezes, o que seria caótico. Então preferi apenas definir 3 categorias e dar a descrição do que se encaixa cada uma delas. Elas são:
1. APPROVED: The report is perfect, fully supported by data, and follows all formatting rules.
2. WRITING_ERROR: The data is present and sufficient, but there are formatting, logical, or structural errors. The Redactor needs to rewrite it.
3. DATA_ERROR: The report makes claims but lacks specific data, quotes, sources, or numbers to support them. The Researcher needs to find more data.

Esses são os textos exatos que a LLM recebe para classificar o texto.

Eu lembrei de também de adicionar o tópico como input para o revisor, algo que eu notei que estava faltando na função do node e é algo vital para a função do revisor.

Sobre a implementação do long-cycle, eu tive que alterar só a função condicional `route_reviewer()` e a aresta dessa condição no `agent.py`.

## Next Steps:
Adicionar os contadores de ciclos
Adicionar os condicionais para ativar intervenção humana
Criar uma forma de interação humana via terminal
Finalizar o HITL