/**
 *
 **/
Ext._define('adm.patrimonio.movimento.ItemRestful', {
    extend: 'core.Restful',

    resource: 'PATMovimentoItem',

    getFields: function() {
        if(!this._fields)
            this._fields = adm.patrimonio.movimento.ItemRestful.superclass.getFields.call(this).concat([
                {name: 'icons', type: 'auto'},
                {name: 'patrimonio_plaqueta', type: 'string'},
                {name: 'patrimonio_unicode', type: 'string'},
                {name: 'patrimonio_conservacao', type: 'string'},
                {name: 'patrimonio_descricao', type: 'string'},
                {name: 'patrimonio', type: 'int'}
            ]);

        return this._fields;
    }
});
