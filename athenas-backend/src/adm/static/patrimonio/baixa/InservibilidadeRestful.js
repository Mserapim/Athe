/**
 *
 **/
Ext._define('adm.patrimonio.baixa.InservibilidadeRestful', {
    extend: 'adm.patrimonio.baixa.Restful',

    resource: 'PATBaixaInservibilidade',

    getFields: function(cfg) {
        if(!this._fields) {

            this._fields = adm.patrimonio.baixa.InservibilidadeRestful.superclass.getFields.call(this, cfg).concat([
                {type: 'int', name: 'subtype', useNull: true}
            ]);
        }

        return this._fields;
    }
});
