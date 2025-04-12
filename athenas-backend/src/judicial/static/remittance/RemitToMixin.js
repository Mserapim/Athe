Ext._define('judicial.remittance.RemitToMixin', {
    getRemitToField: function() {
        if (!this._remitToField) {
            this._remitToField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: "Remeter para",
                allowBlank: true,
                rest: "rh.workplace.Restful",
                name: "department",
                emptyText: 'Caso não seja selecionado nenhuma Lotação será remetido a Central de Triagem',
                preFilter: [
                    {property: 'allow_lawsuit', value: true, stage: 1002}
                ]
            });
        }

        return this._remitToField;
    }
});
