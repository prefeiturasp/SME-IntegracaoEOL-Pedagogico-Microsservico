"""Testes dos servicos do dominio Turmas."""

from unittest.mock import patch

from django.test import TestCase

from apps.turmas.services import TurmasService


class TestTurmasService(TestCase):
    """Valida delegacao do service para o repository."""

    def setUp(self) -> None:
        self.repo_patcher = patch("apps.turmas.services.TurmasRepository")
        self.mock_repo_cls = self.repo_patcher.start()
        self.addCleanup(self.repo_patcher.stop)
        self.repo = self.mock_repo_cls.return_value
        self.service = TurmasService()

    def test_turmas_regulares(self) -> None:
        self.repo.turmas_regulares.return_value = [{"codigo": 1}]

        self.assertEqual(self.service.turmas_regulares([1]), [{"codigo": 1}])
        self.repo.turmas_regulares.assert_called_once_with([1])

    def test_turmas_programa(self) -> None:
        self.repo.turmas_programa.return_value = [{"codigo": 2}]

        self.assertEqual(self.service.turmas_programa([2]), [{"codigo": 2}])
        self.repo.turmas_programa.assert_called_once_with([2])

    def test_listar_turmas(self) -> None:
        self.repo.listar_turmas.return_value = [{"codigo": 3}]

        self.assertEqual(self.service.listar_turmas([3]), [{"codigo": 3}])
        self.repo.listar_turmas.assert_called_once_with([3])

    def test_turmas_atribuidas_dre_ue(self) -> None:
        self.repo.turmas_atribuidas_dre_ue.return_value = [
            {"codigo_turma": 3011229}
        ]

        self.assertEqual(
            self.service.turmas_atribuidas_dre_ue(["019362"]),
            [{"codigo_turma": 3011229}],
        )
        self.repo.turmas_atribuidas_dre_ue.assert_called_once_with(["019362"])

    def test_turmas_elegiveis(self) -> None:
        self.repo.turmas_elegiveis.return_value = [{"cod_turma": 3011229}]

        self.assertEqual(
            self.service.turmas_elegiveis("1234567", 3011228, 138),
            [{"cod_turma": 3011229}],
        )
        self.repo.turmas_elegiveis.assert_called_once_with(
            "1234567",
            3011228,
            138,
        )

    def test_turmas_recorte_fund_medio_eja(self) -> None:
        """Verifica delegação ao repository."""
        self.repo.turmas_recorte_fund_medio_eja.return_value = [{"codigo": 6}]

        self.assertEqual(
            self.service.turmas_recorte_fund_medio_eja([6]),
            [{"codigo": 6}],
        )
        self.repo.turmas_recorte_fund_medio_eja.assert_called_once_with([6])

    def test_dados_turma(self) -> None:
        self.repo.dados_turma.return_value = {"codigo": 4}

        self.assertEqual(self.service.dados_turma(4), {"codigo": 4})
        self.repo.dados_turma.assert_called_once_with(4)

    def test_sincronizacoes_institucionais(self) -> None:
        self.repo.sincronizacoes_institucionais.return_value = {"codigo": 5}

        self.assertEqual(
            self.service.sincronizacoes_institucionais("000532", 5),
            {"codigo": 5},
        )
        self.repo.sincronizacoes_institucionais.assert_called_once_with(
            "000532", 5
        )

    def test_codigos_turmas_por_ue_com_anos(self) -> None:
        self.repo.codigos_turmas_por_ue.return_value = [3036225, 3082921]

        self.assertEqual(
            self.service.codigos_turmas_por_ue("019437", [2025, 2026]),
            [3036225, 3082921],
        )
        self.repo.codigos_turmas_por_ue.assert_called_once_with(
            "019437", [2025, 2026]
        )

    def test_codigos_turmas_por_ue_sem_anos(self) -> None:
        self.repo.codigos_turmas_por_ue.return_value = [3036225]

        self.assertEqual(
            self.service.codigos_turmas_por_ue("019437", None),
            [3036225],
        )
        self.repo.codigos_turmas_por_ue.assert_called_once_with("019437", None)

    def test_turmas_historicas_professor(self) -> None:
        self.repo.turmas_historicas_professor.return_value = [{"codigo": 6}]

        self.assertEqual(
            self.service.turmas_historicas_professor(2024, "RF1"),
            [{"codigo": 6}],
        )
        self.repo.turmas_historicas_professor.assert_called_once_with(
            2024, "RF1"
        )

    def test_itinerarios_ensino_medio(self) -> None:
        self.repo.itinerarios_ensino_medio.return_value = [{"id": 7}]

        self.assertEqual(self.service.itinerarios_ensino_medio(), [{"id": 7}])
        self.repo.itinerarios_ensino_medio.assert_called_once_with()
