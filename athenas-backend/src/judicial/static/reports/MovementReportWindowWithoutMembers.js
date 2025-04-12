
Ext._define('judicial.reports.MovementReportWindowWithoutMembers', {
    extend: 'judicial.reports.ReportBaseWindow',

    width: 850,

    _filename: 'relatorio-de-movimentacoes',

    _report: '/to/mpe/judicial/report_by_movement_without_members',

    _reportName: 'Relatório E-ext - Movimentações Por Servidor',

    prepareValues: function(values) {
        values.instauration = 0;

        values.from = this.castDate(values.from);
        values.at = this.castDate(values.at);


        ['workplace', 'employee', 'legal_class', 'legal_matter', 'legal_movement', 'acting_zone', 'taxonomy'].forEach(
            function(attr) {
                if(values[attr])
                    values[attr] = values[attr];
                else
                    values[attr] = 0;
            }
        );

        return values;
    },

    validateFields: function() {
        var values = this.getFormPanel().getForm().getValues();

        if(this.admPermission())
            return true;

        if(values['workplace'] || values['employee'])
            return true;
        else {

            Ext.Msg.show({
                title: 'Gerar Relatório',
                msg: 'Informe o Local ou o Servidor',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });

            return false;
        }
    },

    getEmployeeField: function(cfg) {
        if(!this._employeeField)
            this._employeeField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Servidor',
                allowBlank: true,
                rest: "judicial.params.SubordinateRestful",
                name: "employee",
                displayField: 'pessoa_fisica_unicode'
            });

        return this._employeeField;
    },


    getItemsFormPanel: function(cfg) {
        return [
            this.getFromDateField(cfg),
            this.getAtDateField(cfg),
            this.getWorkplaceField(cfg),
            this.getEmployeeField(cfg),
            {
                xtype: 'choicefield',
                name: 'legal_class',
                hiddenName: 'legal_class',
                fieldLabel: 'Classe',
                width: 270,
                choiceId: 'judicial.TYPE_LAWSUIT'
            },
            {
                xtype: "rest-autocompletefield",
                fieldLabel: "Assunto",
                rest: "judicial.taxonomy.LegalMatterRestful",
                name: "legal_matter"
            },
            {
                xtype: "rest-autocompletefield",
                fieldLabel: "Área de atuação",
                rest: "judicial.params.ActingZoneRestful",
                name: "acting_zone"
            },
            {
                xtype: "rest-autocompletefield",
                fieldLabel: "Movimento",
                rest: "judicial.params.GlosaryRestful",
                name: "legal_movement",
                displayField: 'title'
            },
            {
               xtype: "rest-autocompletefield",
               fieldLabel: "Taxonomia",
               rest: "judicial.taxonomy.LegalMovimentRestful",
               name: "taxonomy",
               displayField: 'path_cache'
           }
        ];
    },
});
