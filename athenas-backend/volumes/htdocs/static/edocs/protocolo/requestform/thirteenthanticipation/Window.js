Ext._define('edocs.protocolo.requestform.thirteenthanticipation.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormThirteenthAnticipation',

    rest: 'edocs.protocolo.requestform.thirteenthanticipation.Restful',

    width: 900,

    getOptionTermField: function (cfg) {
        if (this._optionTermField) {
            return this._optionTermField;
        }

        this._optionTermField = Ext._create('standard.fields.ChoiceField', {
            fieldLabel: 'Termo de opção',
            editable: false,
            hiddenName: 'option_term',
            anchor: '99%',
            choiceId: 'requestform.THIRTEENTHANTICIPATION_OPTION_TERM',
            allowBlank: false
        });

        return this._optionTermField;
    },

    getMainPanel: function (cfg) {
        if (this._mainPanel) {
            return this._mainPanel;
        }

        this._mainPanel = Ext._create('Ext.Panel', {
            frame: true,
            layout: 'form',
            items: [
                this.getCodeField(cfg),
                {
                    xtype: 'container',
                    layout: 'hbox',
                    items: [
                        {
                            xtype: 'container',
                            layout: 'form',
                            flex: 2.75,
                            items: this.getHomeCourtField(cfg)
                        },
                        {
                            xtype: 'container',
                            layout: 'form',
                            flex: 1.25,
                            labelWidth: 50,
                            items: this.getDocumentTypeField('REQUERIMENTO')  // mixin
                        }
                    ]
                },
                this.getSubjectField(cfg, {
                    value: 'Requerimento de Antecipação de 13º Salário em ' +
                           'Folha Complementar no Mês de Maio – Ato PGJ ' +
                           'nº 026/2022',
                    readOnly: true,
                }),
                this.getControlContainer(cfg),
                this.getContactNumberField(cfg),
                this.getOptionTermField(cfg),
            ]
        });

        return this._mainPanel;
    },

    getFormPanel: function (cfg) {
        if (this._formPanel) {
            return this._formPanel;
        }

        this._formPanel = Ext._create('Ext.form.FormPanel', {
            border: false,
            height: 'auto',
            autoHeight: true,
            items: this.getMainPanel(cfg)
        });

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento de Antecipação de 13º Salário - Maio/2022',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.thirteenthanticipation.Window',
    specialType: 'thirteenthanticipation',
    group: 'Auxílios, indenizações, vales e valores a receber e a antecipar'
});
