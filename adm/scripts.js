
var fpcConfigForm = {

	salva : function(ts_id){
		var doc = document;
		var form =  doc.getElementById("f_form");
		var obj = fpc.getObject(form);
		var json = JSON.stringify(obj);
		fpc.getJSON("/eliot/api1/adm/config_framework/update", {"obj" : json});
	}

};    

