/**
 *
 **/
Ext._define('adm.patrimonio.entrada.ItemEntradaWindow', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.entrada.ItemEntradaRestful',

    width: 650,

    getValorTotalField: function() {
        if(!this._valorTotalField)
            this._valorTotalField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Total',
                name: 'valor_total',
                width: 85,
                readOnly: true,
                submitValue: false,
                decimalPrecision: 2
            });

        return this._valorTotalField;
    },

    calculateTotal: function() {
        var values = this.getFormPanel().getForm().getValues();
        var qnt = eval(values.quantidade);
        var valor_unitario = eval(values.valor_unitario);

        if(!isNaN(qnt) && !isNaN(valor_unitario))
            this.getValorTotalField().setValue(qnt * valor_unitario);
        else
            this.getValorTotalField().setValue(0.00);
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Especie',
                        name: 'especie',
                        rest: 'adm.patrimonio.parametro.EspecieRestful',
                        // width: 295
                    },
                    {
                        xtype: 'panel',
                        layout: 'hbox',
                        items: [
                            {
                                xtype: 'panel',
                                layout: 'form',
                                items: [
                                    {
                                        fieldLabel: 'Conservação',
                                        hiddenName: 'conservacao',
                                        xtype: 'combo',
                                        store: [
                                            [1, 'Novo'],
                                            [2, 'Bom'],
                                            [3, 'Regular'],
                                            [4, 'Inservivel'],
                                        ],
                                        value: 1,
                                        lazyRender: true,
                                        typeAhead: true,
                                        width: 100,
                                        mode: 'local',
                                        displayField: 'titulo',
                                        valueField: 'pk',
                                        triggerAction: 'all'
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        fieldLabel: 'Descrição',
                        xtype: 'ckeditor',
                        height: 150,
                        name: 'descricao'
                    },
                    {
                        xtype: 'panel',
                        layout: 'hbox',
                        items: [
                            {
                                xtype: 'panel',
                                width: 215,
                                layout: 'form',
                                items: [
                                    {
                                        fieldLabel: 'Quantidade',
                                        name: 'quantidade',
                                        xtype: 'numberfield',
                                        width: 85,
                                        decimalPrecision: 0,
                                        listeners: {
                                            scope: this,
                                            change: this.calculateTotal
                                        }
                                    }
                                ]
                            },
                            {
                                xtype: 'panel',
                                width: 215,
                                layout: 'form',
                                items: [
                                    {
                                        fieldLabel: 'Valor Unitário',
                                        name: 'valor_unitario',
                                        xtype: 'numberfield',
                                        width: 85,
                                        decimalPrecision: 2,
                                        listeners: {
                                            scope: this,
                                            change: this.calculateTotal
                                        }
                                    }
                                ]
                            },
                            {
                                xtype: 'panel',
                                width: 215,
                                layout: 'form',
                                items: this.getValorTotalField()
                            }
                        ]
                    },
                    {
                        fieldLabel: 'Garantia (Meses)',
                        xtype: 'numberfield',
                        width: 85,
                        name: 'meses_garantia'
                    },
                ]
            });

        return this._formPanel;
    }
});
