/**
 *
 **/
Ext._define('adm.patrimonio.baixa.ExtravioRestful', {
    extend: 'adm.patrimonio.baixa.Restful',

    resource: 'PATBaixaExtravio',

    getFields: function(cfg) {
        if(!this._fields) {

            this._fields = adm.patrimonio.baixa.ExtravioRestful.superclass.getFields.call(this, cfg).concat([
                {type: 'int', name: 'subtype', useNull: true}
            ]);
        }

        return this._fields;
    }
});
