/**
 *
 **/
Ext._define('rh.pessoa.juridica.Restful', {
    extend: 'core.Restful',

    resource: 'RHPessoaJuridicaRestful',

    getFields: function() {
        if(!this._fields)
            this._fields = rh.pessoa.juridica.Restful.superclass.getFields.call(this).concat([
               {name: 'nome', type: 'string'},
               {name: 'cnpj', type: 'string'},
               {name: 'identificador', type: 'string'},
            ]);

        return this._fields;
    }
});

core.RestfulGrid.register(
    'rh.pessoa.juridica.Restful',
    'rh.pessoa.juridica.Grid'
);