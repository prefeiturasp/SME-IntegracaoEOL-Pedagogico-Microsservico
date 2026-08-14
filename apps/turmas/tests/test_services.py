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

    def test_turmas_recorte_por_tipo(self) -> None:
        """Delega ao repository com códigos e filtros informados."""
        self.repo.turmas_recorte_por_tipo.return_value = [2112345]

        self.assertEqual(
            self.service.turmas_recorte_por_tipo([2112345], [1], "000532", 1),
            [2112345],
        )
        self.repo.turmas_recorte_por_tipo.assert_called_once_with(
            [2112345], [1], "000532", 1
        )

    def test_codigos_turmas_por_ano_modalidade_dre(self) -> None:
        """Delega ao repository com UEs e filtros informados."""
        self.repo.codigos_turmas_por_ano_modalidade_dre.return_value = [
            3011258
        ]

        self.assertEqual(
            self.service.codigos_turmas_por_ano_modalidade_dre(
                ["019370"], "1", 5, 2026
            ),
            [3011258],
        )
        (
            self.repo.codigos_turmas_por_ano_modalidade_dre
        ).assert_called_once_with(["019370"], "1", 5, 2026)

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

    def test_modalidades_ensino(self) -> None:
        self.repo.modalidades_ensino.return_value = ["Infantil"]

        self.assertEqual(self.service.modalidades_ensino(), ["Infantil"])
        self.repo.modalidades_ensino.assert_called_once_with()

    def test_turmas_por_tipo_sala_converte_tipo_numerico(self) -> None:
        self.repo.turmas_por_tipo_sala.return_value = [{"codigo_turma": 1}]

        resultado = self.service.turmas_por_tipo_sala("000532", "3", "2024")

        self.assertEqual(resultado, [{"codigo_turma": 1}])
        self.repo.turmas_por_tipo_sala.assert_called_once_with(
            "000532", 3, 2024
        )

    def test_turmas_por_tipo_sala_nao_numerico_zera_filtro(self) -> None:
        self.repo.turmas_por_tipo_sala.return_value = []

        self.service.turmas_por_tipo_sala("000532", "abc", "2024")

        self.repo.turmas_por_tipo_sala.assert_called_once_with(
            "000532", 0, 2024
        )

    def test_turmas_por_tipo_sala_ano_letivo_nao_numerico_retorna_vazio(
        self,
    ) -> None:
        resultado = self.service.turmas_por_tipo_sala(
            "000532", "3", "asdfaf"
        )

        self.assertEqual(resultado, [])
        self.repo.turmas_por_tipo_sala.assert_not_called()

    def test_turmas_por_escola(self) -> None:
        self.repo.turmas_por_escola.return_value = [{"codigo_turma": 1}]

        resultado = self.service.turmas_por_escola("000532", "2024")

        self.assertEqual(resultado, [{"codigo_turma": 1}])
        self.repo.turmas_por_escola.assert_called_once_with("000532", 2024)

    def test_turmas_por_escola_ano_letivo_nao_numerico_retorna_vazio(
        self,
    ) -> None:
        resultado = self.service.turmas_por_escola("000532", "asdasd")

        self.assertEqual(resultado, [])
        self.repo.turmas_por_escola.assert_not_called()

    def test_turmas_sondagem(self) -> None:
        self.repo.turmas_sondagem.return_value = [{"codigo_turma": 1}]

        resultado = self.service.turmas_sondagem("000532", "2024")

        self.assertEqual(resultado, [{"codigo_turma": 1}])
        self.repo.turmas_sondagem.assert_called_once_with("000532", 2024)

    def test_turmas_sondagem_ano_letivo_nao_numerico_retorna_vazio(
        self,
    ) -> None:
        resultado = self.service.turmas_sondagem("000532", "wewe")

        self.assertEqual(resultado, [])
        self.repo.turmas_sondagem.assert_not_called()
