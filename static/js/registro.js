$(document).ready(function(){
    if($("#ID_CURSO").val() > 0) {
        getIdUnidade($(this).val());
        getDisciplinasHTMLOptions($(this).val());
    }
    $("#ID_CURSO").on("change keyup", function(){
        if($(this).val() > 0) {
            getIdUnidade($(this).val());
            getDisciplinasHTMLOptions($(this).val());
        } else {
            $("#COD_DISCIPLINA").html("<option>Selecione o curso</option>");
        }

    });
});

function getDisciplinasHTMLOptions(idCurso){
    $("#COD_DISCIPLINA").html("<option>Carregando...</option>");
    $.ajax({
        type: 'POST',
        url: 'getDisciplinasHTMLOptions',
        data: { ID_CURSO: idCurso },
        success: function(retorno) {
            $("#COD_DISCIPLINA").html(retorno);
        }
    });
}

function getIdUnidade(idCurso) {
    $.ajax({
        type: 'POST',
        url: 'getIdUnidade',
        data: { ID_CURSO: idCurso },
        success: function(retorno) {
            $("#ID_UNIDADE").val(retorno);
        }
    });
}