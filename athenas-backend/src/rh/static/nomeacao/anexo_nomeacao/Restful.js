Ext._define("rh.nomeacao.anexo_nomeacao.Restful", {
    extend: 'core.Restful',

    resource: 'RHNomeacaoAnexoRestful',

    getFields: function() {
        if(!this._fields){
            this._fields = rh.nomeacao.anexo_nomeacao.Restful.superclass.getFields.call(this, {}).concat([
                {type: "int", name: "tipo_documento"},
                {type: "string", name: "tipo_documento_display"},
                {type: "string", name: "tipo_documento_descr"},
                {type: "string", name: "provimento_unicode"},
                {type: "string", name: "arquivo_nome"},
                {type: "string", name: "link_download"},
            ]);
        }
        return this._fields;
    }
});