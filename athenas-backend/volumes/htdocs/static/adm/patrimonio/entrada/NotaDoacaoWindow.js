/**
 *
 **/
Ext._define('adm.patrimonio.entrada.NotaDoacaoWindow', {
    extend: 'adm.patrimonio.entrada.Window',

    rest: 'adm.patrimonio.entrada.NotaDoacaoRestful',

    tabHeight: 290,

    getProviderField: function() {
        if (!this._providerField) {
            this._providerField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Doador',
                name: "fornecedor",
                rest: 'rh.person.Restful',
                preFilter: [{property: 'kind__in', value: ['pessoafisica', 'pessoajuridica'], stage: 1000}]
            });
        }

        return this._providerField;
    },
});

adm.patrimonio.entrada.Grid.register(
    'nota-doacao',
    'Nota de Doação',
    'icon-patrimonio icon-pat-nota-doacao',
    'adm.patrimonio.entrada.NotaDoacaoWindow'
);
