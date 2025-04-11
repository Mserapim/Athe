 Ext._define('rh.defin.workplace.Restful', {
    extend: 'core.Restful',

    resource: 'DEFINWorkplaceRestful',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.defin.workplace.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int",  name: "created_by",  useNull: true},
                {type: "bool",  name: "ativo"},
                {type: "bool",  name: "habilita_protocolo"},
                {type: "string",  name: "sigla"},
                {type: "string",  name: "code_cnmp"},
            ]);

        return this._fields;
    }
});
