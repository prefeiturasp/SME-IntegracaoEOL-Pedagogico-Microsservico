"""Testes dos servicos do dominio Turmas."""

from datetime import UTC, datetime
from unittest.mock import patch

from django.test import TestCase

from apps.componentes_curriculares.constants import MODALIDADE_EJA
from apps.turmas.services import TurmasService


def _dados_turma(**kwargs) -> dict:
    dados = {
        "codigo": 9000001,
        "tipo_turma": 1,
        "data_inicio": datetime(2026, 2, 2, tzinfo=UTC),
        "data_fim": datetime(2026, 12, 18, tzinfo=UTC),
        "extinta": True,
        "ensino_especial": True,
        "serie_ensino": "EJA II - Ciclo",
    }
    dados.update(kwargs)
    return dados


def _linha(**kwargs) -> dict:
    linha = {
        "codigo_dre": "100000",
        "dre": "DRE A",
        "dre_abreviacao": "A",
        "codigo_escola": "000001",
        "ue": "EMEF A",
        "codigo_tipo_escola": 1,
        "codigo_turma": 9000001,
        "ano": "5",
        "ano_letivo": 2026,
        "modalidade": "Fundamental",
        "codigo_modalidade": 5,
        "nome_turma": "5A",
        "semestre": 0,
        "duracao_turno": 6,
        "tipo_turno": 1,
        "turma": _dados_turma(),
    }
    linha.update(kwargs)
    return linha


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
            {"codigo_turma": 9000001}
        ]

        self.assertEqual(
            self.service.turmas_atribuidas_dre_ue(["000001"]),
            [{"codigo_turma": 9000001}],
        )
        self.repo.turmas_atribuidas_dre_ue.assert_called_once_with(["000001"])

    def test_estrutura_abrangencia_filtra_pela_dre(self) -> None:
        self.repo.linhas_abrangencia_estrutura_vigente.return_value = iter(
            [_linha()]
        )

        resultado = self.service.estrutura_abrangencia("100000")

        self.assertEqual(resultado["dres"][0]["codigo"], "100000")
        self.repo.linhas_abrangencia_estrutura_vigente.assert_called_once_with(
            codigo_dre="100000"
        )

    def test_estrutura_abrangencia_sem_linhas_retorna_estrutura_vazia(
        self,
    ) -> None:
        self.repo.linhas_abrangencia_estrutura_vigente.return_value = iter([])

        self.assertEqual(
            self.service.estrutura_abrangencia(),
            {"dres": []},
        )
        self.repo.linhas_abrangencia_estrutura_vigente.assert_called_once_with(
            codigo_dre=None
        )

    def test_estrutura_abrangencia_agrupa_por_dre_e_ue(self) -> None:
        self.repo.linhas_abrangencia_estrutura_vigente.return_value = iter(
            [
                _linha(codigo_turma=1),
                _linha(codigo_turma=2),
                _linha(codigo_turma=3, codigo_escola="000002", ue="EMEF B"),
                _linha(
                    codigo_turma=4,
                    codigo_dre="200000",
                    dre="DRE B",
                    dre_abreviacao="B",
                    codigo_escola="000003",
                ),
            ]
        )

        dres = self.service.estrutura_abrangencia()["dres"]

        self.assertEqual(
            [
                (
                    dre["codigo"],
                    [
                        (ue["codigo"], [t["codigo"] for t in ue["turmas"]])
                        for ue in dre["ues"]
                    ],
                )
                for dre in dres
            ],
            [
                ("100000", [("000001", [1, 2]), ("000002", [3])]),
                ("200000", [("000003", [4])]),
            ],
        )
        self.assertEqual(
            {k: v for k, v in dres[1].items() if k != "ues"},
            {"codigo": "200000", "nome": "DRE B", "abreviacao": "B"},
        )
        self.assertEqual(
            {k: v for k, v in dres[0]["ues"][1].items() if k != "turmas"},
            {"codigo": "000002", "nome": "EMEF B", "codigo_tipo_escola": 1},
        )

    def test_estrutura_abrangencia_mantem_ordem_de_primeira_aparicao(
        self,
    ) -> None:
        """UEs seguem a primeira turma recebida; turmas, a ordem recebida."""
        self.repo.linhas_abrangencia_estrutura_vigente.return_value = iter(
            [
                _linha(codigo_turma=1, codigo_escola="000009"),
                _linha(codigo_turma=2, codigo_escola="000001"),
                _linha(codigo_turma=3, codigo_escola="000009"),
            ]
        )

        ues = self.service.estrutura_abrangencia()["dres"][0]["ues"]

        self.assertEqual(
            [
                (ue["codigo"], [t["codigo"] for t in ue["turmas"]])
                for ue in ues
            ],
            [("000009", [1, 3]), ("000001", [2])],
        )

    def test_estrutura_abrangencia_monta_turma_com_dados_da_turma(
        self,
    ) -> None:
        self.repo.linhas_abrangencia_estrutura_vigente.return_value = iter(
            [_linha(turma=_dados_turma())]
        )

        turma = self._primeira_turma()

        self.assertEqual(
            turma,
            {
                "ano": "5",
                "ano_letivo": 2026,
                "codigo": 9000001,
                "tipo_turma": 1,
                "modalidade": "Fundamental",
                "codigo_modalidade": 5,
                "nome_turma": "5A",
                "semestre": 0,
                "duracao_turno": 6,
                "tipo_turno": 1,
                "data_fim": datetime(2026, 12, 18, tzinfo=UTC),
                "eh_historico": False,
                "ensino_especial": True,
                "etapa_eja": 0,
                "serie_ensino": None,
                "data_inicio_turma": datetime(2026, 2, 2, tzinfo=UTC),
                "extinta": True,
                "situacao": None,
                "ue_codigo": None,
            },
        )

    def test_estrutura_abrangencia_sem_turma_usa_valores_padrao(
        self,
    ) -> None:
        self.repo.linhas_abrangencia_estrutura_vigente.return_value = iter(
            [_linha(turma=None, codigo_modalidade=None)]
        )

        turma = self._primeira_turma()

        self.assertEqual(turma["tipo_turma"], 0)
        self.assertIsNone(turma["data_fim"])
        self.assertIsNone(turma["data_inicio_turma"])
        self.assertFalse(turma["extinta"])
        self.assertFalse(turma["ensino_especial"])
        self.assertEqual(turma["etapa_eja"], 0)
        self.assertEqual(turma["codigo_modalidade"], 0)

    def test_estrutura_abrangencia_etapa_eja_pela_modalidade_da_linha(
        self,
    ) -> None:
        """Ciclo EJA só se aplica à modalidade EJA da linha de abrangência."""
        self.repo.linhas_abrangencia_estrutura_vigente.return_value = iter(
            [
                _linha(codigo_turma=1, codigo_modalidade=MODALIDADE_EJA),
                _linha(codigo_turma=2, codigo_modalidade=6),
            ]
        )

        turmas = self.service.estrutura_abrangencia()["dres"][0]["ues"][0][
            "turmas"
        ]

        self.assertEqual([t["etapa_eja"] for t in turmas], [2, 0])

    def test_estrutura_abrangencia_por_turmas_consulta_os_codigos(
        self,
    ) -> None:
        self.repo.linhas_abrangencia_estrutura_vigente.return_value = iter(
            [_linha()]
        )

        resultado = self.service.estrutura_abrangencia_por_turmas([9000001])

        self.assertEqual(resultado["dres"][0]["codigo"], "100000")
        self.repo.linhas_abrangencia_estrutura_vigente.assert_called_once_with(
            codigos_turma=[9000001]
        )

    def test_estrutura_abrangencia_por_turmas_lista_vazia_nao_consulta(
        self,
    ) -> None:
        self.assertEqual(
            self.service.estrutura_abrangencia_por_turmas([]),
            {"dres": []},
        )
        self.repo.linhas_abrangencia_estrutura_vigente.assert_not_called()

    def _primeira_turma(self) -> dict:
        estrutura = self.service.estrutura_abrangencia()
        return estrutura["dres"][0]["ues"][0]["turmas"][0]

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
        resultado = self.service.turmas_por_tipo_sala("000532", "3", "asdfaf")

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
