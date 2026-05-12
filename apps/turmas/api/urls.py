"""Rotas da API do domínio Turmas."""

from django.urls import path

from apps.turmas.api.views import (
    AnosLetivosUEView,
    ItinerarioEnsinoMedioView,
    ListarTurmasView,
    TurmaDadosView,
    TurmasHistoricasProfessorView,
    TurmasProgramaView,
    TurmasRegularesView,
    TurmaSincronizacoesInstitucionaisView,
)

urlpatterns = [
    # Endpoints POST — recebem lista de códigos no body
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
    # GET por código de turma
    path(
        "<int:codigo_turma>/dados/",
        TurmaDadosView.as_view(),
        name="turma-dados",
    ),
    # Sincronizações institucionais por UE + turma
    path(
        "ues/<str:ue_codigo>/turmas/<int:turma_codigo>/sincronizacoes-institucionais/",
        TurmaSincronizacoesInstitucionaisView.as_view(),
        name="turma-sincronizacoes-institucionais",
    ),
    # Anos letivos por UE
    path(
        "ue/<str:ue_codigo>/sincronizacoes-institucionais/anosLetivos/",
        AnosLetivosUEView.as_view(),
        name="anos-letivos-ue",
    ),
    # Turmas históricas do professor
    path(
        "anos-letivos/<int:ano_letivo>/professor/<str:professor_rf>/turmas-historicas-geral/",
        TurmasHistoricasProfessorView.as_view(),
        name="turmas-historicas-professor",
    ),
    # Itinerários do Ensino Médio (fixture local)
    path(
        "itinerario/ensino-medio/",
        ItinerarioEnsinoMedioView.as_view(),
        name="itinerario-ensino-medio",
    ),
]
