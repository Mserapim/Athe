/**
 *
 **/
Ext._define('adm.patrimonio.reports.SinteticoBaixadoWindow', {
    extend: 'adm.patrimonio.reports.BaseWindow',

    report: '/to/mpe/adm/patrimonio/Sintetico_de_Bens_Baixado',

    _filename: 'sintetico-de-bens-baixado',

    _reportName: 'Sintético de Bens Baixado',

    getValues: function() {
        var values = adm.patrimonio.reports.SinteticoBaixadoWindow.superclass.getValues.call(this);

        values.data_inicial = this.castDate(values.data_inicial);
        values.data_final = this.castDate(values.data_final);

        return values;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 45,
                items: [
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
                        width: 270,
                        store: [
                            ['nota-baixa-alienacao', 'Alienação'],
                            ['nota-baixa-doacao', 'Doação'],
                            ['nota-baixa', 'Generica'],
                            ['nota-baixa-deterioracao', 'Deterioração'],
                            ['nota-baixa-extravio', 'Extravio'],
                            ['nota-baixa-inservibilidade', 'Inservibilidade'],
                            ['nota-baixa-sinistro', 'Sinistro'],
                            ['nota-mudanca-classificacao', 'Mudança de Classificação']
                        ]
                    },
                    {
                        xtype: 'checkbox',
                        name: 'gerencial',
                        checked: false,
                        inputValue: '1',
                        boxLabel: 'Relatório Gerencial (Não consolidado)',
                        hidden: true
                    },
                    {
                        xtype: 'panel',
                        layout: 'hbox',
                        items: [
                            {
                                xtype: 'panel',
                                layout: 'form',
                                flex: 1.0,
                                labelWidth: 45,
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
                width: 350
            }
        );

        Ext.apply(
            cfg,
            {

            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.reports.SinteticoBaixadoWindow.superclass.constructor.call(this, cfg);
    }
});
