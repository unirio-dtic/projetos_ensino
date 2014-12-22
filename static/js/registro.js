$(document).ready(function(){
    if($("#ID_CURSO").val() > 0) {
        $("#ID_DISCIPLINA").html("<option>Carregando...</option>");
        ajax('getDisciplinasHTMLOptions', ['ID_CURSO'], 'ID_DISCIPLINA');
    }
    $("#ID_CURSO").change(function() {
        if($(this).val() > 0){
            $("#ID_DISCIPLINA").html("<option>Carregando...</option>");
            ajax('getDisciplinasHTMLOptions', ['ID_CURSO'], 'ID_DISCIPLINA');

        }
    });
    $("#ID_CURSO").keyup(function() {
        if($(this).val() > 0) {
            $("#ID_DISCIPLINA").html("<option>Carregando...</option>");
            ajax('getDisciplinasHTMLOptions', ['ID_CURSO'], 'ID_DISCIPLINA');
        }
    });
});
