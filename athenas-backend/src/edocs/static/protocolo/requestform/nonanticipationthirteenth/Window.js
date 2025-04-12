Ext._define('edocs.protocolo.requestform.nonanticipationthirteenth.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestFormNonAnticipationThirteenth',

    rest: 'edocs.protocolo.requestform.nonanticipationthirteenth.Restful',

    width: 900,

    getMainPanel: function (cfg) {
        if (!this._mainPanel) {
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
                        value: 'Requerimento de Não Recebimento da Antecipação de 50% do 13º Salário no Mês do Aniversário - Art. nº 3º do Ato 004/2020',
                        readOnly: true,
                    }),
                    this.getControlContainer(cfg),
                    this.getContactNumberField(cfg)
                ]
            });
        }

        return this._mainPanel;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                height: 'auto',
                autoHeight: true,
                items: this.getMainPanel(cfg)
            });
        }

        return this._formPanel;
    }
});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento de Não Recebimento da Antecipação de 50% do 13º Salário',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.nonanticipationthirteenth.Window',
    specialType: 'nonanticipationthirteenth',
    group: 'Auxílios, indenizações, vales e valores a receber e a antecipar'
});
