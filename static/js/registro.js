$(document).ready(function(){
    if($("#ID_CURSO").val() > 0) {
        $("#COD_DISCIPLINA").html("<option>Carregando...</option>");
        ajax('getDisciplinasHTMLOptions', ['ID_CURSO'], 'COD_DISCIPLINA');
    }
    $("#ID_CURSO").change(function() {
        if($(this).val() > 0){
            $("#COD_DISCIPLINA").html("<option>Carregando...</option>");
            ajax('getDisciplinasHTMLOptions', ['ID_CURSO'], 'COD_DISCIPLINA');

        }
    });
    $("#ID_CURSO").keyup(function() {
        if($(this).val() > 0) {
            $("#COD_DISCIPLINA").html("<option>Carregando...</option>");
            ajax('getDisciplinasHTMLOptions', ['ID_CURSO'], 'COD_DISCIPLINA');
        }
    });
});
