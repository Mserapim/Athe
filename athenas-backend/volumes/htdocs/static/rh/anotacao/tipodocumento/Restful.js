Ext._define('rh.anotacao.tipodocumento.Restful', {
    extend: 'core.Restful',

    resource: 'RHTipoDocumentoAnotacao',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.anotacao.tipodocumento.Restful.superclass.getFields.call(this, cfg).concat([
                {type: 'string', name: 'tipo'},
                {type: 'int', name: 'modified_by', useNull: true},
                {type: 'string', name: 'modified_by_unicode'},
                {type: 'date', name: 'created_at', dateFormat: 'd/m/Y H:i'},
                {type: 'date', name: 'modified_at', dateFormat: 'd/m/Y H:i'},
                {type: 'int', name: 'created_by', useNull: true},
                {type: 'string', name: 'created_by_unicode'}
            ]);

        return this._fields;
    }
});
