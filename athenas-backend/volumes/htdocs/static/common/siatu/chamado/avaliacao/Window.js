/**
 *
 **/
Ext._define('common.siatu.chamado.avaliacao.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.chamado.avaliacao.Restful',

    width: 430,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 100,
                labelAlign: 'top',
                items: [
                    {
                        xtype: 'fieldset',
                        title: '<p> <font color="red"> <font size="1px">Atenção! Esta é uma avaliação de forma geral do atendimento do técnico com referência ao seu problema, lembrando que ele não é responsável por problemas como: falta de equipamentos, pessoal entre outros. Reclamações e/ou sugestões podem ser enviadas via documentos oficiais ou por e-mail para o setor. </font></p>',
                        // title: '<font color="red"> Atenção </font>',
                        layout: 'form',
                        // height: 10,
                        id: 'info_fieldset',
                    },
                    {
                        xtype: 'textarea',
                        width: 400,
                        height: 100,
                        name: 'relatorio',
                        fieldLabel: 'Relatório',
                        disabled: true,
                        value: this.relatorio_display
                    },
                    {
                        xtype:'radiogroup',
                        fieldLabel: 'Qual sua avaliação para a presteza do atendimento?',
                        columns: 5,
                        items: [
                            {
                                xtype:'radio',
                                inputValue: 2,
                                boxLabel: 'Ruim',
                                checked: false,
                                name: 'presteza'
                            },
                            {
                                xtype:'radio',
                                inputValue: 3,
                                boxLabel: 'Regular',
                                checked: false,
                                name: 'presteza'
                            },
                            {
                                xtype:'radio',
                                inputValue: 4,
                                boxLabel: 'Bom',
                                checked: false,
                                name: 'presteza'
                            },
                            {
                                xtype:'radio',
                                inputValue: 5,
                                boxLabel: 'Ótimo',
                                checked: false,
                                name: 'presteza'
                            },
                        ]
                    },
                    {
                        xtype:'radiogroup',
                        fieldLabel: 'Qual sua avaliação para a explicação do técnico para resolver o problema?',
                        columns: 5,
                        items: [
                            {
                                xtype:'radio',
                                inputValue: 2,
                                boxLabel: 'Ruim',
                                checked: false,
                                name: 'esclarecimento'
                            },
                            {
                                xtype:'radio',
                                inputValue: 3,
                                boxLabel: 'Regular',
                                checked: false,
                                name: 'esclarecimento'
                            },
                            {
                                xtype:'radio',
                                inputValue: 4,
                                boxLabel: 'Bom',
                                checked: false,
                                name: 'esclarecimento'
                            },
                            {
                                xtype:'radio',
                                inputValue: 5,
                                boxLabel: 'Ótimo',
                                checked: false,
                                name: 'esclarecimento'
                            },
                        ]
                    },
                    {
                        xtype:'radiogroup',
                        fieldLabel: 'Qual sua avaliação quanto ao tempo em que o técnico iniciou o atendimento até a sua conclusão?',
                        columns: 5,
                        items: [
                            {
                                xtype:'radio',
                                inputValue: 2,
                                boxLabel: 'Ruim',
                                checked: false,
                                name: 'tempo'
                            },
                            {
                                xtype:'radio',
                                inputValue: 3,
                                boxLabel: 'Regular',
                                checked: false,
                                name: 'tempo'
                            },
                            {
                                xtype:'radio',
                                inputValue: 4,
                                boxLabel: 'Bom',
                                checked: false,
                                name: 'tempo'
                            },
                            {
                                xtype:'radio',
                                inputValue: 5,
                                boxLabel: 'Ótimo',
                                checked: false,
                                name: 'tempo'
                            },
                        ]
                    },
                    {
                        xtype:'radiogroup',
                        fieldLabel: 'Qual sua avaliação do técnico sobre este atendimento, não levando em consideração o tempo que você ficou esperando pra ser atendido',
                        columns: 5,
                        items: [
                            {
                                xtype:'radio',
                                inputValue: 1,
                                boxLabel: 'Péssimo',
                                checked: false,
                                name: 'satisfacao'
                            },
                            {
                                xtype:'radio',
                                inputValue: 2,
                                boxLabel: 'Ruim',
                                checked: false,
                                name: 'satisfacao'
                            },
                            {
                                xtype:'radio',
                                inputValue: 3,
                                boxLabel: 'Regular',
                                checked: false,
                                name: 'satisfacao'
                            },
                            {
                                xtype:'radio',
                                inputValue: 4,
                                boxLabel: 'Bom',
                                checked: false,
                                name: 'satisfacao'
                            },
                            {
                                xtype:'radio',
                                inputValue: 5,
                                boxLabel: 'Ótimo',
                                checked: false,
                                name: 'satisfacao'
                            },
                        ]
                    },
                    {
                        xtype: 'textarea',
                        name: 'sugestao',
                        width: 400,
                        fieldLabel: 'Comentários e sugestões de melhoria',
                        allowBlank: true,
                    },
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.apply(
            cfg,
            {
                disableSaveAndNew: true,
            }
        );
        console.log(cfg);
        this.relatorio_display = cfg.relatorio_display;
        common.siatu.chamado.avaliacao.Window.superclass.constructor.call(this, cfg);
    }
});
