/**
 *
 **/
Ext._define('adm.patrimonio.reports.AnaliticoAdquiridoWindow', {
    extend: 'adm.patrimonio.reports.BaseWindow',

    report: '/to/mpe/adm/patrimonio/Analitico_de_Bens_Adquiridos',

    _filename: 'analitico-de-bens-adquirido',

    _reportName: 'Analitico de Bens Adquirido',

    getValues: function() {
        var values = adm.patrimonio.reports.AnaliticoAdquiridoWindow.superclass.getValues.call(this);

        values.data_inicial = this.castDate(values.data_inicial);
        values.data_final = this.castDate(values.data_final);

        return values;
    },

    getGrupoField: function() {
        if(!this._groupField) {
            this._groupField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Grupo',
                name: 'grupo',
                rest: 'adm.patrimonio.parametro.GrupoEspecieRestful',
                gridColumnAction: false,
                comboListeners: {
                    scope: this,
                    changevalid: function(combo, value, oldvalue, valid) {
                        if(valid) {
                            this.getEspecieField().setValue('');
                            this.getEspecieField().setPreFilter([{property: 'grupo', value: value}]);
                        }
                        else {
                            this.getEspecieField().setPreFilter(null);
                        }
                    }
                }
            });
        }

        return this._groupField;
    },

    getEspecieField: function() {
        if(!this._especieField)
            this._especieField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Especie',
                name: 'especie',
                rest: 'adm.patrimonio.parametro.EspecieRestful',
                gridColumnAction: false
            });

        return this._especieField;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 75,
                items: [
                    this.getGrupoField(),
                    this.getEspecieField(),
                    {
                        xtype: 'rest-foldedfield',
                        restTree: 'adm.patrimonio.localizacao.Tree',
                        fieldLabel: 'Localização',
                        name: 'localizacao',
                        width: 358
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Conta',
                        name: 'conta',
                        rest: 'adm.patrimonio.parametro.ContaRestful',
                        gridColumnAction: false
                    },
                    {
                        fieldLabel: 'Nota',
                        hiddenName: 'tipo_nota',
                        xtype: 'combo',
                        width: 125,
                        store: [
                            ['nota-fiscal', 'Nota Fiscal'],
                            ['nota-doacao', 'Doação'],
                            ['nota-convenio', 'Convênio']
                        ]
                    },
                    {
                        xtype: 'panel',
                        layout: 'hbox',
                        items: [
                            {
                                xtype: 'panel',
                                layout: 'form',
                                flex: 1.0,
                                labelWidth: 75,
                                items: {
                                    xtype: 'datefield',
                                    name: 'data_inicial',
                                    fieldLabel: 'De',
                                    allowBlank: false
                                }
                            },
                            {
                                xtype: 'panel',
                                layout: 'form',
                                flex: 1.0,
                                labelWidth: 45,
                                items: {
                                    xtype: 'datefield',
                                    name: 'data_final',
                                    fieldLabel: 'Até',
                                    allowBlank: false
                                }
                            }
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: this.reportName(),
                width: 450
            }
        );

        Ext.apply(
            cfg,
            {

            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.reports.AnaliticoAdquiridoWindow.superclass.constructor.call(this, cfg);
    }
});
