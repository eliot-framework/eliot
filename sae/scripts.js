

var estudoSocioEconomicoForm = {

    avanca_etapa : function(){
    	var doc = document;
    	var f_estudo = doc.getElementById("f_estudo");
    	var dat_estudo = f_estudo.dataset;

    	switch (dat_estudo.passoAtual) {
    		case "ler_edital":
    		    if (doc.getElementById('f_aceite').checked){
    		        doc.getElementById('f_estudo_preliminar').style.display = '';
    		        doc.getElementById('f_ler_edital').style.display = 'none';
    		        doc.getElementById("f_estudo").dataset.passoAtual = "estudo_preliminar";
    		    }else{
    		    	alert("Você deve ler o edital primeiro!");
    		    }
    		    break;
    		case ("estudo_preliminar"):
    			doc.getElementById('f_dados_pessoais').style.display = '';
    			doc.getElementById('f_estudo_preliminar').style.display = 'none';
    			doc.getElementById("f_estudo").dataset.passoAtual = "dados_pessoais";
    			break;
    		case ("dados_pessoais"):
    			doc.getElementById('f_dados_familiares').style.display = '';
    			doc.getElementById('f_dados_pessoais').style.display = 'none';
    			doc.getElementById("f_estudo").dataset.passoAtual = "dados_familiares";
    			break;
    		case ("dados_familiares"):
    			doc.getElementById('f_bens').style.display = '';
    			doc.getElementById('f_dados_familiares').style.display = 'none';
    			doc.getElementById("f_estudo").dataset.passoAtual = "bens";
    			break;
    	}
    },
    
    volta_etapa : function(){
    	var doc = document;
    	var f_estudo = doc.getElementById("f_estudo");
    	var dat_estudo = f_estudo.dataset;

    	switch (dat_estudo.passoAtual) {
    		case "ler_edital":
    			 window.history.back();
    		    break;
    		case ("estudo_preliminar"):
    			doc.getElementById('f_ler_edital').style.display = '';
    			doc.getElementById('f_estudo_preliminar').style.display = 'none';
    			doc.getElementById("f_estudo").dataset.passoAtual = "ler_edital";
    			break;
    		case ("dados_pessoais"):
    			doc.getElementById('f_estudo_preliminar').style.display = '';
    			doc.getElementById('f_dados_pessoais').style.display = 'none';
    			doc.getElementById("f_estudo").dataset.passoAtual = "estudo_preliminar";
    			break;
    		case ("dados_familiares"):
    			doc.getElementById('f_dados_pessoais').style.display = '';
    			doc.getElementById('f_dados_familiares').style.display = 'none';
    			doc.getElementById("f_estudo").dataset.passoAtual = "dados_pessoais";
    			break;
    		case ("bens"):
    			doc.getElementById('f_dados_familiares').style.display = '';
    			doc.getElementById('f_bens').style.display = 'none';
    			doc.getElementById("f_estudo").dataset.passoAtual = "dados_familiares";
    			break;

    	}
    }
    
};    

