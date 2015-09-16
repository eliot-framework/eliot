
var produtoForm = {

    onchange : function(field, operacao) {
        var op = operacao;
        if (op === "novo"){
        		op = "inclusão";
        }
    	alert('O Campo "' + field.dataset.field + '" com id ' + field.id + ' foi alterado em uma '+ op + '.');
    },

    
    onready : function(field, operacao) {
        var op = operacao;
        if (op === "novo"){
        		op = "inclusão";
        }
    	alert('O elemento "' + field.id + '" foi carregado. Operacao:  ' + op + '.');
    },
    
};    
