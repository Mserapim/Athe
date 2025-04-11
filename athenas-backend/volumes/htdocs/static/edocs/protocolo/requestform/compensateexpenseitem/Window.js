Ext._define('edocs.protocolo.requestform.compensateexpenseitem.Window', {
    extend: 'core.RestfulWindow',

    rest: 'edocs.protocolo.requestform.compensateexpenseitem.Restful',

    width: 900,
    
    getNotaField: function(cfg) {
        if (!this._notaField) {
            this._notaField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Número da nota fiscal',
                name: 'nota',
                anchor: '90%',
                allowBlank: true
            });
        }

        return this._notaField;
    },

    getCompanyField: function(cfg) {
        if (!this._companyField) {
            this._companyField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Nome da empresa ou do prestador do serviço',
                name: 'company',
                anchor: '90%',
                allowBlank: true
            });
        }

        return this._companyField;
    },

    getVencNotaDateField: function(cfg) {
        if (!this._vencNotaDateField) {
            this._vencNotaDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: "Vencimento da nota fiscal",
                name: "venc_date_nf",
                width: 200,
                allowBlank: true
            });
        }

        return this._vencNotaDateField;
    }, 

    getNotaMaterialField: function (cfg) {
        if (!this._notaMaterialField) {
            this._notaMaterialField = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Nota de material',
                name: 'nota_material',
                value: 'off',
                allowBlank: true,
            });
        }

        return this._notaMaterialField;
    },

    getNotaServiceField: function (cfg) {
        if (!this._notaServiceField) {
            this._notaServiceField = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Nota de serviço',
                name: 'nota_service',
                value: 'off',
                allowBlank: true,
            });
        }

        return this._notaServiceField;
    },

    getValueField: function (cfg) {
        if (!this._valueField) {
            this._valueField = Ext._create('Ext.form.NumberField', {
                fieldLabel: "Valor",
                name: "value",
                width: 250,
                allowBlank: true,
                decimalPrecision: 2,
                allowDecimals: true,
                maxLength: 10
            });
        }

        return this._valueField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'fieldset',
                        title: 'Informações',
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.0,
                                items: this.getNotaField(cfg)
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.0,
                                items: this.getCompanyField(cfg)
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                flex: 1.0,
                                items: this.getVencNotaDateField(cfg)
                            },
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        title: 'Tipo da nota',
                        layout: 'form',
                        labelWidth: 1,
                        items: [
                            this.getNotaMaterialField(cfg),
                            this.getNotaServiceField(cfg),
                        ]
                    },
                    {
                        xtype: 'fieldset',
                        layout: 'form',
                        labelWidth: 60,
                        items: this.getValueField(cfg)
                    },
                ]
            });
    
        return this._formPanel;
    }
});