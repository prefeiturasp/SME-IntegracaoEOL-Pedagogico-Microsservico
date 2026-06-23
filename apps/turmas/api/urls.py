"""Rotas da API do domínio Turmas."""

from django.urls import path

from apps.turmas.api.views import (
    AnosLetivosUEView,
    ItinerarioEnsinoMedioView,
    ListarTurmasView,
    TurmaDadosView,
    TurmasHistoricasProfessorView,
    TurmaSincronizacoesInstitucionaisView,
    TurmasProgramaView,
    TurmasRecorteFundMedioEjaView,
    TurmasRegularesView,
)

urlpatterns = [
    path(
        "turmas-regulares/",
        TurmasRegularesView.as_view(),
        name="turmas-regulares",
    ),
    path(
        "turmas-programa/",
        TurmasProgramaView.as_view(),
        name="turmas-programa",
    ),
    path(
        "listar-turmas/",
        ListarTurmasView.as_view(),
        name="listar-turmas",
    ),
    path(
        "recorte-fund-medio-eja/",
        TurmasRecorteFundMedioEjaView.as_view(),
        name="turmas-recorte-fund-medio-eja",
    ),
    path(
        "<int:codigo_turma>/dados/",
        TurmaDadosView.as_view(),
        name="turma-dados",
    ),
    path(
        "ues/<str:ue_codigo>/turmas/<int:turma_codigo>/sincronizacoes-institucionais/",
        TurmaSincronizacoesInstitucionaisView.as_view(),
        name="turma-sincronizacoes-institucionais",
    ),
    path(
        "ue/<str:ue_codigo>/sincronizacoes-institucionais/anos-letivos/",
        AnosLetivosUEView.as_view(),
        name="anos-letivos-ue",
    ),
    path(
        "anos-letivos/<int:ano_letivo>/professor/<str:professor_rf>/turmas-historicas-geral/",
        TurmasHistoricasProfessorView.as_view(),
        name="turmas-historicas-professor",
    ),
    path(
        "itinerario/ensino-medio/",
        ItinerarioEnsinoMedioView.as_view(),
        name="itinerario-ensino-medio",
    ),
]
