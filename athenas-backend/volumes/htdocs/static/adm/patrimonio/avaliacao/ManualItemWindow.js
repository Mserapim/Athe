/*
 *
 */

Ext._define('adm.patrimonio.avaliacao.ManualItemWindow', {
    extend: 'adm.patrimonio.avaliacao.ItemWindow',

    actionTitles: {
        create: 'Novo - Depreciação Manual',
        update: 'Editar - Depreciação Manual',
        remove: 'Remover - Depreciação Manual',
        read: 'Carregar - Depreciação Manual',
    },

    getPatrimonioField: function(cfg) {
        if(!this._patrimonioField)
            this._patrimonioField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Patrimonio',
                name: 'patrimonio',
                rest: 'adm.patrimonio.PatrimonioRestful'
            });

        return this._patrimonioField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = adm.patrimonio.avaliacao.ManualItemWindow.superclass.getFormPanel.call(this, cfg);

            this._formPanel.remove(this._formPanel.get(0));
            this._formPanel.remove(this._formPanel.get(0));

            this._formPanel.insert(0, this.getPatrimonioField());
        }

        return this._formPanel;
    }
});
