/**
 *
 **/
Ext._define('adm.patrimonio.baixa.ExtravioWindow', {
    extend: 'adm.patrimonio.baixa.Window',

    rest: 'adm.patrimonio.baixa.ExtravioRestful',

    getKindField: function(cfg) {
        if (!this._kindField) {
            this._kindField = Ext._create('core.fields.ComboField', {
                fieldLabel: 'Subtipo',
                hiddenName: 'subtype',
                allowBlank: false,
                displayField: 'label',
                valueField: 'value',
                rest: 'standard.ChoiceRestful',
                preFilter: [
                    {property: 'app_label', value: 'patrimonio', stage: 1001},
                    {property: 'name', value: 'WRITEOFF_SUBTYPES', stage: 1002},
                    {property: 'value__range', value: [11, 13], stage: 10},
                    {property: 'value', value: 1000, stage: 10}
                ]
            });

            this._kindField.on({
                scope: this,
                select: {
                    buffer: 500,
                    fn: function(combo) {
                        if(combo.getValue() === 1000)
                            combo.markInvalid('Não é permitido o subtipo "Não informado"');
                    }
                }
            });
        }

        return this._kindField;
    },

    getFormPanel: function() {
        if(!this._formPanel) {
            this._formPanel = adm.patrimonio.baixa.ExtravioWindow.superclass.getFormPanel.call(this, {});
            this._formPanel.items.insert(1, this.getKindField());
        }

        return this._formPanel;
    }
});

adm.patrimonio.baixa.Grid.register(
    'nota-baixa-extravio',
    'Nota de Extravio',
    'icon-patrimonio icon-pat-nota-baixa-extravio',
    'adm.patrimonio.baixa.ExtravioWindow'
);
