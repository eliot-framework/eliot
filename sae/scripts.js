
var estudoSocioEconomicoForm = {

	salva_e_avanca : function(){
    	var doc = document;
    	var f_estudo = doc.getElementById("f_estudo");
    	var dat_estudo = f_estudo.dataset;
    	switch (dat_estudo.passoAtual) {
    		case "ler_edital":
    			this.avanca_etapa();
    			break;
    		case ("estudo_preliminar"):
    			var frm = doc.getElementById('f_estudo_preliminar'); 
    			var obj = this.serializeForm(frm);
    			this.avanca_etapa();
    			break;
    		case ("dados_pessoais"):
    			var frm = doc.getElementById('f_dados_pessoais'); 
				var obj = this.serializeForm(frm);
				this.avanca_etapa();
				break;
    		case ("dados_familiares"):
    			var frm = doc.getElementById('f_dados_familiares'); 
				var obj = this.serializeForm(frm);
				this.avanca_etapa();
    			break;
    		default:
    			throw error("Erro ao obter o formulário atual do questionário socioeconômico");
    	}
	},
		
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
    		default:
    			throw error("Erro ao obter o formulário atual do questionário socioeconômico");
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
    		default:
    			throw error("Erro ao obter o formulário atual do questionário socioeconômico");
    	}
    },
    
    get_form_etapa_atual : function(){
    	var doc = document;
    	var f_estudo = doc.getElementById("f_estudo");
    	var dat_estudo = f_estudo.dataset;
    	switch (dat_estudo.passoAtual) {
    		case "ler_edital":	return doc.getElementById('f_ler_edital'); 
    		case ("estudo_preliminar"): return doc.getElementById('f_estudo_preliminar'); 
    		case ("dados_pessoais"): return doc.getElementById('f_dados_pessoais'); 
    		case ("dados_familiares"): return doc.getElementById('f_dados_familiares');
    		case ("bens"): return doc.getElementById('f_bens'); 
    		default: throw error("Erro ao obter o formulário atual do questionário socioeconômico");
    	}
    },
    
    serializeForm : function(form){
    	var list_fields = $.makeArray(form.getElementsByClassName("form-control"));
    	var result = [];
    	var fields_dirty = [];
    	for (var i = 0, len = list_fields.length; i < len; i++){
    		var field = list_fields[i];
    		// se o field estiver em outro form não serialize 
    		if (field.form != form){
    			continue; 
    		}
    		var dat = field.dataset;
    		var dfield = dat.field;
    		if (dfield != undefined && fpc.isFieldChanged(field) && fields_dirty.indexOf(dfield) == -1) {
    			result.push(dfield);
    			result.push("=");
    			if (dat.type === "lookup"){
	    			result.push(escape(dat.key));
	    		}else {
	    			result.push(escape(field.value));
	    		}
	    		result.push("&");
	    		fields_dirty.push(dfield);
    		}
    	}
    	if (result.length > 0){
    		result.pop();
    	}
    	return result.join("");
    }
    
};    

