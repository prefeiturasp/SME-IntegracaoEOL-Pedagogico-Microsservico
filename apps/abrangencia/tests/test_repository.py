"""Testes do repositório de abrangência."""

from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from apps.abrangencia.models import CicloEnsino
from apps.abrangencia.repository import AbrangenciaRepository


class AbrangenciaRepositoryTest(TestCase):
    """Valida as consultas de abrangência."""

    def test_lista_ciclos_ordenados_em_uma_query(self) -> None:
        """Retorna os ciclos ordenados sem consultas adicionais."""
        data = timezone.make_aware(datetime(2026, 8, 20, 10, 30))
        CicloEnsino.objects.create(
            codigo_modalidade_ensino=5,
            codigo_etapa_ensino=4,
            codigo=3,
            descricao="Alfabetização",
            data_atualizacao=data,
        )
        CicloEnsino.objects.create(
            codigo_modalidade_ensino=1,
            codigo_etapa_ensino=1,
            codigo=1,
            descricao="Educação Infantil",
            data_atualizacao=data,
        )

        with self.assertNumQueries(1):
            ciclos = list(AbrangenciaRepository().listar_ciclos_ensino())

        self.assertEqual([ciclo.codigo for ciclo in ciclos], [1, 3])
