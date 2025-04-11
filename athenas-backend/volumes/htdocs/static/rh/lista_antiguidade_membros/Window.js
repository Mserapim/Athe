Ext._define('rh.lista_antiguidade_membros.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.lista_antiguidade_membros.Restful',

    width: 900,

    constructor: function(cfg) {
        rh.lista_antiguidade_membros.Window.superclass.constructor.call(this, cfg);
    },

    getFormPanel: function(cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: "textfield",
                        fieldLabel: "Ordem Antiguidade",
                        name: "ordem_antiguidade",
                        disabled: true,
                    },
                    {
                        xtype: "numberfield",
                        fieldLabel: "Matrícula Funcional",
                        name: "matricula",
                        disabled: true,
                    },
                    {
                        xtype: "textfield",
                        fieldLabel: "Nome",
                        name: "nome",
                        disabled: true,
                    },
                    {
                        xtype: "textfield",
                        fieldLabel: "Tipo Membro",
                        name: "tipo_cargo",
                        disabled: true,
                    },
                    {
                        xtype: "datefield",
                        fieldLabel: "Início na Instância",
                        name: "data_inicio_instancia",
                        disabled: true,
                    },
                    {
                        xtype: "datefield",
                        fieldLabel: "Início na Carreira",
                        name: "data_inicio_carreira",
                        disabled: true,
                    },
                    {
                        xtype: "textfield",
                        fieldLabel: "Tempo de Afastamento",
                        name: "tempo_afastamento_formatado",
                        disabled: true,
                    },
                    {
                        xtype: "textfield",
                        fieldLabel: "Tempo Total na Instância - Critério Principal",
                        name: "total_instancia_formatado",
                        disabled: true,
                    },
                    {
                        xtype: "textfield",
                        fieldLabel: "Tempo de Efetivo Exercício - 1º critério de desempate",
                        name: "efetivo_exercicio_formatado",
                        disabled: true,
                    },
                    {
                        xtype: "textfield",
                        fieldLabel: "Tempo Total de Carreira - 2º critério de desempate",
                        name: "total_carreira_formatado",
                        disabled: true,
                    },
                    {
                        xtype: "textfield",
                        fieldLabel: "Ordem de Convocação no Concurso",
                        name: "posicao_concurso",
                        disabled: true,
                    },
                    {
                        xtype: "textfield",
                        fieldLabel: "Origem da Atualização",
                        name: "origem",
                        disabled: true,
                    },
                    {
                        xtype: "datefield",
                        fieldLabel: "Processado em",
                        name: "modified_at",
                        disabled: true,
                    }

                ]
            });

        return this._formPanel;
    }


});

