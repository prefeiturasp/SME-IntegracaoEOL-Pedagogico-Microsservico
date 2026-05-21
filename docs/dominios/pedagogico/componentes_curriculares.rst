Componentes curriculares
========================

Objetivo
--------

O dominio de componentes curriculares atende consultas usadas pelo Transition
Gateway para substituir endpoints do legado pedagogico. A implementacao do MS
de dominio le dados materializados pelo ETL e aplica pequenas regras de
compatibilidade para preservar o contrato do legado.

As principais classes envolvidas sao:

* ``apps.componentes_curriculares.repository.ComponentesRepository``;
* ``apps.componentes_curriculares.services.ComponentesService``;
* ``apps.componentes_curriculares.api.views``;
* tabelas materializadas em ``apps.componentes_curriculares.models``.

Endpoints atendidos
-------------------

O MS expõe os endpoints internos usados pelo gateway, entre eles:

* ``GET /api/v1/componentes-curriculares/``
* ``GET /api/v1/componentes-curriculares/grade-curricular/{ano_letivo}/``
* ``GET /api/v1/componentes-curriculares/anos/{ano_turma}/regencia/``
* ``GET /api/v1/componentes-curriculares/funcionarios/{login}/``
* ``GET /api/v1/componentes-curriculares/turmas/{codigo_turma}/pap/``
* ``GET /api/v1/componentes-curriculares/ues/{ue_id}/modalidades/{modalidade}/anos/{ano_letivo}/turmas-programa/``
* ``GET /api/v1/componentes-curriculares/ues/{ue_id}/modalidades/{modalidade}/anos/{ano_letivo}/``
* ``GET /api/v1/componentes-curriculares/ues/{ue_id}/turmas/``
* ``GET /api/v1/componentes-curriculares/turmas/``
* ``GET /api/v1/componentes-curriculares/turmas/brutos/``
* ``GET /api/v1/componentes-curriculares/turmas/vigencia/``

O Transition Gateway publica rotas legadas equivalentes e repassa as chamadas
para este MS.

Fontes materializadas
---------------------

O MS nao consulta diretamente o EOL. Ele depende das tabelas carregadas pelo
ETL pedagogico, principalmente:

* ``componente_curricular``;
* ``componente_turma``;
* ``atribuicao_componente``;
* ``grade_componente_curricular``;
* ``componente_curricular_hierarquia``;
* ``componente_curricular_pap``;
* ``componente_curricular_planejamento_regencia``;
* ``componente_curricular_agrupamento``;
* ``agrupamento_atribuicao_territorio_saber``;
* ``turma``.

A tabela ``atribuicao_componente`` representa a relacao entre professor,
turma e componente curricular. Ela deve carregar vinculos SME, externos,
regulares, de programa e os casos historicos/disponibilizados necessarios aos
endpoints. A decisao sobre quais registros existem nessa tabela pertence ao
ETL; o MS apenas aplica filtros de consulta compativeis com o legado.

Regras de compatibilidade
-------------------------

Componente pai e deduplicacao
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alguns componentes possuem hierarquia no EOL. O legado normaliza componentes
filhos para o componente pai e depois remove duplicidades por:

``codigo_componente_curricular_pai`` quando houver pai valido, caso contrario
``codigo``.

No MS, essa regra aparece nos endpoints que retornam componentes completos,
especialmente ``ComponentesRepository.listar_por_funcionario`` e consultas de
grade/turma programa. O objetivo e manter o mesmo contrato do legado, onde o
cliente recebe o componente agrupador em vez de varias linhas filhas.

Ponto de atencao: quando o mesmo professor possui o mesmo componente em varias
turmas, a deduplicacao preserva uma unica turma. O legado usa ``DistinctBy`` e
mantem o primeiro item retornado pela query. Como o MS usa dados
materializados, a ordem precisa ser definida explicitamente quando o valor de
``turma_codigo`` fizer parte da comparacao de homologacao.

Regencia e planejamento de regencia
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Componentes com ``regencia = true`` podem ser expandidos para componentes de
planejamento de regencia. A expansao usa a tabela
``componente_curricular_planejamento_regencia``.

A regra de busca e:

* para anos maiores que zero, buscar configuracoes com ``ano = ano_turma``;
* para ano zero ou nulo, usar configuracoes genericas com ``ano IS NULL``;
* quando a consulta vem de turma, considerar tambem ``turno`` quando houver
  configuracao especifica;
* se nao houver regra especifica por ano/turno, usar a regra generica.

O componente ``512`` recebe tratamento especial para compatibilizar a resposta
com o legado:

* codigo pai igual ao proprio ``512``;
* descricao ``Regencia de classe infantil``;
* ``regencia = true``.

Essa regra existe para preservar a forma esperada pelos consumidores do
legado, mesmo quando o dado materializado vem com descricao ou hierarquia
diferente.

Componentes por funcionario
~~~~~~~~~~~~~~~~~~~~~~~~~~~

O endpoint sem turma retorna os componentes do professor no ano corrente. O
filtro vigente usado pelo MS e:

* ``professor = login``;
* ``ano_letivo = ano atual``;
* ``dt_cancelamento IS NULL``;
* ``dt_disponibilizacao IS NULL``.

Depois da consulta, o MS:

* normaliza componente pai;
* aplica regra de regencia infantil;
* remove duplicidades por componente pai/codigo;
* retorna ``professor = null``, como o legado.

