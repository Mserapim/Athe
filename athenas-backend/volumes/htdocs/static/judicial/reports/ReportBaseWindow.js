
Ext._define('judicial.reports.ReportBaseWindow', {
    extend: 'engine.mq.ReportWindow',

    updateFilter: function(opts) {
        if(opts.from)
            this.getAtDateField().setMinValue(
                this.getFromDateField().getValue());

        if(opts.at)
            this.getFromDateField().setMaxValue(
                this.getAtDateField().getValue());
    },

    prepareValues: function(values) {
        values.instauration = 0;

        values.from = this.castDate(values.from);
        values.at = this.castDate(values.at);

        ['workplace', 'member', 'legal_class', 'legal_matter', 'legal_movement', 'acting_zone'].forEach(
            function(attr) {
                if(values[attr])
                    values[attr] = values[attr];
                else
                    values[attr] = 0;
            }
        );

        return values;
    },

    castDate: function(value) {
        var wdt;

        try {
            wdt = Date.parseDate(value, 'd/m/Y');
        }
        catch(e) {
            wdt = new Date('1/1/1900');
        }
        finally {
            value = Ext.util.Format.date(wdt, 'Y-m-d');
        }

        return value;
    },

    getFromDateField: function(cfg) {
        if(!this._fromDateField)
            this._fromDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: 'De',
                name: 'from',
                maxValue: new Date(),
                listeners: {
                    scope: this,
                    change: function(field, value, older) {
                        this.updateFilter({from: Ext.util.Format.date(value, 'Y-m-d')})
                    }
                }
            });

        return this._fromDateField;
    },

    getAtDateField: function(cfg) {
        if(!this._atDateField)
            this._atDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: 'Até',
                name: 'at',
                maxValue: new Date(),
                listeners: {
                    scope: this,
                    change: function(field, value, older) {
                        this.updateFilter({at: Ext.util.Format.date(value, 'Y-m-d')})
                    }
                }
            });

        return this._atDateField;
    },

    getWorkplaceField: function(cfg) {
        if(!this._executionOrganField)
            this._executionOrganField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Local',
                allowBlank: true,
                rest: "judicial.params.WorkplaceRestful",
                name: "workplace"
            });

        return this._executionOrganField;
    },

    getMemberField: function(cfg) {
        if(!this._memberField)
            this._memberField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Membro',
                allowBlank: true,
                rest: "judicial.params.EmployeeRestful",
                name: "member",
                displayField: 'pessoa_fisica_unicode'
            });

        return this._memberField;
    },

    validateFields: function() {
        var values = this.getFormPanel().getForm().getValues();

        if(this.admPermission())
            return true;

        if(values['workplace'] || values['member'])
            return true;
        else {

            Ext.Msg.show({
                title: 'Gerar Relatório',
                msg: 'Informe o Local ou o Membro',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });

            return false;
        }

    },

    generateReport: function(preventClose) {
        if(!this.validateFields())
            return;

        judicial.reports.ReportBaseWindow.superclass.generateReport.call(this, preventClose);
    },

    getItemsFormPanel: function(cfg) {
        return [
            this.getFromDateField(cfg),
            this.getAtDateField(cfg),
            this.getWorkplaceField(cfg),
            this.getMemberField(cfg),
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
            }
        ];
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getItemsFormPanel(cfg)
                ]
            });

        return this._formPanel;
    },

    admPermission: function(value) {
        if(!this._admPermission)
            this._admPermission = false;

        if(value !== undefined)
            this._admPermission = value;

        return this._admPermission;
    },

    getPermissions: function() {

        Ext.Ajax.request({
            url: core.callAction('EJudOutCourtLawsuitAdmin', 'check_permission_admin'),
            scope: this,
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                this.admPermission(rst.is_admin);
            }
        });
    },


    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        judicial.reports.ReportBaseWindow.superclass.constructor.call(this, cfg);

        this.on({
            afterrender: function(me) {
                this.getPermissions();
            }
        });
    }

});
