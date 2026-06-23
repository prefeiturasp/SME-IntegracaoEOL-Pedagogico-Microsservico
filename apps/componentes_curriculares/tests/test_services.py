"""Testes de serviços do domínio Componentes Curriculares."""

from datetime import date
from unittest.mock import patch

from django.test import SimpleTestCase

from apps.componentes_curriculares.services import ComponentesService

_REPO = "apps.componentes_curriculares.services.componentes.ComponentesRepository"


class TestComponentesService(SimpleTestCase):
    """Valida delegação do service de componentes curriculares."""

    def setUp(self) -> None:
        """Configura o repository usado pelos testes."""
        patcher = patch(_REPO)
        self.addCleanup(patcher.stop)
        self.mock_repo_cls = patcher.start()
        self.repo = self.mock_repo_cls.return_value
        self.service = ComponentesService()

    def assert_delega(
        self, metodo_service, metodo_repo, *args, retorno=None, **kwargs
    ):
        """Valida delegação do service para o repository.

        Args:
            metodo_service: Nome do método no service a ser chamado.
            metodo_repo: Nome do método esperado no repository.
            retorno: Valor retornado pelo repository; padrão é lista vazia.
        """
        retorno = [] if retorno is None else retorno
        getattr(self.repo, metodo_repo).return_value = retorno

        resultado = getattr(self.service, metodo_service)(*args, **kwargs)

        self.assertEqual(resultado, retorno)
        getattr(self.repo, metodo_repo).assert_called_once_with(
            *args, **kwargs
        )

    def test_ep1_sem_turma_delega_listar_por_funcionario(self) -> None:
        """Delega listagem sem turma para o repository."""
        self.repo.listar_por_funcionario.return_value = []

        resultado = self.service.listar_componentes_por_funcionario("f1")

        self.assertEqual(resultado, [])
        self.repo.listar_por_funcionario.assert_called_once_with("f1")

    def test_ep1_com_turma_planejamento_true(self) -> None:
        """Delega listagem com planejamento para o repository."""
        self.repo.listar_planejamento_por_turma_funcionario.return_value = []

        resultado = self.service.listar_componentes_por_funcionario(
            "f1",
            codigo_turma="T1",
            planejamento=True,
        )

        self.assertEqual(resultado, [])
        self.repo.listar_planejamento_por_turma_funcionario.assert_called_once_with(
            "T1",
            "f1",
        )

    def test_ep1_com_turma_planejamento_false(self) -> None:
        """Delega listagem por turma para o repository."""
        self.repo.listar_por_turma_funcionario.return_value = []

        resultado = self.service.listar_componentes_por_funcionario(
            "f1",
            codigo_turma="T1",
        )

        self.assertEqual(resultado, [])
        self.repo.listar_por_turma_funcionario.assert_called_once_with(
            "T1",
            "f1",
            incluir_territorios_outros_professores=False,
        )

    def test_ep1_agrupamento_false_nao_altera_retorno(self) -> None:
        """Mantém exibição do componente quando agrupamento está inativo."""
        dados = [{"codigo": 1, "exibir_componente_eol": True}]
        self.repo.listar_por_funcionario.return_value = dados

        resultado = self.service.listar_componentes_por_funcionario(
            "f1",
            agrupamento=False,
        )

        self.assertEqual(resultado, dados)
        self.assertTrue(resultado[0]["exibir_componente_eol"])

    def test_ep1_agrupamento_true_oculta_componente_eol(self) -> None:
        """Oculta componente EOL quando agrupamento está ativo."""
        self.repo.listar_por_funcionario.return_value = [
            {"codigo": 1, "exibir_componente_eol": True},
            {"codigo": 2, "exibir_componente_eol": True},
        ]

        resultado = self.service.listar_componentes_por_funcionario(
            "f1",
            agrupamento=True,
        )

        self.assertEqual(
            resultado,
            [
                {"codigo": 1, "exibir_componente_eol": False},
                {"codigo": 2, "exibir_componente_eol": False},
            ],
        )

    def test_ep1_agrupamento_true_com_turma_inclui_territorios_outros_rfs(
        self,
    ) -> None:
        """Solicita territórios de outros RFs quando agrupa por turma."""
        self.repo.listar_por_turma_funcionario.return_value = [
            {"codigo": 813071, "exibir_componente_eol": True},
            {"codigo": 1216, "exibir_componente_eol": True},
        ]

        resultado = self.service.listar_componentes_por_funcionario(
            "f1",
            codigo_turma="T1",
            agrupamento=True,
        )

        self.repo.listar_por_turma_funcionario.assert_called_once_with(
            "T1",
            "f1",
            incluir_territorios_outros_professores=True,
        )
        self.assertEqual(
            resultado,
            [
                {"codigo": 813071, "exibir_componente_eol": False},
                {"codigo": 1216, "exibir_componente_eol": False},
            ],
        )

    def test_ep2_regencia_delega(self) -> None:
        """Delega listagem de regência para o repository."""
        self.assert_delega(
            "listar_regencia_por_ano_turma",
            "listar_regencia_por_ano_turma",
            2024,
        )

    def test_ep3_pap_delega(self) -> None:
        """Delega verificação de componente PAP para o repository."""
        self.assert_delega(
            "turma_possui_componente_pap",
            "turma_possui_componente_pap",
            "T1",
            "f1",
            retorno=True,
        )

    def test_ep4_ue_anos_escolares_delega(self) -> None:
        """Delega listagem por UE, modalidade, ano e séries."""
        self.assert_delega(
            "listar_por_ue_modalidade_ano_e_anos_escolares",
            "listar_por_ue_modalidade_ano_e_anos_escolares",
            "U1",
            1,
            2024,
            ["1"],
        )

    def test_ep5_turma_programa_delega(self) -> None:
        """Delega listagem de turmas programa."""
        self.assert_delega(
            "listar_turma_programa_por_ue_modalidade_ano",
            "listar_turma_programa_por_ue_modalidade_ano",
            "U1",
            1,
            2024,
        )

    def test_ep6_ue_turmas_delega(self) -> None:
        """Delega listagem por UE e turmas."""
        self.assert_delega(
            "listar_por_ue_e_turmas",
            "listar_por_ue_e_turmas",
            "U1",
            ["T1"],
        )

    def test_ep7_lista_turmas_delega(self) -> None:
        """Delega listagem por turmas com parâmetro padrão."""
        self.repo.listar_por_lista_turmas.return_value = []

        resultado = self.service.listar_por_lista_turmas(["T1"])

        self.assertEqual(resultado, [])
        self.repo.listar_por_lista_turmas.assert_called_once_with(
            ["T1"],
            adicionar_componentes_planejamento=True,
        )

    def test_ep7_lista_turmas_sem_planejamento_delega(self) -> None:
        """Delega listagem por turmas sem componentes de planejamento."""
        self.repo.listar_por_lista_turmas.return_value = []

        resultado = self.service.listar_por_lista_turmas(
            ["T1"],
            adicionar_componentes_planejamento=False,
        )

        self.assertEqual(resultado, [])
        self.repo.listar_por_lista_turmas.assert_called_once_with(
            ["T1"],
            adicionar_componentes_planejamento=False,
        )

    def test_ep8_brutos_delega(self) -> None:
        """Delega listagem de componentes sem pós-processamento."""
        self.assert_delega(
            "listar_turmas_brutos",
            "listar_turmas_brutos",
            ["T1"],
        )

    def test_ep9_catalogo_delega(self) -> None:
        """Delega listagem do catálogo ao repository."""
        self.assert_delega("listar_catalogo", "listar_catalogo")

    def test_ep10_vigencia_delega(self) -> None:
        """Delega listagem de vigência ao repository."""
        self.assert_delega(
            "listar_vigencia_componentes",
            "listar_vigencia_componentes",
            "U1",
            2024,
            ["1"],
            None,
        )

    def test_ep11_grade_curricular_delega(self) -> None:
        """Delega listagem de grade curricular ao repository."""
        self.assert_delega(
            "listar_grade_curricular",
            "listar_grade_curricular",
            2024,
        )

    def test_ep12_sem_atribuicao_delega(self) -> None:
        """Delega listagem de componentes sem atribuição."""
        data_base = date(2024, 6, 1)
        self.assert_delega(
            "listar_componentes_sem_atribuicao",
            "listar_componentes_sem_atribuicao",
            "T1",
            data_base,
        )

    def test_ep13_correlacionados_delega(self) -> None:
        """Delega listagem de agrupamentos correlacionados."""
        data_base = date(2024, 1, 1)

        self.assert_delega(
            "listar_agrupamentos_correlacionados",
            "listar_agrupamentos_correlacionados",
            130,
            data_base,
        )

    def test_ep14_correlacionados_lote_delega(self) -> None:
        """Delega listagem de agrupamentos correlacionados em lote."""
        self.assert_delega(
            "listar_agrupamentos_correlacionados_lote",
            "listar_agrupamentos_correlacionados_lote",
            [140],
            None,
        )

    def test_ep15_territorio_delega(self) -> None:
        """Delega listagem de agrupamentos de território."""
        self.assert_delega(
            "listar_agrupamentos_territorio",
            "listar_agrupamentos_territorio",
            [15],
        )
