

var estudoSocioEconomicoForm = {

    onchange : function(field, operacao) {
    },

    
    onready : function(field, operacao) {
    },
    
    avanca_etapa : function(){

	    if (document.getElementById('f_aceite').checked){
	        document.getElementById('f_estudo_preliminar').style.display = '';
	        document.getElementById('f_ler_edital').style.display = 'none';
	    }else{
	    	document.getElementById('f_estudo_preliminar').style.display = 'none';
	    	document.getElementById('f_ler_edital').style.display = '';
	    	alert("Você deve ler o edital primeiramente!");
	    }

    }
};    

