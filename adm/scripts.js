
var fpcConfigForm = {

	on_open_form : function(response){
		var doc = document;
		var param = response.params[0]; 
		var update_fields = param.update_fields;
		var f_form = doc.getElementById("f_form");
		fpc.updateFields(f_form, update_fields);
		fpc.resetFields(f_form);
	},
		
	salva : function(ts_id){
		fpc.mensagem("");
		var doc = document;
		var form =  doc.getElementById("f_form");
		var obj = fpc.getObject(form);
		if (obj != undefined){
			fpc.getJSON("/eliot/api1/adm/config_framework/update", {"obj" : JSON.stringify(obj)});
			fpc.mensagem("Atenção: As novas configurações somente entraram em vigor após reiniciar o servidor!", "info");
		}else{
			fpc.mensagem("Nenhuma alteração realizada nas configurações para salvar.", "info");
		}
	}

};    

