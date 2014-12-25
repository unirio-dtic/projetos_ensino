$(document).ready(function(){
    if($("#ID_CURSO").val() > 0) {
        getDisciplinasHTMLOptions()
    }
    $("#ID_CURSO").on("change keyup", function(){
       getDisciplinasHTMLOptions();
    });
});

function getDisciplinasHTMLOptions(){
    $("#COD_DISCIPLINA").html("<option>Carregando...</option>");
    ajax('getDisciplinasHTMLOptions', ['ID_CURSO'], 'COD_DISCIPLINA');
}
