 Ext._define('rh.gratifications_manager.aux_coordenation.gratificacao.Restful', {
    extend: 'core.Restful',

    resource: 'GMGratAuxCoordenacao',

    getFields: function() {
        if(!this._fields){
            this._fields = rh.gratifications_manager.aux_coordenation.gratificacao.Restful.superclass.getFields.call(this, {}).concat([
                {type: 'string', name: 'periodo' },
                {type: "string", name: "titular"},
                {type: "string", name: "substituto"},
                {type: "int", name: "ano"},
                {type: "int", name: "mes"},
                {type: "int", name: "qtd_dias_consolidado_titular", useNull: true},
                {type: "int", name: "qtd_dias_deferido_titular", useNull: true},
                {type: "int", name: "qtd_dias_consolidado_substituto", useNull: true},
                {type: "int", name: "qtd_dias_deferido_substituto", useNull: true},
            ]);
        }
        return this._fields;
    }
});