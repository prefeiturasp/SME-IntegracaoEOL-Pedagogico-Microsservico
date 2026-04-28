"""Testes de serviços do domínio Componentes Curriculares."""
from datetime import date
from unittest.mock import patch

from django.test import SimpleTestCase

from apps.componentes_curriculares.services import ComponentesService

_REPO = "apps.componentes_curriculares.services.ComponentesRepository"


class TestComponentesService(SimpleTestCase):
    """Valida que ComponentesService delega corretamente ao repository."""

    def test_ep1_sem_turma_delega_listar_por_funcionario(self) -> None:
        """EP-1 sem codigoTurma delega a listar_por_funcionario."""
        with patch(_REPO) as mock:
            mock.return_value.listar_por_funcionario.return_value = []
            res = ComponentesService().listar_componentes_por_funcionario(
                "f1"
            )
            self.assertEqual(res, [])
            mock.return_value.listar_por_funcionario.assert_called_once_with(
                "f1"
            )

    def test_ep1_com_turma_planejamento_true(self) -> None:
        """EP-1 com codigoTurma e planejamento=True usa planejamento."""
        with patch(_REPO) as mock:
            mock.return_value.listar_planejamento_por_turma_funcionario.return_value = []  # noqa: E501
            res = ComponentesService().listar_componentes_por_funcionario(
                "f1", codigo_turma="T1", planejamento=True
            )
            self.assertEqual(res, [])
            mock.return_value.listar_planejamento_por_turma_funcionario.assert_called_once()  # noqa: E501

    def test_ep1_com_turma_planejamento_false(self) -> None:
        """EP-1 com codigoTurma e planejamento=False usa turma_funcionario."""
        with patch(_REPO) as mock:
            mock.return_value.listar_por_turma_funcionario.return_value = []
            res = ComponentesService().listar_componentes_por_funcionario(
                "f1", codigo_turma="T1", planejamento=False
            )
            self.assertEqual(res, [])
            mock.return_value.listar_por_turma_funcionario.assert_called_once()

    def test_ep2_regencia_delega(self) -> None:
        """EP-2 delega listar_regencia_por_ano_turma ao repository."""
        with patch(_REPO) as mock:
            mock.return_value.listar_regencia_por_ano_turma.return_value = []
            res = ComponentesService().listar_regencia_por_ano_turma(2024)
            self.assertEqual(res, [])
            mock.return_value.listar_regencia_por_ano_turma.assert_called_once_with(
                2024
            )

    def test_ep3_pap_delega(self) -> None:
        """EP-3 delega turma_possui_componente_pap ao repository."""
        with patch(_REPO) as mock:
            mock.return_value.turma_possui_componente_pap.return_value = True
            res = ComponentesService().turma_possui_componente_pap(
                "T1", "f1"
            )
            self.assertTrue(res)
            mock.return_value.turma_possui_componente_pap.assert_called_once()

    def test_ep4_ue_anos_escolares_delega(self) -> None:
        """EP-4 delega listar_por_ue_modalidade_ano_e_anos_escolares."""
        with patch(_REPO) as mock:
            mock.return_value.listar_por_ue_modalidade_ano_e_anos_escolares.return_value = []  # noqa: E501
            res = ComponentesService().listar_por_ue_modalidade_ano_e_anos_escolares(
                1, 2024, ["A1"]
            )
            self.assertEqual(res, [])
            mock.return_value.listar_por_ue_modalidade_ano_e_anos_escolares.assert_called_once_with(  # noqa: E501
                1, 2024, ["A1"]
            )

    def test_ep5_turma_programa_delega(self) -> None:
        """EP-5 delega listar_turma_programa_por_ue_modalidade_ano."""
        with patch(_REPO) as mock:
            mock.return_value.listar_turma_programa_por_ue_modalidade_ano.return_value = []  # noqa: E501
            res = ComponentesService().listar_turma_programa_por_ue_modalidade_ano(
                1, 2024
            )
            self.assertEqual(res, [])
            mock.return_value.listar_turma_programa_por_ue_modalidade_ano.assert_called_once_with(  # noqa: E501
                1, 2024
            )

    def test_ep6_ue_turmas_delega(self) -> None:
        """EP-6 delega listar_por_ue_e_turmas ao repository."""
        with patch(_REPO) as mock:
            mock.return_value.listar_por_ue_e_turmas.return_value = []
            res = ComponentesService().listar_por_ue_e_turmas(["T1"])
            self.assertEqual(res, [])
            mock.return_value.listar_por_ue_e_turmas.assert_called_once_with(
                ["T1"]
            )

    def test_ep7_lista_turmas_delega(self) -> None:
        """EP-7 delega listar_por_lista_turmas ao repository."""
        with patch(_REPO) as mock:
            mock.return_value.listar_por_lista_turmas.return_value = []
            res = ComponentesService().listar_por_lista_turmas(["T1"])
            self.assertEqual(res, [])
            mock.return_value.listar_por_lista_turmas.assert_called_once_with(
                ["T1"]
            )

    def test_ep8_brutos_delega(self) -> None:
        """EP-8 delega listar_turmas_brutos ao repository."""
        with patch(_REPO) as mock:
            mock.return_value.listar_turmas_brutos.return_value = []
            res = ComponentesService().listar_turmas_brutos(["T1"])
            self.assertEqual(res, [])
            mock.return_value.listar_turmas_brutos.assert_called_once_with(
                ["T1"]
            )

    def test_ep9_catalogo_delega(self) -> None:
        """EP-9 delega listar_catalogo ao repository."""
        with patch(_REPO) as mock:
            mock.return_value.listar_catalogo.return_value = []
            res = ComponentesService().listar_catalogo()
            self.assertEqual(res, [])
            mock.return_value.listar_catalogo.assert_called_once()

    def test_ep10_vigencia_delega(self) -> None:
        """EP-10 delega listar_vigencia_componentes ao repository."""
        with patch(_REPO) as mock:
            mock.return_value.listar_vigencia_componentes.return_value = []
            res = ComponentesService().listar_vigencia_componentes(
                "U1", 2024, ["1"], None
            )
            self.assertEqual(res, [])
            mock.return_value.listar_vigencia_componentes.assert_called_once()

    def test_ep11_grade_curricular_delega(self) -> None:
        """EP-11 delega listar_grade_curricular ao repository."""
        with patch(_REPO) as mock:
            mock.return_value.listar_grade_curricular.return_value = []
            res = ComponentesService().listar_grade_curricular(2024)
            self.assertEqual(res, [])
            mock.return_value.listar_grade_curricular.assert_called_once_with(
                2024
            )

    def test_ep12_sem_atribuicao_delega(self) -> None:
        """EP-12 delega listar_componentes_sem_atribuicao ao repository."""
        with patch(_REPO) as mock:
            mock.return_value.listar_componentes_sem_atribuicao.return_value = []  # noqa: E501
            res = ComponentesService().listar_componentes_sem_atribuicao(
                "T1"
            )
            self.assertEqual(res, [])
            mock.return_value.listar_componentes_sem_atribuicao.assert_called_once()  # noqa: E501

    def test_ep13_correlacionados_delega(self) -> None:
        """EP-13 delega listar_agrupamentos_correlacionados ao repository."""
        with patch(_REPO) as mock:
            mock.return_value.listar_agrupamentos_correlacionados.return_value = []  # noqa: E501
            res = ComponentesService().listar_agrupamentos_correlacionados(
                130, date(2024, 1, 1)
            )
            self.assertEqual(res, [])
            mock.return_value.listar_agrupamentos_correlacionados.assert_called_once_with(  # noqa: E501
                130, date(2024, 1, 1)
            )

    def test_ep14_correlacionados_lote_delega(self) -> None:
        """EP-14 delega listar_agrupamentos_correlacionados_lote."""
        with patch(_REPO) as mock:
            mock.return_value.listar_agrupamentos_correlacionados_lote.return_value = []  # noqa: E501
            res = ComponentesService().listar_agrupamentos_correlacionados_lote(
                [140], None
            )
            self.assertEqual(res, [])
            mock.return_value.listar_agrupamentos_correlacionados_lote.assert_called_once_with(  # noqa: E501
                [140], None
            )

    def test_ep15_territorio_delega(self) -> None:
        """EP-15 delega listar_agrupamentos_territorio ao repository."""
        with patch(_REPO) as mock:
            mock.return_value.listar_agrupamentos_territorio.return_value = []
            res = ComponentesService().listar_agrupamentos_territorio([15])
            self.assertEqual(res, [])
            mock.return_value.listar_agrupamentos_territorio.assert_called_once_with(  # noqa: E501
                [15]
            )