Esse endpoint nao deve ser interpretado como uma listagem de todas as turmas do
professor. Ele entrega uma lista de componentes atribuídos ao funcionario, e
``turma_codigo`` e apenas um campo preservado do primeiro vinculo escolhido
pela regra de deduplicacao.

Validacao PAP
~~~~~~~~~~~~~

O endpoint de validacao PAP responde se a turma possui componente PAP para o
funcionario informado.

A regra aplicada e:

* buscar atribuicoes da turma e professor;
* ignorar atribuicoes canceladas;
* considerar atribuicoes sem disponibilizacao;
* considerar atribuicoes disponibilizadas a partir de ``05/02`` do ano letivo;
* considerar motivo de disponibilizacao de fim de ano letivo;
* validar se o componente esta em ``componente_curricular_pap``.

No MS, a consulta deve usar ``SELECT EXISTS`` para evitar materializar todos os
componentes da atribuicao apenas para responder verdadeiro/falso.

Turmas programa
~~~~~~~~~~~~~~~

O endpoint de turmas programa lista componentes de turmas com
``codigo_tipo_programa IS NOT NULL`` e exclui turmas de evento para atribuicao.

O legado obtem os componentes a partir das estruturas de grade regular e grade
de programa, depois aplica normalizacao de componente pai e ``DistinctBy``. No
MS, a tabela ``componente_turma`` ja deve ter recebido do ETL os componentes
necessarios para turmas regulares e de programa.

Para compatibilidade de resposta, o MS ordena o resultado por ``codigo``. O
legado nao possui ``ORDER BY`` explicito nesse endpoint, mas o resultado
observado costuma sair crescente por codigo do componente. Como o PostgreSQL
nao garante ordem sem ordenacao explicita, a ordenacao no MS torna o contrato
estavel.

Modalidade educacao infantil
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Para modalidade de educacao infantil, o endpoint de turmas programa aplica o
mesmo recorte de series usado pelo legado. As series atualmente consideradas
sao:

``23, 24, 25, 26, 116, 117, 118, 119, 225, 297``.

Vigencia de atribuicao
~~~~~~~~~~~~~~~~~~~~~~

Ha dois filtros principais de vigencia:

* por turma: aceita atribuicoes sem cancelamento e com disponibilizacao nula,
  disponibilizacao a partir de ``05/02`` do ano letivo ou motivo de fim de ano;
* vigente por funcionario: exige cancelamento nulo e disponibilizacao nula.

Esses filtros nao sao intercambiaveis. Endpoints por turma precisam enxergar
casos disponibilizados que o endpoint de funcionario sem turma nao deve
retornar.

Decisoes de ordenacao
---------------------

O legado nem sempre possui ``ORDER BY`` nas queries. Porem, varios endpoints
sao comparados byte a byte pelo script de validacao. Onde a ordem observada do
legado faz parte do contrato pratico, o MS deve ordenar explicitamente.

Decisoes atuais:

* componentes por anos escolares: ordenar por ``codigo``;
* componentes de turmas programa: ordenar por ``codigo``;
* componentes por funcionario: preservar a primeira ocorrencia apos a consulta
  e a normalizacao de componente pai.

Quando uma nova divergencia aparecer apenas por ordem, confirmar primeiro se o
conjunto de codigos e igual. Se for igual, preferir ordenar no MS a alterar o
ETL.

Responsabilidades: ETL x MS
---------------------------

O ETL deve:

* materializar os dados necessarios para todos os endpoints;
* manter as chaves de upsert coerentes com o conceito consultado;
* trazer regular, programa, SME, externo e historico quando esses dados forem
  necessarios ao contrato;
* evitar multiplicar linhas que nao representam vinculos diferentes para os
  endpoints.

O MS deve:

* aplicar filtros de vigencia;
* normalizar componentes pais;
* aplicar regras pontuais de compatibilidade com o legado;
* deduplicar de acordo com o endpoint;
* retornar o formato esperado pelo gateway.

Regra pratica: se a decisao define quais dados existem na tabela, ela pertence
ao ETL. Se a decisao define como esses dados sao filtrados, agrupados ou
serializados para um endpoint, ela pertence ao MS.

Consultas de apoio
------------------

Para investigar divergencia de componentes por funcionario, verificar no banco
materializado:

.. code-block:: sql

   SELECT
       professor,
       turma_codigo,
       componente_codigo,
       ano_letivo,
       dt_cancelamento,
       dt_disponibilizacao,
       cd_motivo_disponibilizacao
   FROM atribuicao_componente
   WHERE professor = '<RF>'
     AND ano_letivo = <ANO>
     AND componente_codigo = <COMPONENTE>
   ORDER BY turma_codigo, componente_codigo;

Para verificar se uma divergencia de turma programa e apenas ordenacao:

.. code-block:: sql

   SELECT DISTINCT
       ct.componente_codigo,
       cc.descricao
   FROM componente_turma ct
   JOIN componente_curricular cc
     ON cc.codigo = ct.componente_codigo
   JOIN turma t
     ON t.codigo::text = ct.turma_codigo
   WHERE t.ue_codigo = '<UE>'
     AND t.ano_letivo = <ANO>
     AND t.codigo_tipo_programa IS NOT NULL
   ORDER BY ct.componente_codigo;

Manutencao da documentacao
--------------------------

Use esta pagina para regras de negocio e decisoes de compatibilidade. Use
docstrings para o contrato tecnico de classes e metodos. Use comentarios inline
apenas para explicar uma linha ou bloco cuja intencao nao seja obvia no codigo.
