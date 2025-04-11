Ext._define('adm.contabilidade.PPAAcaoRestful', {
    extend: 'core.Restful',

    resource: 'ContabPPAAcao',

    getFields: function(cfg) {
        if (this._fields) {
            return this._fields;
        }

        var fields = [
            { "type": "int",    "name": "id" },
            { "type": "string", "name": "unicode" },
            { "type": "string", "name": "titulo" },
            { "type": "string", "name": "cache_codigo" },
            { "type": "string", "name": "funcao" },
            { "type": "string", "name": "subfuncao" },
            { "type": "int",    "name": "programa"},
            { "type": "string", "name": "programa_unicode" },
            { "type": "string", "name": "programa_titulo" },            
            { "type": "string", "name": "codigo" },
            { "type": "int",    "name": "fonte_exclusiva" },
            { "type": "string", "name": "fonte_exclusiva_unicode" },
            { "type": "int",    "name": "revision_year" },
        ];

        this._fields = adm.contabilidade
                          .PPAAcaoRestful
                          .superclass
                          .getFields
                          .call(this, cfg)
                          .concat(fields);

        return this._fields;
    }
});
