/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.ItemWindow', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.avaliacao.ItemRestful',

    width: 700,

    actionTitles: {
        create: 'Novo - Depreciação de Rotina',
        update: 'Editar - Depreciação de Rotina',
        remove: 'Remover - Depreciação de Rotina',
        read: 'Carregar - Depreciação de Rotina',
    },

    getValorAvaliadoField: function(cfg) {
        if(!this._valorAvaliadoField)
            this._valorAvaliadoField = Ext._create('Ext.form.NumberField', {
                fieldLabel: 'Valor liquido',
                name: 'valor_avaliado',
                readOnly: false,
                style: 'text-align:right'
            });

        return this._valorAvaliadoField;
    },

    getConservacaoField: function(cfg) {
        if(!this._conservacaoField)
            this._conservacaoField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Conservação',
                name: 'conservacao_display',
                readOnly: true
            });

        return this._conservacaoField;
    },

    getValorAtualField: function(cfg) {
        if(!this._valorAtualField)
            this._valorAtualField = Ext._create('Ext.form.NumberField', {
                xtype: 'numberfield',
                fieldLabel: 'Valor no momento',
                name: 'valor_atual',
                readOnly: true,
                style: 'text-align:right'
            });

        return this._valorAtualField;
    },

    getDepreciacaoField: function(cfg) {
        if(!this._depreciacaoField)
            this._depreciacaoField = Ext._create('Ext.form.NumberField', {
                fieldLabel: 'Depreciado',
                name: 'depreciacao',
                readOnly: true,
                style: 'text-align:right'
            });

        return this._depreciacaoField;
    },

    getResidualField: function(cfg) {
        if(!this._residualField)
            this._residualField = Ext._create('Ext.form.NumberField', {
                fieldLabel: 'Residual',
                name: 'residual',
                readOnly: true,
                style: 'text-align:right'
            });

        return this._residualField;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 120,
                items: [
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Patrimonio',
                        name: 'plaqueta',
                    },
                    {
                        xtype: 'displayfield',
                        fieldLabel: 'Especie',
                        name: 'especie_unicode',
                    },
                    {
                        xtype: 'container',
                        layout: 'hbox',
                        defaults: {
                            flex: 1
                        },
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                items: [
                                    this.getValorAvaliadoField(),
                                ]
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                items: [
                                    this.getDepreciacaoField()
                                ]
                            }
                        ]
                    },
                    {
                        xtype: 'container',
                        layout: 'hbox',
                        defaults: {
                            flex: 1
                        },
                        items: [
                            {
                                xtype: 'container',
                                layout: 'form',
                                items: [
                                    this.getValorAtualField()
                                ]
                            },
                            {
                                xtype: 'container',
                                layout: 'form',
                                items: [
                                    this.getResidualField()
                                ]
                            },
                        ]
                    },
                    this.getConservacaoField(),
                    {
                        xtype: 'panel',
                        title: 'Dispensado',
                        layout: 'form',
                        frame: true,
                        items: [
                            {
                                xtype: 'displayfield',
                                fieldLabel: 'Por',
                                name: 'discarded_by_unicode',
                            },
                            {
                                xtype: 'displaydatetimefield',
                                fieldLabel: 'Na data',
                                name: 'discarded_at',
                            },
                            {
                                xtype: 'container',
                                items: [
                                    {
                                        xtype: 'ckeditor',
                                        fieldLabel: '',
                                        hidelabel: true,
                                        name: 'discarded_justify',
                                    }
                                ]
                            }
                        ]
                    }
                ]
            });

        return this._formPanel;
    }
});
