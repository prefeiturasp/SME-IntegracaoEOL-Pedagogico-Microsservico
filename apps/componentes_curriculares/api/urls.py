"""URLs do domínio Componentes Curriculares."""
from django.urls import path

from apps.componentes_curriculares.api.views import (
    AgrupamentosCorrelacionadosLoteView,
    AgrupamentosCorrelacionadosView,
    AgrupamentosTerritorioLoteView,
    ComponentesCatalogoView,
    ComponentesPorFuncionarioView,
    ComponentesPorListaTurmasView,
    ComponentesPorUeAnosEscolaresView,
    ComponentesPorUeTurmasView,
    ComponentesRegenciaView,
    ComponentesSemAtribuicaoView,
    ComponentesTurmaProgramaView,
    ComponentesTurmasBrutosView,
    GradeCurricularView,
    ValidarPapView,
    VigenciaComponentesView,
)

urlpatterns = [
    # Rotas estáticas de /turmas antes das dinâmicas
    path(
        "turmas/brutos/",
        ComponentesTurmasBrutosView.as_view(),
        name="turmas-brutos",
    ),
    path(
        "turmas/vigencia/",
        VigenciaComponentesView.as_view(),
        name="vigencia",
    ),
    path(
        "turmas/",
        ComponentesPorListaTurmasView.as_view(),
        name="lista-turmas",
    ),
    # Rotas dinâmicas de /turmas
    path(
        "turmas/<str:codigo_turma>/pap/",
        ValidarPapView.as_view(),
        name="pap",
    ),
    path(
        "turmas/<str:codigo_turma>/sem-atribuicao/",
        ComponentesSemAtribuicaoView.as_view(),
        name="sem-atribuicao",
    ),
    # EP-2
    path(
        "anos/<int:ano_turma>/regencia/",
        ComponentesRegenciaView.as_view(),
        name="regencia",
    ),
    # EP-1
    path(
        "funcionarios/<str:login>/",
        ComponentesPorFuncionarioView.as_view(),
        name="componentes-funcionario",
    ),
    # EP-5 antes do EP-4 (mais específico primeiro)
    path(
        "ues/<str:ue_id>/modalidades/<int:modalidade>/anos/<int:ano_letivo>"
        "/turmas-programa/",
        ComponentesTurmaProgramaView.as_view(),
        name="turma-programa",
    ),
    # EP-4
    path(
        "ues/<str:ue_id>/modalidades/<int:modalidade>/anos/<int:ano_letivo>/",
        ComponentesPorUeAnosEscolaresView.as_view(),
        name="ue-anos-escolares",
    ),
    # EP-6
    path(
        "ues/<str:ue_id>/turmas/",
        ComponentesPorUeTurmasView.as_view(),
        name="ue-turmas",
    ),
    # EP-11
    path(
        "grade-curricular/<int:ano_letivo>/",
        GradeCurricularView.as_view(),
        name="grade-curricular",
    ),
    # EP-13
    path(
        "<int:codigo_componente>/territorio-saber"
        "/agrupamentos-correlacionados/",
        AgrupamentosCorrelacionadosView.as_view(),
        name="agrupamentos-correlacionados",
    ),

    # EP-14
    path(
        "territorio-saber/agrupamentos-correlacionados/",
        AgrupamentosCorrelacionadosLoteView.as_view(),
        name="agrupamentos-lote",
    ),
    # EP-15
    path(
        "territorio-saber/agrupamentos/",
        AgrupamentosTerritorioLoteView.as_view(),
        name="agrupamentos-territorio",
    ),
    # EP-9 (raiz — deve ser o último)
    path("", ComponentesCatalogoView.as_view(), name="catalogo"),
]
